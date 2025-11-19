#!/usr/bin/env -S python3 -u
from antithesis.assertions import (
    always,
    sometimes,
)

# Antithesis SDK
from antithesis.random import (
    random_choice,
    get_random,
)


import pydgraph
import json

import time
import sys

import string

import os
import mmap, struct, fcntl

def generate_range(max,min):
    return (get_random() % (max- min)) + min

def generate_random_string():
    random_str = []
    for _ in range(8):
        random_str.append(random_choice(list(string.ascii_letters + string.digits)))
    return "".join(random_str)

#keep track of (potentially) successful transactions
def increment_counter(COUNTER_FILE,inc = 1):
    if inc == 0:
        return
    with open(COUNTER_FILE, "r+b") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        with mmap.mmap(f.fileno(), 8) as mm:
            
            val = struct.unpack("q", mm[:8])[0]
            val += inc
            mm[:8] = struct.pack("q", val)
            mm.flush()
            
        fcntl.flock(f, fcntl.LOCK_UN)

def check_if_ring(links_copy):
    for l in links_copy:
        #traverse links
        original_node = l[0]
        node_next = l[1]
        for l_index in range(len(links_copy) - 1):
            idx_of = next(i for i, (first, _) in enumerate(links_copy) if first == node_next)
            node_next = links_copy[idx_of][1]
        if original_node != node_next:
            return False
    return True

#test out changes, double check that they dont break the ring
def local_modify(links,dels,makes):
    links_copy = list(links)
    if not check_if_ring(links_copy):
        return "Original Ring Broken",links_copy 

    for d in dels:
        parts = d.split(" ")
        prev_uid = parts[0].strip("<>")
        next_uid = parts[2].strip("<>")
        if ((prev_uid, next_uid) in links_copy):
            links_copy.remove((prev_uid, next_uid))
    for m in makes:
        parts = m.split(" ")
        prev_uid = parts[0].strip("<>")
        next_uid = parts[2].strip("<>")
        links_copy.append((prev_uid, next_uid))

    #check to make sure its still a ring
    if len(links_copy) != len(links):
        return "Txn duped links",links_copy
    if not check_if_ring(links_copy):
        return "Txn Broke Ring",links_copy 
    
    return "Clean Swap",links_copy

#dot visualization
def links_to_dot(links):
    out_msg = ""
    for l in links:
        l1 = l[0][2:]
        l2 = l[1][2:]
        out_msg = out_msg + l1 + "->" + l2 + ";"
    return out_msg

def swap_triplets_atomic(client: pydgraph.DgraphClient, index0: int, index1: int, num_nodes: int):
    assert index0 != index1, "Indices must be different"
    assert num_nodes >= 3, "Ring must have at least 3 nodes"

    MAX_RETRIES = 30

    for attempt in range(MAX_RETRIES):
        txn = client.txn(read_only=False)
        try:
            #construct a query and get all relationships of form
            #X1 -> X2 -> X3
            query = f"""
            {{
              nodes(func: type(Node), first: {num_nodes}) {{
                uid
                name
                counter
                friend {{
                  uid
                  name
                  counter
                  friend {{
                    uid
                    name
                    counter
                  }}
                }}
              }}
            }}
            """
            res = txn.query(query)
            data = json.loads(res.json)


            #parse triplets to links
            triplets = []
            for node in data["nodes"]:
                curr = node
                if not curr.get("friend") or not curr["friend"][0].get("friend"):
                    continue  # incomplete triplet
                prev = None
                next_node = curr["friend"][0]#["friend"][0]
                for candidate in data["nodes"]:
                    if candidate.get("friend") and candidate["friend"][0]["uid"] == curr["uid"]:
                        prev = candidate
                        break
                if prev:
                    triplets.append({
                        "prev": prev,
                        "curr": curr,
                        "next": next_node
                    })
            links = set()
            for i in range(len(triplets)):
                links.add((triplets[i]['prev']['uid'],triplets[i]['curr']['uid']))
                links.add((triplets[i]['curr']['uid'],triplets[i]['next']['uid']))

            always(check_if_ring(list(links)), "Ring held before commit", {"links":links_to_dot(links)})

            if index0 >= len(triplets) or index1 >= len(triplets):
                print("Triplet indices",len(triplets),num_nodes)
                for i in range(len(triplets)):
                    print(triplets[i]['prev']['uid'],triplets[i]['curr']['uid'],triplets[i]['next']['uid'])
                raise IndexError("Triplet index out of bounds")
            
            #pick 2 random ones from the list (provided extrnally by index0 and index1)
            #a1 -r1> a2 -r2> a3
            #b1 -r3> b2 -r4> b3
            t1 = triplets[index0]
            t2 = triplets[index1]

            
            a1, a2, a3 = t1["prev"], t1["curr"], t1["next"]
            b1, b2, b3 = t2["prev"], t2["curr"], t2["next"]

            
            def uid(n): return n["uid"]

            # handle swapping adjacent nodes
            # X -> Y -> Z -> W
            # Case 1: Swapping Y and Z
            # X -> Z -> Y -> W
            # y1 y2 y3
            #    z1 z2 z3 
            # thus: Y3 = Z2 and Y2 = Z1
            # redudant deletes are no-ops
            # normal creation will make
            # Y1 -> Z2, Z2 -> Y3, Z1 -> Y2, Y2 -> Z3
            # which in this case makes:
            # X -> Z -> Z
            # Y -> Y -> W
            # If we set Y3_hat to Y2 and Z1_hat to Z2
            # we instead make:
            # X -> Z , Z -> Y , Z -> Y , Y -> W
            # filtering out duplicate relationships (with a set) yields:
            # X -> Z -> Y -> W

            # Case 2: Swapping Z and Y
            # X -> Z -> Y -> W
            #    z1 z2 z3
            # y1 y2 y3 
            # thus: Z1 = Y2 and Z2 = Y3
            # redudant deletes are no-ops
            # normal creation will make
            # Z1 -> Y2, Y2 -> Z3, Y1 -> Z2, Z2 -> Y3
            # which in this case makes:
            # Y -> Y -> W
            # X -> Z -> Z
            # If we set Z1_hat to Z2 and Y3_hat to Y2
            # we instead make:
            # Z -> Y , Y -> W , X -> Z , Z -> Y
            # filtering out duplicate relationships (with a set) yields:
            # X -> Z -> Y -> W

            #Why make it so complicated? Why not just use an if statement with a different codepath?
            #Because this works on GraphQL without interleaved python (Like Neo4J's cypher)

            a1_hat = a2 if uid(a1) == uid(b2) else a1
            b3_hat = b2 if uid(a2) == uid(b3) else b3
            a3_hat = a2 if uid(a3) == uid(b2) else a3
            b1_hat = b2 if uid(a2) == uid(b1) else b1

            
            touched = {uid(n): n for n in [a1_hat, b2, a3_hat, b1_hat, a2, b3_hat]}
            
            del_lines = []
            set_lines = []

            # Delete r1, r2 , r3, r4
            del_lines.append(f"<{uid(a1)}> <friend> <{uid(a2)}> .")
            del_lines.append(f"<{uid(a2)}> <friend> <{uid(a3)}> .")
            del_lines.append(f"<{uid(b1)}> <friend> <{uid(b2)}> .")
            del_lines.append(f"<{uid(b2)}> <friend> <{uid(b3)}> .")

            #create new relationships
            # a1 -r5> b2 -r6> a3
            # b1 -r7> a2 -r8> b3
            # Prevent duplicate relationships with a set
            # Other GraphQL can use merge or upsert
            set_of_nquads = set()

            set_lines.append(f"<{uid(a1_hat)}> <friend> <{uid(b2)}> .")
            set_of_nquads.add(f"<{uid(a1_hat)}> <friend> <{uid(b2)}> .")

            if not f"<{uid(b2)}> <friend> <{uid(a3_hat)}> ." in set_of_nquads:
                set_lines.append(f"<{uid(b2)}> <friend> <{uid(a3_hat)}> .")
                set_of_nquads.add(f"<{uid(b2)}> <friend> <{uid(a3_hat)}> .")
            if not f"<{uid(b1_hat)}> <friend> <{uid(a2)}> ." in set_of_nquads:
                set_lines.append(f"<{uid(b1_hat)}> <friend> <{uid(a2)}> .")
                set_of_nquads.add(f"<{uid(b1_hat)}> <friend> <{uid(a2)}> .")
            if not f"<{uid(a2)}> <friend> <{uid(b3_hat)}> ." in set_of_nquads:
                set_lines.append(f"<{uid(a2)}> <friend> <{uid(b3_hat)}> .")
                set_of_nquads.add(f"<{uid(a2)}> <friend> <{uid(b3_hat)}> .")

            set_lines_make = set_lines.copy()
            # Increment counters
            for node_uid, node in touched.items():
                current = node.get("counter", 0)
                new_val = current + 1
                set_lines.append(f'<{node_uid}> <counter> "{new_val}" .')
            

            del_lines_prejoin = del_lines.copy()
            del_lines = "\n".join(del_lines)
            set_lines = "\n".join(set_lines)
            txn.mutate(del_nquads = del_lines)
            txn.mutate(set_nquads=set_lines)
            txn.commit()

            mod_msg,local_links = local_modify(links,del_lines_prejoin,set_lines_make)
            print("START: " + links_to_dot(links) + "\n" + "DEL: " + str(del_lines_prejoin) + "\n" + "MAKE: " + str(set_lines_make) + "\n" + mod_msg + ": " + links_to_dot(local_links) + "\n")

            # return names of counters, for increment
            return [node.get("name") for node in touched.values()]

        except pydgraph.AbortedError:
            txn.discard()
            time.sleep(1)
            continue
        except Exception as e:
            txn.discard()
            raise e
        finally:
            txn.discard()

    raise RuntimeError("Failed to commit after retries")

def simulate_transactions():
  
    with open("node_count", 'r') as f:
        num_nodes = int(f.read())
    
    client_stub1 = pydgraph.DgraphClientStub('10.0.0.25:9080')
    client_stub2 = pydgraph.DgraphClientStub('10.0.0.30:9081')
    client_stub3 = pydgraph.DgraphClientStub('10.0.0.35:9082')
    client = pydgraph.DgraphClient(client_stub1,client_stub2,client_stub3)

    max_swaps = int(os.environ.get('NUM_SWAPS_MAX', 35))

    min_swaps = int(os.environ.get('NUM_SWAPS_MIN', 20))

    num_swaps = generate_range(max_swaps,min_swaps)

    counter_dict = {str(i): 0 for i in range(num_nodes)}

    for s in range(num_swaps):
        #sample i0 and i1 without replacement
        index0 = generate_range(num_nodes,0)
        i1_list = list(range(num_nodes))
        i1_list.remove(index0)
        index1 = random_choice(i1_list)
        
        node_touched_names = swap_triplets_atomic(client,index0,index1,num_nodes)

        #update the counters, without blocking
        for n in node_touched_names:
            counter_dict[n] = counter_dict[n] + 1
            


    for n in counter_dict:
        increment_counter("/tmp/shared_counter_" + n + ".bin",inc = counter_dict[n])
    
    client_stub1.close()
    client_stub2.close()
    client_stub3.close()


    
if __name__ == "__main__":
    simulate_transactions()
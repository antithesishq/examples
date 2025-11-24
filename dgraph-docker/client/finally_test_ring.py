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

import os,mmap, struct, fcntl


def generate_range(max,min):
    return (get_random() % (max- min)) + min

def generate_random_string():
    random_str = []
    for _ in range(8):
        random_str.append(random_choice(list(string.ascii_letters + string.digits)))
    return "".join(random_str)

MAX_RETRIES = 10
RETRY_DELAY = 4  # seconds, base delay for exponential backoff



def get_counter(COUNTER_FILE):
    try:
        with open(COUNTER_FILE, "r+b") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            with mmap.mmap(f.fileno(), 8) as mm:
                
                val = struct.unpack("q", mm[:8])[0]
                fcntl.flock(f, fcntl.LOCK_UN)
                return val
    except FileNotFoundError:
        return 0

def is_ring(txn, start_name: str, num_nodes: int) -> bool:
    #get the ring recursively, friend has its own uid, name and friend field
    query = f"""
    {{
      ring(func: eq(name, "{start_name}")) @recurse(depth: {int(num_nodes + 1)}, loop: true) {{
        uid
        name
        friend
      }}
    }}
    """

   
 
    res = txn.query(query)
    data = json.loads(res.json)
    nodes = data.get("ring", [])
    print(nodes)
    if not nodes:
        return False, "No nodes"

    uid_to_node = {n["uid"]: n for n in nodes}
    visited = []
    visited_set = set()

    # Start at the root
    current = nodes[0]
    start_uid = current["uid"]

    for _ in range(num_nodes - 1):
        if current["uid"] in visited_set:
            return False,"Visted Twice"
        visited.append(current["uid"])
        visited_set.add(current["uid"])

        # follow the first friend
        friends = current.get("friend", [])
        if not friends:
            return False,"Terminal Node"  # chain broken

        current = friends[0]

    # After N steps, the next friend should loop back to the start
    friends = current.get("friend", [])
    if not friends:
        return False, "Terminal Node"

    #loops back ot original node, path walks exactly n nodes
    rvalue = friends[0]["uid"] == start_uid and len(visited_set) == num_nodes - 1
    msg = "successful"
    if not rvalue:
        msg = "Didn't loop back"
    return rvalue, msg 


def get_node_counters(txn):
    query = """
    {
        nodes(func: type(Node)) {
            name
            counter
        }
    }
    """

    res = txn.query(query)
    data = json.loads(res.json)

    nodes = data.get("nodes", [])
    print(nodes)

    name_counter_dict = {
        node["name"]: node.get("counter", 0)
        for node in nodes
        if "name" in node
    }

    return name_counter_dict

def check_ring():

    with open("node_count", 'r') as f:
        num_nodes = int(f.read())
    

    client_stub1 = pydgraph.DgraphClientStub('10.0.0.25:9080')
    client_stub2 = pydgraph.DgraphClientStub('10.0.0.30:9081')
    client_stub3 = pydgraph.DgraphClientStub('10.0.0.35:9082')
    client = pydgraph.DgraphClient(client_stub1,client_stub2,client_stub3)

    #check num_nodes = total_num nodes
    #check that N steps makes you end up where you started
    #check that the list of distinct visitors in the traversal is equal to num_nodes

    for i in range(num_nodes):
        txn = client.txn(read_only=True)
        ok,msg = is_ring(txn, start_name=str(i), num_nodes=num_nodes)
        txn.discard()
        if not ok:
            return False,msg
        


    txn = client.txn(read_only=True)
    name_counter_dict = get_node_counters(txn)
    txn.discard()

    for i in range(num_nodes):
        node_str = str(i)
        ctr = get_counter("/tmp/shared_counter_" + node_str + ".bin")
        invariant = ctr <= name_counter_dict[node_str]
        if (not invariant):
            print(f"Counter mismatch Expected: {ctr} Actual: {name_counter_dict[node_str]}")
        always(invariant, "Ring durability counter correct", {"expected":str(ctr),"actual": str(name_counter_dict[node_str])})

    print("Ring is intact.")

    client_stub1.close()
    client_stub2.close()
    client_stub3.close()
    return True, "successful"


if __name__ == "__main__":
    time.sleep(30)
    continuity,msg = check_ring()

    always(continuity, "Ring continuity maintained", {"cause":msg})


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


def generate_range(max,min):
    return (get_random() % (max- min)) + min

def generate_random_string():
    random_str = []
    for _ in range(8):
        random_str.append(random_choice(list(string.ascii_letters + string.digits)))
    return "".join(random_str)



def upsert_graph_data(client, graph_data):
    for row in graph_data:
    
        try:
            txn = client.txn()
            name = row["name"]
            friend = row["friend"]

            upsert_query = f"""
            query {{
            a as var(func: eq(name, "{name}"))
            b as var(func: eq(name, "{friend}"))
            }}
            """

            # Create <a> -> <b>
            nquads = f"""
            uid(a) <name> "{name}" .
            uid(a) <counter> "0" .
            uid(a) <dgraph.type> "Node" .
            uid(b) <name> "{friend}" .
            uid(b) <counter> "0" .
            uid(b) <dgraph.type> "Node" .
            uid(a) <friend> uid(b) .
            """

            mutation = pydgraph.Mutation(set_nquads=nquads.encode("utf-8"))
            req = pydgraph.Request(
                query=upsert_query,
                mutations=[mutation],
                commit_now=True  # We'll commit at the end
            )
            txn.do_request(req)

            #txn.commit()
        finally:
            txn.discard()


if __name__ == "__main__":
    num_verts = generate_range(10,4)
    num_edges = num_verts
    vert_names = []
    for i in range(num_verts):
        vert_names.append(str(i))

    with open("node_count", 'w') as f:
        f.write(f"{num_verts}")

    #(a,b,relation)
    graph_edges = []
    #generate ring graph
    for i in range(num_edges):
        a = str(i)
        b = str(i + 1)
        if i == num_edges - 1 :
            b = str(0)
        graph_edges.append((a,b))

    graph_data = []
    for ed in graph_edges:
        graph_data.append({"name" : ed[0], "friend" : ed[1] })

    client_stub1 = pydgraph.DgraphClientStub('10.0.0.25:9080')
    client_stub2 = pydgraph.DgraphClientStub('10.0.0.30:9081')
    client_stub3 = pydgraph.DgraphClientStub('10.0.0.35:9082')
    client = pydgraph.DgraphClient(client_stub1,client_stub2,client_stub3)

    # <a> -[friend]> <b.
    schema = """
    name: string @index(exact) @upsert .
    counter: int .
    friend: [uid] .
    """

    # set schema
    operation = pydgraph.Operation(schema=schema)
    client.alter(operation)

    upsert_graph_data(client,graph_data)

    client_stub1.close()
    client_stub2.close()
    client_stub3.close()
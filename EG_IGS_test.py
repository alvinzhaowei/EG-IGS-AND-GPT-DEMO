import pickle
import random
import numpy as np
import utility
import TS_IGS
import networkx as nx

# dataset name
dataset = "ImageNet"
# tau
tau = 0.6
d_t = 1 - tau
# maximum size of matched entities
k = 20

# entity index for distance matrix
index = pickle.load(open("./data/" + dataset + "/" + dataset + "_entity_index", "rb"))
# distance matrix
distances = np.load("./data/" + dataset + "/" + dataset + "_distances.npy")
# hierarchy
H = pickle.load(open("./data/" + dataset + "/" + dataset + "_hierarchy", "rb"))
root = H.root
# path tree for IGS algorithm
Pi = pickle.load(open("./data/" + dataset + "/" + dataset + "_path_tree", "rb"))
# entity for testing
testing = pickle.load(open("./data/" + dataset + "/" + dataset + "_Id_t", "rb"))
# example_entities
example_entities = {}
testing_order = list(testing.keys())
random.shuffle(testing_order)

results = []

print("total query:", len(testing_order))
queried = 0
for entity_Id in testing_order:
    if (queried + 1) % 100 == 0:
        print(queried + 1, "queries has finished")
    t = testing[entity_Id]
    i = index[entity_Id]
    matched_entities = []
    q_count = 0
    for ex_Id in example_entities:
        d = distances[i][index[ex_Id]]
        if d < d_t:
            matched_entities.append((ex_Id, d))

    if len(matched_entities) == 0:
        q_count = TS_IGS.query(Pi, H, t, root, set())
        results.append(q_count)
        example_entities[entity_Id] = t
        queried += 1
        continue

    # takes only the top k
    if len(matched_entities) > k:
        matched_entities = sorted(matched_entities, key=lambda x: x[1])[:k]

    # calculate weights
    F = dict()

    # compute a promising tree
    OPT = nx.DiGraph()
    for matched_en_Id, d in matched_entities:
        HQ = set()
        t_ = example_entities[matched_en_Id]
        node = t_
        parent = H.parent(node)
        HQ.add(node)
        while parent is not None:
            parent = parent.identifier
            OPT.add_edge(parent, node)
            node = parent
            HQ.add(node)
            parent = H.parent(node)
        for q in HQ:
            if q not in F:
                F[q] = 1 - d
            else:
                F[q] += 1 - d

    # only the root node
    if len(F) == 1:
        qc = TS_IGS.query(Pi, H, t, root, set())
        q_count += qc
        results.append(q_count)
        example_entities[entity_Id] = t
        queried += 1

    # compress the promising tree
    CPT = nx.DiGraph()
    ln = utility.compress_promising_tree(OPT, root, CPT)
    nr = None
    # one single path will become an empty graph
    if len(CPT) == 0:
        CPT.add_node(ln)
        nr = ln
    else:
        # locate the new root
        for node in CPT.nodes():
            if len(CPT.pred[node]) == 0:
                nr = node
                break
    found = False
    pruned = set()

    # search on the compressed promising tree
    q = nr
    flag = utility.reach(H, q, t)
    q_count += 1
    if flag == 0:
        pruned.union(set(H.subtree(q).all_nodes()))
    while flag == 1:
        C = list(CPT.succ[q])
        if len(C) == 0:
            break
        else:
            all_zeros = True
            C = sorted(C, key=lambda x: F[x], reverse=True)
            for c in C:
                flag = utility.reach(H, c, t)
                q_count += 1
                if flag == 1:
                    q = c
                    all_zeros = False
                    break
                else:
                    pruned.union(set(H.subtree(c).all_nodes()))
            if all_zeros:
                break

    # if q is not a leaf node in the promising tree
    if len(CPT.succ[q]) > 0:
        qc, q = utility.deepest_yes(H, OPT, q, t, pruned)
        q_count += qc

    # continue searching from the deepest yes concept excluding the pruned nodes
    qc = TS_IGS.query(Pi, H, t, q, pruned)
    q_count += qc

    results.append(q_count)
    example_entities[entity_Id] = t
    queried += 1
print("Average cost:", sum(results) / len(results))
# pickle.dump(results, open("./data/" + dataset + "/" + dataset + "EG_IGS_result", "wb"))

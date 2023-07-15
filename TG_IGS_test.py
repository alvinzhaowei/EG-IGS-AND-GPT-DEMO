import pickle
import random
import IGS
import TS_IGS

# dataset name
dataset = "ImageNet"

# hierarchy
H = pickle.load(open("./data/" + dataset + "/" + dataset + "_hierarchy", "rb"))
root = H.root
# path tree for IGS algorithm
Pi = pickle.load(open("./data/" + dataset + "/" + dataset + "_path_tree", "rb"))
# entity for testing
testing = pickle.load(open("./data/" + dataset + "/" + dataset + "_Id_t", "rb"))

testing_order = list(testing.keys())
random.shuffle(testing_order)

results1 = []
results2 = []

print("total query:", len(testing_order))
queried = 0
for entity_Id in testing_order:
    if (queried + 1) % 100 == 0:
        print(queried + 1, "queries has finished")
    t = testing[entity_Id]
    cost1 = IGS.query(Pi, H, t, root, set())
    cost2 = TS_IGS.query(Pi, H, t, root, set())
    results1.append(cost1)
    results2.append(cost2)
    queried += 1
print("IGS average cost:", sum(results1) / len(results1))
print("TS-IGS average cost:", sum(results2) / len(results2))

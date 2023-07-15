import treelib
import pickle

dataset = "ImageNet"
T = pickle.load(open("./data/" + dataset + "/" + dataset + "_hierarchy", "rb"))

Pi = treelib.Tree()
r = T.root
S = []
S.append(r)
pi = []
counter = 1
while len(S) > 0:
    u = S.pop()
    if len(pi) == 0:
        pi.append(u)
    if len(T.children(u)) == 0:
        if len(Pi.nodes) == 0:
            Pi.create_node(identifier=counter, data=pi)
            counter += 1
        else:
            p = T.parent(pi[0]).identifier
            P = None
            for node in Pi.all_nodes():
                if p in node.data:
                    P = node
                    break
            Pi.create_node(identifier=counter, data=pi, parent=P.identifier)
            counter += 1
        pi = []
        continue
    maxSize = 0
    heavyNode = None
    for c in T.children(u):
        size = len(T.subtree(c.identifier))
        if maxSize < size:
            maxSize = size
            heavyNode = c.identifier
    for c in T.children(u):
        if c.identifier != heavyNode:
            S.append(c.identifier)
    S.append(heavyNode)
    pi.append(heavyNode)
    # print(len(S))

# Pi.show()
pickle.dump(Pi, open("./data/" + dataset + "/" + dataset + "_path_tree", "wb"))

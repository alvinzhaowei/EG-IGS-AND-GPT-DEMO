from .utility import *

last_yes_question = None
all_messages = []

# binary search on super node
def binary_search(arr, low, high, c, T, pruned, rn_nodes, oracle, description):
    global last_yes_question
    global all_messages
    if high >= low:
        mid = (high + low) // 2
        qn = arr[mid]
        flag = None
        if qn in pruned:
            flag = 0
        else:
            if c in rn_nodes:
                flag = 1
            else:
                flag, messages = oracle.ask_question(description, qn)
                all_messages.append(messages)
            # flag = utility.reach(T, qn, t)
            if qn != "root":
                c = c + 1
        if flag == 1:
            last_yes_question = qn
            rn_nodes.add(last_yes_question)
            return binary_search(arr, mid + 1, high, c, T, pruned, rn_nodes, oracle, description)
        elif flag == 0:
            return binary_search(arr, low, mid - 1, c, T, pruned, rn_nodes, oracle, description)
        else:
            last_yes_question = qn
            return c
    else:
        return c


def query(Pi, T, r, pruned, rn_nodes, oracle, description):
    global all_messages
    all_messages = []
    q_count = 0
    pi = None
    tn = None
    for node in Pi.all_nodes():
        if r in node.data:
            pi = node.data
            break
    while True:
        if len(pi) == 1:
            q_count += 1
            rn_nodes.add(pi[0])
            tn = pi[0]
            break
        else:
            c = binary_search(pi, 0, len(pi) - 1, 0, T, pruned, rn_nodes, oracle, description)
            q_count += c
            q = last_yes_question
            tn = q
            if q is None:
                q = "root"
            # search the child has larger subtree first
            children = sorted(list(T.children(q)), key=lambda x: T.subtree(x.identifier).size(), reverse=True)
            found = True
            for child in children:
                child = child.identifier
                if child in pruned:
                    continue
                if c in rn_nodes:
                    flag = 1
                else:
                    flag, messages = oracle.ask_question(description, child)
                    all_messages.append(messages)
                # flag = utility.reach(T, child, t)
                if child != "root":
                    q_count += 1
                if flag == 1:
                    # if one of the child node is reachable, q is not the target node
                    rn_nodes.add(child)
                    tn = child
                    found = False
                    for node in Pi.all_nodes():
                        if child in node.data:
                            pi = node.data
                            break
                    break
            if found:
                break
    return q_count, tn, all_messages

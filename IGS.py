import utility

last_yes_question = None


# binary search on super node
def binary_search(arr, low, high, t, c, T, pruned):
    global last_yes_question
    if high >= low:
        mid = (high + low) // 2
        qn = arr[mid]
        flag = None
        if qn in pruned:
            flag = 0
        else:
            flag = utility.reach(T, qn, t)
            c = c + 1
        if flag == 1:
            last_yes_question = qn
            return binary_search(arr, mid + 1, high, t, c, T, pruned)
        elif flag == 0:
            return binary_search(arr, low, mid - 1, t, c, T, pruned)
    else:
        return c


def query(Pi, T, t, r, pruned):
    q_count = 0
    pi = None
    for node in Pi.all_nodes():
        if r in node.data:
            pi = node.data
            break
    while True:
        if len(pi) == 1:
            q_count += 1
            break
        else:
            c = binary_search(pi, 0, len(pi) - 1, t, 0, T, pruned)
            q_count += c
            q = last_yes_question
            # search the child has larger subtree first
            children = sorted(list(T.children(q)), key=lambda x: T.subtree(x.identifier).size(), reverse=True)
            found = True
            for child in children:
                child = child.identifier
                if child in pruned:
                    continue
                flag = utility.reach(T, child, t)
                q_count += 1
                if flag == 1:
                    # if one of the child node is reachable, q is not the target node
                    found = False
                    for node in Pi.all_nodes():
                        if child in node.data:
                            pi = node.data
                            break
                    break
            if found:
                # # q will be the target node
                # print(q)
                break
    return q_count

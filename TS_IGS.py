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


# k step search on super node
def k_step_search(arr, t, c, T, pruned):
    global last_yes_question
    arr_length = len(arr) - 1
    arr_index = 0
    qn = None
    i = 0
    flag = 1
    last_yes_question = arr[0]
    if arr_length == 0:
        return 0
    p = 1
    step = 4
    while flag == 1:
        i = i + 1
        p = p * step
        arr_index = p - 1
        if arr_index > arr_length:
            break
        qn = arr[arr_index]
        flag = utility.reach(T, qn, t)
        c = c + 1

    low = p // step
    last_yes_question = arr[low - 1]
    if arr_index > arr_length:
        high = arr_length
    else:
        high = arr_index - 1
    c = binary_search(arr, low, high, t, c, T, pruned)
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
            c = k_step_search(pi, t, 0, T, pruned)
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

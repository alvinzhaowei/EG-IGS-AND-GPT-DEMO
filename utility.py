def reach(T, q, t):
    if q == t:
        return 1
    if T.is_ancestor(q, t):
        return 1
    else:
        return 0


def compress_promising_tree(OPT, qr, CPT):
    children = OPT.succ[qr]
    if len(children) == 0:
        return qr
    elif len(children) > 1:
        for child in children:
            n_child = compress_promising_tree(OPT, child, CPT)
            CPT.add_edge(qr, n_child)
        return qr
    elif len(children) == 1:
        return compress_promising_tree(OPT, list(children).pop(), CPT)


def binary_search(arr, low, high, t, cost, T, pruned, lyq):
    if high >= low:
        mid = (high + low) // 2
        qn = arr[mid]
        flag = None
        if qn in pruned:
            flag = 0
        else:
            flag = reach(T, qn, t)
            cost = cost + 1
        if flag == 1:
            return binary_search(arr, mid + 1, high, t, cost, T, pruned, qn)
        elif flag == 0:
            return binary_search(arr, low, mid - 1, t, cost, T, pruned, lyq)
    else:
        return lyq, cost


def deepest_yes(T, TQO, q, t, pruned):
    qc = 0
    while True:
        cs = set(TQO.succ[q])
        if len(cs) == 0:
            return qc, q
        for c in cs:
            ans = reach(T, c, t)
            qc = qc + 1
            if ans == 0:
                pruned.union(set(T.subtree(c).all_nodes()))
            elif ans == 1:
                # binary search on this path
                arr = []
                node = c
                gcs = TQO.succ[node]
                while len(gcs) == 1:
                    node = list(gcs)[0]
                    arr.append(node)
                    gcs = TQO.succ[node]
                q, qc = binary_search(arr, 0, len(arr), t, qc, T, pruned, c)
        return qc, q

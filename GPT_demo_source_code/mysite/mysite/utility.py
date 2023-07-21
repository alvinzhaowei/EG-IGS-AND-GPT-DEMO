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


def deepest_yes(T, TQO, q, t, pruned, reachable_nodes):
    qc = 0
    while True:
        cs = set(TQO.succ[q])
        if len(cs) == 0:
            return qc, q
        all_zeros = True
        for c in cs:
            ans = reach(T, c, t)
            qc = qc + 1
            if ans == 0:
                pruned.union(set(T.subtree(c).all_nodes()))
            elif ans == 1:
                reachable_nodes.add(c)
                q = c
                all_zeros = False
                break
        if all_zeros:
            return qc, q


def deepest_yes_GPT(T, TQO, q, pruned, reachable_nodes, oracle, description):
    qc = 0
    tn = None
    all_messages = []
    while True:
        cs = set(TQO.succ[q])
        if len(cs) == 0:
            return qc, q, tn, all_messages
        all_zeros = True
        for c in cs:
            # ans = reach(T, c, t)
            ans, messages = oracle.ask_question(description, c)
            all_messages.append(messages)
            qc = qc + 1
            if ans == 0:
                pruned.union(set(T.subtree(c).all_nodes()))
            elif ans == 1:
                reachable_nodes.add(c)
                tn = c
                q = c
                all_zeros = False
                break
        if all_zeros:
            return qc, q, tn, all_messages

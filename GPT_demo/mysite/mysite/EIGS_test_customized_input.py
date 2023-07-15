import pickle
from .utility import *
from .IGS_method import *
import networkx as nx
from .ChatGPT_demo import ChatGPTOracle
from .item_description_crawler import DescriptionCrawler
import spacy
import warnings
import os


class EIGS_Tester:
    def __init__(self, SHOW_MESSAGE=True, WITH_PRE_MINED=True):
        warnings.filterwarnings("ignore", message=r"\[W007\]", category=UserWarning)

        # show messages and reply
        self.SHOW_MESSAGE = SHOW_MESSAGE
        # with or without pre-mined items
        self.WITH_PRE_MINED = WITH_PRE_MINED
        # initialize Chat-GPT oracle
        self.oracle = ChatGPTOracle(SHOW_MESSAGE)
        # dataset name
        dataset = "amazon"
        # hierarchy
        self.H = pickle.load(open("./data/" + dataset + "/" + dataset + "_hierarchy", "rb"))
        self.root = self.H.root
        # path tree for IGS algorithm
        self.Pi = pickle.load(open("./data/" + dataset + "/" + dataset + "_path_tree", "rb"))
        # example_entities
        if WITH_PRE_MINED:
            self.example_entities = pickle.load(open("./data/" + dataset + "/" + dataset + "_pre_mined", "rb"))
        else:
            self.example_entities = {}
        # item descriptions
        self.item_description = pickle.load(open("./data/amazon/item_description_nlp", "rb"))
        # website crawler
        self.crawler = DescriptionCrawler()
        # text similarity
        self.nlp = spacy.load('en_core_web_sm')

    def crawl_description(self,
                          url='https://www.amazon.com.au/Ikigai-Japanese-secret-long-happy/dp/178633089X/ref=sr_1_5'
                              '?keywords=book '
                              '&qid=1686272706&sr=8-5'):
        # input URL
        # url = input("Please enter the URL: ")
        self.description = self.crawler.crawl(
            url)
        if len(self.description) <= 50:
            return 0, "Sorry, failed to find the item description or item description doesn't exist"
        if self.SHOW_MESSAGE:
            return 1, self.description

    def test_EIGS(self, des):
        all_messages = []
        Pi = self.Pi
        H = self.H
        root = self.root
        oracle = self.oracle
        description = None
        if des is None:
            description = self.description
        else:
            description = des
        example_entities = self.example_entities
        # print(description)
        # tau
        tau = 0.6
        d_t = 1 - tau
        matched_entities = []
        description_nlp = self.nlp(description)
        for ex_Id in self.example_entities:
            ex_des = self.nlp(self.item_description[ex_Id])
            sc = description_nlp.similarity(ex_des)
            d = 1 - sc
            if d < d_t - 0.2:
                matched_entities.append((ex_Id, d))
        reachable_nodes = set()
        target_node = None

        q_count = 0

        if len(matched_entities) == 0:
            q_count, target_node, messages = query(Pi, H, root, set(), reachable_nodes, oracle, description)
            all_messages.extend(messages)
        else:
            # calculate weights
            F = dict()
            Q = set()

            for matched_en_Id, d in matched_entities:
                HQ = example_entities[matched_en_Id]
                for q in HQ:
                    if q not in F:
                        F[q] = 1 - d
                    else:
                        F[q] += 1 - d
                Q = Q.union(HQ)

            # compute a promising tree
            OPT = nx.DiGraph()
            for q in Q:
                p = q
                while p != root:
                    p = H.parent(p).identifier
                    if p in Q:
                        break
                if q != root:
                    OPT.add_edge(p, q)

            vr = set()
            for node in OPT.nodes():
                if len(OPT.pred[node]) == 0:
                    vr.add(node)
            qr = None
            if len(vr) > 1:
                ancestors = {}
                lca = None
                for node in vr:
                    p = node
                    while p != root:
                        p = H.parent(p).identifier
                        if p not in ancestors:
                            ancestors[p] = 1
                        else:
                            ancestors[p] += 1
                            if ancestors[p] == len(vr):
                                lca = p
                                break
                for node in vr:
                    OPT.add_edge(lca, node)
                qr = lca
            else:
                qr = vr.pop()

            # compress the promising tree
            CPT = nx.DiGraph()
            ln = compress_promising_tree(OPT, qr, CPT)
            nr = None
            # stick shape will become an empty graph
            if len(CPT) == 0:
                CPT.add_node(ln)
                nr = ln
            else:
                for node in CPT.nodes():
                    if len(CPT.pred[node]) == 0:
                        nr = node
                        break
            found = False
            pruned = set()

            q = nr
            # flag = utility.reach(H, q, t)
            if q in reachable_nodes:
                flag = 1
            else:
                flag, messages = oracle.ask_question(description, q)
                all_messages.append(messages)
            if q != "root":
                q_count += 1
            if flag == 0:
                pruned.union(set(H.subtree(q).all_nodes()))
            while flag == 1:
                reachable_nodes.add(q)
                target_node = q
                C = list(CPT.succ[q])
                if len(C) == 0:
                    break
                else:
                    all_zeros = True
                    C = sorted(C, key=lambda x: F[x], reverse=True)
                    for c in C:
                        # flag = utility.reach(H, c, t)
                        if c in reachable_nodes:
                            flag = 1
                        else:
                            flag, messages = oracle.ask_question(description, c)
                            all_messages.append(messages)
                        if q != "root":
                            q_count += 1
                        if flag == 1:
                            q = c
                            all_zeros = False
                            break
                        else:
                            pruned.union(set(H.subtree(c).all_nodes()))
                    if all_zeros:
                        break
            qc, q, target_node, messages = deepest_yes_GPT(H, OPT, q, pruned, reachable_nodes, oracle,
                                                           description)
            all_messages.extend(messages)
            q_count += qc
            if len(reachable_nodes) == 0:
                q = root
            qc, target_node, messages = query(Pi, H, q, pruned, reachable_nodes, oracle, description)
            all_messages.extend(messages)
            if len(reachable_nodes) == 0:
                target_node = root
            print(reachable_nodes)
            q_count += qc
        return all_messages, "The target node is: " + target_node + ". "

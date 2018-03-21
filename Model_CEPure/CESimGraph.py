# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nx
from cmyToolkit import *
from sxpPackage import *
from cmyConfFuncForRankModels import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CESimGraph:
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, remove_stopwords=default_remove_stopword):
        self.ceopt = ceopt
        self.cesimbias = cesim_bias
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.s = np.matrix(np.zeros(len(self.text.sentenceset))).T  # sentence weight, is a len(sentences) * 1 matrix
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*1 matrix
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.page_rank_cesim_graph(self.ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
    def page_rank_cesim_graph(self, ceopt):
        cesimgraph = self.mancesimgraph
        if ceopt == "sysce":
            cesimgraph = self.syscesimgraph
        # using pagerank to get sentence-id to sentence-weight dict from causal-similarity graph
        sid_sw_dict = nx.pagerank(cesimgraph)
        # If the graph is empty, i.e., there has no cause-effect links in this paper, do not need to rank sentences.
        if len(sid_sw_dict) == 0:
            return
        # create all sentence weight according to sid_sw_dict
        for sid, sw in sid_sw_dict.items():
            self.s[sid, 0] = sw
        # -- Delete sentences without cause-effect links from sent ranked idx --
        idx_s_inc0 = np.argsort(-self.s, axis=0)
        idx_s_inc0 = np.array(idx_s_inc0).reshape(-1,).tolist()  # The idx_s which contains 0 value sentences
        while self.s[idx_s_inc0[-1]] == 0:
            del idx_s_inc0[-1]
        self.idx_s = np.matrix(idx_s_inc0).T


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestCESimGraph():
    pk = r"E:\Programs\Eclipse\CE_relation\CEsummary_new\acl\pickle\P14-1007.xhtml_1.pickle"
    model = CESimGraph(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    for idx, sid in enumerate(model.idx_s):
        print idx, "th:", sid
    for sid, sw in enumerate(model.s):
        print sid, sw
    # for idx in range(topksent):
    #     print '----------------'
    #     print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestCESimGraph()
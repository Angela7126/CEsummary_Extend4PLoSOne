# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nx
from sxpPackage import *
from cmyToolkit import *
from cmyConfFuncForRankModels import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CEBias_SimGraph:
    # section2sentence_id_list: stores the mapping between section_title and sentences id that belong to this section
    #                           i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}
    # idx_s: stores the sentence idx ordered reversely by their page-rank weight.
    # text: stores the sxpText object for the paper
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_cebias,
                 remove_stopwords=default_remove_stopword):
        self.remove_stopwords = remove_stopwords
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.text = LoadSxptext(pickle_path)
        self.s = []  # sentence weight, is a len(sentences) * 1 array
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*2 matrix, each element is (row_idx, column_idx)
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.page_rank_cebias()
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
    def page_rank_cebias(self):
        g = create_graph(self.text, self.remove_stopwords)
        pr = nx.pagerank(g)
        self.s = np.array(pr.values())  # pr.values() return a list storing sentences's page-rank weight in original sentence order
        # -- get sentence weight that obtained by page-rank for cesim_graph --
        if self.ceopt == "mance":
            cesim_sw = Pagerank_CESimGraph_for_CEBias(self.mancesimgraph, len(self.text.sentenceset))
        else:
            cesim_sw = Pagerank_CESimGraph_for_CEBias(self.syscesimgraph, len(self.text.sentenceset))
        # -- Get the combined sentence weight, which is obtained by [CEsim-sw*cebias + Para-sw*(1-cebias)]
        if len(cesim_sw) == len(self.s):
            print "combine ce-sim-graph sentweight with iteration weight"
            self.s = self.s * (1 - self.cebias) + cesim_sw * self.cebias
            self.s = normalize(self.s)
        # -- rank sentences index lists --
        self.idx_s = argsort(array(-self.s), axis=0).reshape(len(self.s), 1)


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################

def TestSimGraphCEBias():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    GS = CEBias_SimGraph(pk)
    # print GS.section2sentence_id_list
    print GS.idx_s
    # for text in GS.OutPutTopKSent(10, maxwords=0):
    #     print text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestSimGraphCEBias()

if __name__ == "__main__":
    main()

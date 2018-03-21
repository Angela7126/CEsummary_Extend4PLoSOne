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
class SimGraph:
    # section2sentence_id_list: stores the mapping between section_title and sentences id that belong to this section
    #                           i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}
    # idx_s: stores the sentence idx ordered reversely by their page-rank weight.
    # text: stores the sxpText object for the paper
    def __init__(self, pickle_path, remove_stopwords=default_remove_stopword):
        self.s = []  # sentence weight, is a len(sentences) * 1 array
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*2 matrix, each element is (row_idx, column_idx)
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.page_rank(self.text)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
    def page_rank(self, sxptxt):
        g = create_graph(sxptxt, self.remove_stopwords)
        pr = nx.pagerank(g)
        self.s = np.array(pr.values())  # pr.values() return a list storing sentences's page-rank weight in original sentence order
        self.s = self.s.reshape((len(self.s), 1))  # change self.s from len(sent) 1D-array to type(self.s) = len(sent)*1 2D-array
        self.idx_s = argsort(array(-self.s), axis=0)  # argsort performs an indirect sort and returns the indices that would sort an array.


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################

def TestSimGraph():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    GS = SimGraph(pk)
    topksent = 10
    ranked_sentences = GS.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestSimGraph()

if __name__ == "__main__":
    main()

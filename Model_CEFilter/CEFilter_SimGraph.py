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
class CEFilter_SimGraph:
    # section2sentence_id_list: stores the mapping between section_title and sentences id that belong to this section
    #                           i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}
    # idx_s: stores the sentence idx ordered reversely by their page-rank weight.
    # text: stores the sxpText object for the paper
    def __init__(self, pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        self.s = []  # sentence weight, is a len(sentences) * 1 array
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*2 matrix, each element is (row_idx, column_idx)
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.remove_stopwords = remove_stopwords
        self.ceopt = ceopt
        self.text = LoadSxptext(pickle_path)
        self.page_rank_cefilter(ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
    def page_rank_cefilter(self, ceopt=default_ceopt):
        g = create_graph(self.text, self.remove_stopwords)
        pr = nx.pagerank(g)
        self.s = np.array(pr.values())  # pr.values() return a list storing sentences's page-rank weight in original sentence order
        # -- get sentence IDs that contains cause-effect links --
        ce_sidlst = self.text.mance_sent_id_dict.keys()
        if ceopt == 'sysce':
            ce_sidlst = self.text.sysce_sent_id_dict.keys()
        # -- If there is no sentence that contains cause-effect link in this paper, do not rank sentences --
        if len(ce_sidlst) == 0:
            return
        # -- set the weight of sentences which contains no cause-effect links as 0 --
        ce_sidlst.sort()
        snum = len(self.s)
        for sid in range(snum):
            if sid not in ce_sidlst:
                self.s[sid] = 0
        # -- normalize sentence weight --
        self.s = normalize(self.s)
        # -- rank sents index lists --
        idx_s_inc0 = list(argsort(array(-self.s), axis=0))  # The idx_s which contains 0 value sentences
        while self.s[idx_s_inc0[-1]] == 0:
            del idx_s_inc0[-1]
        self.idx_s = array(idx_s_inc0).reshape(len(idx_s_inc0), 1)


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################

def TestSimGraphCEfilter():
    pk = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CEFilter_SimGraph(pk)
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    print model.idx_s, len(model.idx_s)
    print model.s, len(model.s)

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestSimGraphCEfilter()

if __name__ == "__main__":
    main()

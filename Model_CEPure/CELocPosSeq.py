# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------------------
# Name:        CELocPosSeq
# Purpose:  Ranked sentences according to whether they contains cause-effect links
#           and the location in the paper by positive sequence
#
# -------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nx
import numpy as np
from cmyToolkit import *
from sxpPackage import *
from cmyConfFuncForRankModels import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CELocPosSeq:
    def __init__(self, pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        self.ceopt = ceopt
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.s = np.zeros(len(self.text.sentenceset))
        self.idx_s = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.rank_weight_loc_posseq(ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    def rank_weight_loc_posseq(self, ceopt=default_ceopt):
        ce_sidlst = self.text.mance_sent_id_dict.keys()
        if ceopt == 'sysce':
            ce_sidlst = self.text.sysce_sent_id_dict.keys()
        # -- If current paper dose not contains cause-effect links, do not need to rank sentences ---
        if len(ce_sidlst) == 0:
            return
        # -- rank sentences containing according to their occurrence in paper ---
        ce_sidlst.sort(reverse=True)  # The main difference to CELocNegseq.rank_weight_loc_posseq
        for i, sid in enumerate(ce_sidlst):
            self.s[sid] = i+1
        # -- delete sentences that contains no cause-effect links --
        idx_s_inc0 = list(argsort(array(-self.s), axis=0))  # The idx_s which contains 0 value sentences
        while self.s[idx_s_inc0[-1]] == 0:
            del idx_s_inc0[-1]
        self.idx_s = array(idx_s_inc0).reshape(len(idx_s_inc0), 1)


#######################################################################################
# -------------------------------- Test Functions ----------------------------------- #
#######################################################################################
def TestPickle():
    pkfp1 = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    pkfp2 = os.path.join(kg_dir, "pickle", "f0001.txt_2.pk")
    sxptxt1 = LoadSxptext(pkfp1)
    sxptxt2 = LoadSxptext(pkfp2)
    print len(sxptxt1.sentenceset)
    print len(sxptxt2.sentenceset)

def TestCELocPosSeq():
    pkfp1 = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CELocPosSeq(pkfp1, ceopt="mance")
    topksent = 10
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    print model.section2sentence_id_list
    print model.idx_s, len(model.idx_s)
    print model.s, len(model.s)
    # for idx in range(topksent):
    #     print '----------------'
    #     print idx, ranked_sentences[idx].sentence_text


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    # TestPickle()
    TestCELocPosSeq()

if __name__ == '__main__':
    main()
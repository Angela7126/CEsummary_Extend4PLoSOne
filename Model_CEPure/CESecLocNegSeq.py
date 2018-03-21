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
class CESecLocNegSeq:
    def __init__(self, pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        self.ceopt = ceopt
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.s = np.zeros(len(self.text.sentenceset))
        self.idx_s = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.rank_weight_secloc_negseq(ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)
        self.ReRankSentBySectionNeg()

    def rank_weight_secloc_negseq(self, ceopt=default_ceopt):
        ce_sidlst = self.text.mance_sent_id_dict.keys()
        if ceopt == 'sysce':
            ce_sidlst = self.text.sysce_sent_id_dict.keys()
        # -- If current paper dose not contains cause-effect links, do not need to rank sentences ---
        if len(ce_sidlst) == 0:
            return
        # -- If current paper contains cause-effect links, rank sentences that contains ---
        ce_sidlst.sort()  # The main difference to CESecLocPosSeq.rank_weight_secloc_posseq
        for i, sid in enumerate(ce_sidlst):
            self.s[sid] = i+1   # +1是为了在计算idx_s时避免误删有因果关系的句子
        # -- delete sentences that contains no cause-effect links --
        idx_s_inc0 = list(argsort(array(-self.s), axis=0))  # The idx_s which contains 0 value sentences
        while self.s[idx_s_inc0[-1]] == 0:
            del idx_s_inc0[-1]
        self.idx_s = array(idx_s_inc0).reshape(len(idx_s_inc0), 1)

    # ---------- Rerank sentences according to their occurrence in turn in each section -------------
    def ReRankSentBySectionNeg(self):
        # -- If we do not rank sentences in paper, then we do not need to re rank it by position --
        if len(self.ranked_sentences) == 0:
            return
        # -- Else, rank sentences according to their position in sections in turn.--
        # Get section title list
        sectaglst = []
        for sec in self.text.section_list:
            sectaglst.append(sec.title)
        sectaglst.reverse()  # The main difference to CESecLocPosSeq.ReRankSentBySectionPos
        # Get the max num of sentence in section
        snum_max = 0
        sec2sidlist = self.section2sentence_id_list
        for sectag in sectaglst:
            if len(sec2sidlist[sectag]) > snum_max:
                snum_max = len(sec2sidlist[sectag])
        # Rerank sentences according to their position
        ranked_sentences = []
        for sidx in range(snum_max):
            for sectag in sectaglst:
                if sidx >= len(sec2sidlist[sectag]):
                    continue
                ranked_sentences.append(self.text.sentenceset[sec2sidlist[sectag][sidx]])
        self.ranked_sentences = ranked_sentences

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

def TestCESecLocNegSeq():
    pkfp1 = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CESecLocNegSeq(pkfp1, ceopt="mance")
    topksent = 20
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
    TestCESecLocNegSeq()

if __name__ == '__main__':
    main()
# -------------------------------------------------------------------------------
# Name:        sxpContextModel
# Purpose:
#
# Author:      sunxp
#
# Created:     26/10/2015
# Copyright:   (c) sunxp 2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

### Notification:
### The only difference between MySecContextModel and MySecModel lies in:
### MySecContextModel added context as sub-paragraph
### 1. add s_t and t_p matrix to store the belongingness among sentences and context, and among context and paragraph
### 2. add t to store the weight of each context
### 3. add idx_t to store the context idx ordered reversely by their iterated weight.
### 4. add function update_context_weigth() to iterate context's weight
### 5. add function update_paragraph_weight_bycontext() to iterate paragraph's weight use context
### 6. add function update_word_weight_bycontext() to iterate words' weight considering context matrix and weights

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from sxpPackage import *
from cmyToolkit import *
from cmyConfFuncForRankModels import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CEFilter_SecParaCtx:
    # remove_stopwords: 0 means with stopwords; 1 means remove stopwords
    def __init__(self,  pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword, iteration_times=default_itertime):
        self.w_s = None
        self.s_p = None
        self.p_c = None
        self.t_p = None
        self.s_t = None
        self.c_c = None
        self.w = []
        self.s = []
        self.p = []
        self.c = []
        self.t = []  # context weight
        self.idx_w = []
        self.idx_s = []
        self.idx_p = []
        self.idx_c = []
        self.idx_t = []  # sorted context
        self.remove_stopwords = remove_stopwords
        self.times = iteration_times
        self.ceopt = ceopt
        self.words = []
        self.text = LoadSxptext(pickle_path)
        self.section2sentence_id_list = {}
        self.ranked_sentences = []
        if remove_stopwords == 0:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif remove_stopwords == 1:
            self.get_parameters_without_stopwords()
        w = matrix(random.rand(len(self.words))).T
        self.iteration(w)
        self.rank_weight_cefilter(ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)


    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T
        self.t_p = matrix(self.text.p_t.toarray()).T
        self.s_t = matrix(self.text.t_s.toarray()).T
        self.c_c = matrix(self.text.c_c.toarray())

    def get_parameters_without_stopwords(self):
        # -- assign values to words, w_s, s_p, p_c, c_c
        self.get_parameters_with_stopwords()
        # -- get stopwords list
        if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
            getStopWord()
        stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # -- strip stopwords out from self.words and self.w_s
        idx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
               and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        new_w_s = []
        for i in idx:
            new_w_s.append(array(self.w_s[i, :]).tolist())
        new_w_s = matrix(array(new_w_s))
        new_words = [self.words[i] for i in idx]
        self.words = new_words
        self.w_s = new_w_s


    def update_sentence_weight(self, w):
        s = self.w_s.T * w
        s = normalize(s)
        return s

    def update_context_weigth(self, s):
        t = self.s_t.T * s
        t = normalize(t)
        return t

    def update_paragraph_weight_bycontext(self, t):
        p = self.t_p.T * t
        p = normalize(p)
        return p

    def update_section_weight(self, p):
        sec = self.c_c * self.p_c.T * p
        sec = normalize(sec)
        return sec

    def update_word_weight_bycontext(self, w, s, t, p, sec):
        # -- SecSub Model -- #
        w = self.w_s * s + self.w_s*self.s_t*t + self.w_s * self.s_t * self.t_p * p\
            + self.w_s * self.s_t * self.t_p * self.p_c * sec
        w = normalize(w)
        return w

    def iteration(self, w):
        for i in range(self.times):
            s = self.update_sentence_weight(w)

            t = self.update_context_weigth(s)

            p = self.update_paragraph_weight_bycontext(t)

            c = self.update_section_weight(p)

            w = self.update_word_weight_bycontext(w, s, t, p, c)

        self.w = w
        self.s = s
        self.p = p
        self.c = c
        self.t = t

    def rank_weight_cefilter(self, ceopt=default_ceopt):
        # -- rank words, paras, secs context index lists --
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
        self.idx_t = argsort(array(-self.t), axis=0)
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
def TestSecParaCtxCEfilter():
    pk = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CEFilter_SecParaCtx(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    print model.idx_s, len(model.idx_s)
    print model.s, len(model.s)
    # for idx in range(topksent):
    #     print '----------------'
    #     print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestSecParaCtxCEfilter()
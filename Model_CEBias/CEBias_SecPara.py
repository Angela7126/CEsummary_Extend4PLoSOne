# -*- coding: UTF-8 -*-

### Notification:
### The only difference between MySecModel and MyModel lies in that
### 1. MySecModel use section's weight to update the word weight
### 2. MySecModel consider c_c matrix when update section weight

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
class CEBias_SecPara:
    # remove_stopwords: 0 means with stopwords; 1 means remove stopwords
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_cebias,
                 remove_stopwords=default_remove_stopword, iteration_times=default_itertime):
        self.times = iteration_times
        self.remove_stopwords = remove_stopwords
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.text = LoadSxptext(pickle_path)
        self.w_s = None
        self.s_p = None
        self.p_c = None
        self.c_c = None  # section_section matrix, the only difference
        self.w = []
        self.s = []
        self.p = []
        self.c = []
        self.idx_w = []
        self.idx_s = []
        self.idx_p = []
        self.idx_c = []
        self.words = []
        self.section2sentence_id_list = {}
        self.rank_sentences = []

        if remove_stopwords == 0:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif remove_stopwords == 1:
            self.get_parameters_without_stopwords()

        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)

        w = matrix(random.rand(len(self.words))).T
        self.iteration(w)
        self.rank_weight_cebias()  # get idx_w, idx_s, idx_p, idx_c
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- get_parameters_with_stopwords: assign values to words, w_s, s_p, p_c, c_c -- #
    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T
        self.c_c = matrix(self.text.c_c.toarray())

    # -- get_parameters_without_stopwords: assign values to words, w_s, s_p, p_c and strip stopwords out-- #
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

    def update_paragraph_weight(self, s):
        p = self.s_p.T * s
        p = normalize(p)
        return p

    def update_section_weight(self, p):
        sec = self.c_c * self.p_c.T * p
        sec = normalize(sec)
        return sec

    def update_word_weight(self, w, s, p, sec):
        # -- Section Model -- #
        w = self.w_s * s + self.w_s * self.s_p * p + self.w_s * self.s_p * self.p_c * sec
        w = normalize(w)
        return w

    def iteration(self, w):
        for i in range(self.times):
            s = self.update_sentence_weight(w)

            p = self.update_paragraph_weight(s)

            c = self.update_section_weight(p)

            w = self.update_word_weight(w, s, p, c)

        self.w = w
        self.s = s
        self.p = p
        self.c = c

    # -- rank_weight_CEBias: get idx_w, idx_s, idx_p, idx_c -- #
    def rank_weight_cebias(self):
        if self.ceopt == "mance":
            cesim_sw = Pagerank_CESimGraph_for_CEBias(self.mancesimgraph, len(self.text.sentenceset))
        else:
            cesim_sw = Pagerank_CESimGraph_for_CEBias(self.syscesimgraph, len(self.text.sentenceset))
        # -- rank words, sents, contexts, paras, secs and get the index lists --
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
        # -- Get the combined sentence weight, which is obtained by [CEsim-sw*cebias + Para-sw*(1-cebias)]
        if len(cesim_sw) == len(self.s):
            print "combine ce-sim-graph sentweight with iteration weight"
            self.s = self.s * (1 - self.cebias) + cesim_sw * self.cebias
            self.s = normalize(self.s)
        # -- rank sentences index lists --
        self.idx_s = argsort(array(-self.s), axis=0)


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestSecParaCEBias():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEBias_SecPara(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestSecParaCEfliter()
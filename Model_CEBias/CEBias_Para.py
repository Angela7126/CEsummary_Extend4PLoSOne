# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from cmyToolkit import *
from sxpPackage import *
from cmyConfFuncForRankModels import *


#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CEBias_Para:
    # remove_stopwords: 0 means with stopwords; 1 means remove stopwords
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_cebias,
                 remove_stopwords=default_remove_stopword, iteration_times=default_itertime):
        self.remove_stopwords = remove_stopwords
        self.times = iteration_times
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.text = LoadSxptext(pickle_path)  # sxpText object
        self.w_s = None  # word_sentence matrix
        self.s_p = None  # sentence_paragraph matrix
        self.p_c = None  # paragraph_section matrix
        self.w = []  # words weight, is a len(words) * 1 matix
        self.s = []  # sentence weight, is a len(sentences) * 1 matix
        self.p = []  # paragraph weight, is a len(paragraph) * 1 matix
        self.c = []  # section weight, is a len(section) * 1 matix
        self.idx_w = []  # words idx ordered reversely by their iterated weight, because self.w is a 2D list, idx_w is len(words)*2 matrix, each element is (row_idx, column_idx)
        self.idx_s = []  # sentence idx ordered reversely by their iterated weight. idx_s is len(sentence)*2 matrix, each element is (row_idx, column_idx)
        self.idx_p = []  # paragraph idx ordered reversely by their iterated weight. idx_p is len(paragraph)*2 matrix, each element is (row_idx, column_idx)
        self.idx_c = []  # section idx ordered reversely by their iterated weight. idx_c is len(section)*2 matrix, each element is (row_idx, column_idx)
        self.words = []   # keywords list
        self.section2sentence_id_list = {}  # i.e. {"1 Introduction": [8,9,10,11...21]; "2 Semantic Link":[22,23,...,31]; ...}
        self.ranked_sentences = []
        if remove_stopwords == 0:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif remove_stopwords == 1:
            self.get_parameters_without_stopwords()

        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)

        w = matrix(random.rand(len(self.words))).T  # Initial words weight vector
        self.iteration(w)
        self.rank_weight_cebias()  # get idx_w, idx_s, idx_p, idx_c
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    # -- get_parameters_with_stopwords: assign values to words, w_s, s_p, p_c -- #
    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T

    # -- get_parameters_without_stopwords: assign values to words, w_s, s_p, p_c and strip stopwords out-- #
    def get_parameters_without_stopwords(self):
        # -- assign values to words, w_s, s_p, p_c
        self.get_parameters_with_stopwords()
        # -- get stopwords list
        if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
            getStopWord()
        stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # -- strip stopwords out from self.words and self.w_s
        idx = [i for i in range(len(self.words)) if self.words[i].lower() not in stopwords
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
        sec = self.p_c.T * p
        sec = normalize(sec)
        return sec

    def update_word_weight(self, w, s, p, sec):
        w = self.w_s * s + self.w_s * self.s_p * p
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
        # -- rank words, sents, paras, secs index lists --
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
        # -- Get the combined sentence weight, which is obtained by [CEsim-sw*cebias + Para-sw*(1-cebias)]
        if len(cesim_sw) == len(self.s):
            print "combine ce-sim-graph sentweight with iteration weight"
            self.s = self.s*(1-self.cebias) + cesim_sw*self.cebias
            self.s = normalize(self.s)
        # -- rank sentences index lists --
        self.idx_s = argsort(array(-self.s), axis=0)


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestParaCEBias():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEBias_Para(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestParaCEBias()
    # f = open(os.path.join(corpdir, 'stopwords.txt'), 'r')
    # lines = f.readlines()
    # f.close()
    # stopwords = [line.strip() for line in lines]
    # words = ["world", "hall", "above", "actually", "Yeah", "Again", "1.23"]
    # idx = [i for i in range(len(words)) if words[i].lower() not in stopwords
    #        and re.match(r'^[a-zA-Z]+$', words[i]) is not None]
    # data = [
    #     [1, 2, 3, 4, 5, 6, 7],
    #     [2, 3, 4, 5, 6, 7, 8],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [4, 5, 6, 7, 8, 9, 10],
    #     [0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0]
    # ]
    # new_words = [words[i] for i in idx]
    # w_s = matrix(np.array(data))
    # new_w_s = []
    # for i in idx:
    #     new_w_s.append(array(w_s[i, :]).tolist())
    # new_w_s = matrix(array(new_w_s))
    # print new_w_s
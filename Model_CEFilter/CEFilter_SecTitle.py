# -------------------------------------------------------------------------------
# Name:        MySecTitleNetwork
# Purpose:     In order to increase the weight of words in the section title
#
# Author:      sunxp
#
# Created:     12/06/2016
# Copyright:   (c) sunxp 2016
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

### Notification:
### The difference between MySecTitleNetwork and MySecModel lies in:
###   The original thought that words in section title may be more important,
### so we add a weight vector tk and two belongingness matrix s_tk, w_tk and
### rewrite the word_weight_update function to increase weight of words in
### section title.
### 1. tk: (length of token list from main body)*1 vector, the word weight for words in section title
### 2. s_tk: (number of sentences)*(length of token list from main body) matrix, for each sentence set its section title words as 1, other words as 0
### 3. w_tk: (length of token list from main body)*(length of token list from main body) matrix = w_s * s_tk, only set words appearing in section title as 1
### 4. update_section_title_weight: update tk = normalize(s_tk.T * s)
### 5. update_word_weight:
###      w1 = word weight update as same as MySecModel
###      w2 = w_tk*tk
###      w = normalize(w1+w2)
### 6. word_count: a vector stores word count number for token list from main body

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
class CEFilter_SecTitle:
    # remove_stopwords: 0 means with stopwords; 1 means remove stopwords
    def __init__(self, pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword, iteration_times=default_itertime):
        self.w_s = None
        self.s_p = None
        self.p_c = None
        self.c_c = None
        self.s_tk = None  # sentence_section-title-words matrix
        self.w_tk = None  # words_section-title-words matrix
        self.tk = []  # initial section title words weight vector
        self.w = []
        self.s = []
        self.p = []
        self.c = []
        self.idx_w = []
        self.idx_s = []
        self.idx_p = []
        self.idx_c = []
        self.remove_stopwords = remove_stopwords
        self.times = iteration_times
        self.ceopt = ceopt
        self.words = []
        self.word_count = []
        self.sec_title_word_set = []
        self.ranked_sentences = []
        self.ranked_word = []
        self.text = LoadSxptext(pickle_path)
        self.section2sentence_id_list = {}
        if remove_stopwords == 0:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif remove_stopwords == 1:
            self.get_parameters_without_stopwords()
        self.BuildTitleNetwork()  # build title network
        # self.word_count = self.Buildwordcount()  # add a new attribute named as "word_count" to sxpText object
        # self.NormalizeWS()
        w = matrix(random.rand(len(self.words))).T  # initial
        self.iteration(w)
        self.rank_weight_cefilter(ceopt)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.word_count = self.text.sentence_tfidf.ct.sum(axis=0).T
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T
        self.c_c = matrix(self.text.c_c.toarray())

    def get_parameters_without_stopwords(self):
        # -- assign values to words, w_s, s_p, p_c
        self.get_parameters_with_stopwords()
        # -- get stopwords list
        if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
            getStopWord()
        stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # -- strip stopwords out from self.words and self.w_s
        idx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
               and re.match(r'^[a-zA-Z\-]+$', self.words[i]) is not None]
        new_w_s = []
        new_word_count = []
        for i in idx:
            new_w_s.append(array(self.w_s[i, :]).tolist())
            new_word_count.append(self.word_count[(i,0)])
        new_words = [self.words[i] for i in idx]
        new_w_s = matrix(array(new_w_s))
        new_word_count = matrix(array(new_word_count)).T
        self.words = new_words
        self.w_s = new_w_s
        self.word_count = new_word_count

    def BuildTitleNetwork(self):
        section_list = self.text.section_list
        self.sec_title_word_set = []
        for i, eachsec in enumerate(section_list):
            # print i, eachsec.title
            title_word_index = self.GetWordIndex(eachsec.title.lower())
            self.sec_title_word_set.append(title_word_index)

        self.tk = matrix(random.rand(len(self.words))).T
        self.s_tk = matrix(np.zeros(self.w_s.T.shape, dtype=np.float))

        for sent in self.text.sentenceset:
            wi = self.sec_title_word_set[sent.id_sec]
            self.s_tk[sent.id, wi] = 1
        self.w_tk = self.w_s*self.s_tk

    def GetWordIndex(self, sent):
        pat = '[\s|\:|,]'
        ws = re.split(pat, sent)
        ws = [w for w in ws if len(w) > 0]
        index_list = []
        for w in ws:
            if w in self.words:
                index_list.append(self.words.index(w))
            # else:
            #     index_list.append(-1)  # 这里不合理，为什么没有该词时要加-1? 导致BuildTitleNetwork建words list中最后一个与该section所有句子的链接
        return index_list

    # 这个函数不对, 直接从sentence split得到的word 和 self.words中的tokens是不同的，不如直接都用sentence_tfidf.ct相加得到， 这样tokens是一样的
    # def Buildwordcount(self):
    #     word_dict = {}  # record words and their appearance time in all sentences
    #     nwd = 0
    #     # print u'applications' in self.words
    #     for eachsent in self.text.sentenceset:
    #         wds = SplitSentence(eachsent.sentence_text.lower())
    #         for wd in wds:
    #             if wd not in self.words:   # ignore words that are not in token list
    #                 continue
    #             else:
    #                 if wd in word_dict:
    #                     word_dict[wd] += 1.0
    #                 else:
    #                     word_dict[wd] = 1.0
    #                     nwd += 1
    #
    #     word_count = matrix(np.zeros((len(self.words), 1), dtype=np.float))
    #     for i, wd in enumerate(self.words):
    #         if wd in word_dict:
    #             word_count[i, 0] = word_dict[wd]
    #     return word_count

    def rank_weight_cefilter(self, ceopt=default_ceopt):
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
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

    def update_section_title_weight(self, s):
        tk = self.s_tk.T * s
        tk = normalize(tk)
        return tk

    def update_word_weight(self, w, s, p, c):
        w = self.w_s * s + self.w_s * self.s_p * p\
            + self.w_s * self.s_p * self.p_c * c
        # w = self.w_s * s + self.w_s * self.s_p * p  #this is the mostly used model
        w = normalize(w)
        return w

    def iteration(self, w):
        for i in range(self.times):
            s = self.update_sentence_weight(w)

            tk = self.update_section_title_weight(s)

            p = self.update_paragraph_weight(s)

            c = self.update_section_weight(p)

            w1 = self.update_word_weight(w, s, p, c)
            w2 = normalize(self.w_tk*tk)
            w = normalize(w1+w2)
        self.w = w
        self.s = s
        self.p = p
        self.c = c

    # this function do not involve the number of words in the paper
    # i.e. this function do not divide the all word count
    def NormalizeWS(self):
        # s_w = self.w_s.T / self.text.word_count.T
        t = np.sum(self.word_count)
        # s_w = self.w_s.T / t
        self.w_s = np.multiply(self.w_s, self.word_count)/t


#######################################################################################
# -------------------------------- Some tool functions ------------------------------ #
#######################################################################################
def SplitSentence(sent_txt):
    pat = r'[\s,\(\)\[\]\:\?\"\'\/]'
    s = re.split(pat, sent_txt)
    return s

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestSecTitleCEfilter():
    pk = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CEFilter_SecTitle(pk)
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    print model.idx_s, len(model.idx_s)
    print model.s, len(model.s)
    # topksent = 10
    # tops = model.OutPutTopKSentWeight(topksent, 1, -1)
    # for i, eachs in enumerate(tops):
    #     print '----------------'
    #     print i, eachs

    # model.OutPutTopKWord(20)
    # sent_id = 79
    # s_w = model.w_s.T[sent_id, :]
    # print s_w[s_w > 0.0]
    # print model.text.sentenceset[sent_id].sentence_text
    #
    # sent_id = 57
    # s_w = model.w_s.T[sent_id, :]
    # print s_w[s_w > 0.0]
    #
    # sections = model.text.section_list
    # for sec in sections:
    #     print sec.title.lower()
    #     for idx in model.sec_title_word_set[sec.id]:
    #         print model.words[idx],
    #     print
    #     print

def TestText():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    text = LoadSxptext(pk)
    for i, eachsent in enumerate(text.sentenceset):
        print i, eachsent.sentence_text
    print text.sentence_tfidf.word
    # print text.sentence_tfidf.tfidf[79, :]

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    cmdstr = 'testrank'
    if cmdstr == 'testrank':
        TestSecTitleCEfilter()
    if cmdstr == 'testtext':
        TestText()


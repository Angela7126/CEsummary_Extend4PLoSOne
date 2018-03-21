# -*- coding: UTF-8 -*-

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
class CEBias_TfIdf:
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_cebias,
                 remove_stopwords=default_remove_stopword):
        self.remove_stopwords = remove_stopwords
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.text = LoadSxptext(pickle_path)
        self.words = self.text.sentence_tfidf.word
        self.count_words = []
        self.w_s = []
        self.s = []
        self.idx_s = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.get_sentence_weight()
        self.rank_sentences_cebias()
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)


    def get_sentence_weight(self):
        # -- get stopwords list --
        stopwords = []
        if self.remove_stopwords == 1:
            if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
                getStopWord()
            stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # -- visit each sentence and get words and their appearance times in main body --
        sentences = self.text.sentenceset
        words_count = {}
        for sent in sentences:
            # get words in current sentence that are not stopwords and contains only a~zA~Z
            words = sent.sentence_text.split()
            words = [word.lower() for word in words]
            words = [word for word in words if word not in stopwords and re.match(r'^[a-zA-Z]+$', word) is not None]
            # count word and update key and value in words_count
            for word in words:
                if word in words_count:
                    words_count[word] += 1
                else:
                    words_count[word] = 1
        # -- get (appearance times, words) list, and sort them by their appearance times reversely
        aux = [(words_count[k], k) for k in words_count.keys()]
        aux.sort(reverse=True)
        self.count_words = aux

    def rank_sentences_cebias(self):
        # -- get stopwords list --
        stopwords = []
        if self.remove_stopwords == 1:
            if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
                getStopWord()
            stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # get the non-stopwords indexes in token list
        allwidx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
                      and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        # get the words_sentences matrix, which are all tf_idf values on sentence_level
        self.w_s = matrix(self.text.s_k.toarray()).T
        # -- get tfidf weight for each sentence--
        words2sentences = []
        for i in allwidx:
            words2sentences.append(array(self.w_s[i, :]).tolist())
        w2s_tfidf_mat = matrix(array(words2sentences))
        wnum, snum = w2s_tfidf_mat.shape
        # -- sumup all non-stop words' tf-idf value as the sentences' weight
        e = matrix(ones(wnum)).T
        self.s = normalize(w2s_tfidf_mat.T * e)
        # -- page rank the cesim-graph --
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
        self.idx_s = argsort(array(-self.s), axis=0)



#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestTfIdfCEBias():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEBias_TfIdf(pk)
    # for k, v in tfidf.count_words:
    #     print v, k
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestTfIdfCEBias()

if __name__ == '__main__':
    main()




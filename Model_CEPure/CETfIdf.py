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
class CETfIdf:
    def __init__(self, pickle_path, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        self.ceopt = ceopt
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.words = self.text.sentence_tfidf.word
        self.count_words = []
        self.get_word_counts(ceopt, remove_stopwords)
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s = np.zeros(len(self.text.sentenceset))
        self.idx_s = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.rank_sentences_cepure(ceopt, remove_stopwords)
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)


    def get_word_counts(self, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        # -- get stopwords list --
        stopwords = []
        if remove_stopwords == 1:
            if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
                getStopWord()
            stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # -- visit each sentence and get words and their appearance times in main body --
        words_count = {}
        for sent in self.text.sentenceset:
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

    def rank_sentences_cepure(self, ceopt=default_ceopt, remove_stopwords=default_remove_stopword):
        # -- get sentence IDs that contains cause-effect links --
        ce_sidlst = self.text.mance_sent_id_dict.keys()
        if ceopt == 'sysce':
            ce_sidlst = self.text.sysce_sent_id_dict.keys()
        # -- If current paper dose not contains cause-effect links, do not need to rank sentences ---
        if len(ce_sidlst) == 0:
            return
        # -- If current paper contains cause-effect links, rank sentences that contains cause-effect links ---
        ce_sidlst.sort()
        # -- get stopwords list --
        stopwords = []
        if remove_stopwords == 1:
            if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
                getStopWord()
            stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
        # get the non-stopwords indexes in token list
        allwidx = [i for i in range(len(self.words)) if self.words[i] not in stopwords
                      and re.match(r'^[a-zA-Z]+$', self.words[i]) is not None]
        # get the words_sentences matrix, which are all tf_idf values on sentence_level
        # -- get tfidf weight for each sentence--
        words2sentences = []
        for i in allwidx:
            words2sentences.append(array(self.w_s[i, :]).tolist())
        w2s_tfidf_mat = matrix(array(words2sentences))
        wnum, snum = w2s_tfidf_mat.shape
        # -- set the weight of sentences which contains no cause-effect links as 0 --
        for sid in range(snum):
            if sid not in ce_sidlst:
                w2s_tfidf_mat[:, sid] = 0
        # -- sumup all non-stop words' tf-idf value as the sentences' weight
        e = matrix(ones(wnum)).T
        self.s = w2s_tfidf_mat.T * e
        # -- Delete sentences without cause-effect links from sent ranked idx --
        idx_s_inc0 = list(argsort(array(-self.s), axis=0))  # The idx_s which contains 0 value sentences
        while self.s[idx_s_inc0[-1]] == 0:
            del idx_s_inc0[-1]
        self.idx_s = array(idx_s_inc0).reshape(len(idx_s_inc0), 1)



#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestCETfIdf():
    pk = os.path.join(kg_dir, "pickle", "f0002.txt_1.pk")
    model = CETfIdf(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    print ranked_sentences
    print model.idx_s, len(model.idx_s)
    print model.s, len(model.s)
    # for idx in range(topksent):
    #     if idx >= len(ranked_sentences):
    #         break
    #     print '----------------'
    #     print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestCETfIdf()

if __name__ == '__main__':
    main()




# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nk
from sxpPackage import *
from cmyToolkit import *
from cmyConfFuncForRankModels import *

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class WordGraph:
    def __init__(self, pickle_path, word_window=default_word_window, remove_stopwords=default_remove_stopword):
        self.remove_stopwords = remove_stopwords
        self.word_window = word_window
        self.text = LoadSxptext(pickle_path)
        self.s = np.zeros(len(self.text.sentenceset))
        self.w = []
        self.idx_s = []
        self.idx_w = []
        self.words = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.page_rank()
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    def page_rank(self):
        g = create_wordgraph(self.text, self.remove_stopwords, self.word_window)
        pr = nk.pagerank(g)
        for elem in pr.items():
            self.words.append(elem[0])
            self.w.append(elem[1])
        self.idx_w = argsort(-array(self.w)).tolist()
        for sid, sent in enumerate(self.text.sentenceset):
            words = sent.sentence_text.split()
            for word in words:
                word = word.lower()
                if word not in pr.keys():
                    continue
                self.s[sid] += pr[word]
        self.s = normalize(self.s)
        self.idx_s = argsort(array(-self.s), axis=0).reshape(len(self.s), 1)


#######################################################################################
# -------------------------------- Words graph building ----------------------------- #
#######################################################################################
# ---- create_graph function: ---- #
# Input: pickle file path of sxpText object; window size
# Output: a words graph: each words in the whole token list is a node, words that appear in a given window will set up a edges
# for example:
#   text = 'There was never a night or a problem that could defeat sunrise or hope.'
#   token list = ['there', 'was', 'never', 'a', 'night', 'or', 'problem', 'that', 'could', 'defeat', 'sunrise', 'hope']
#   node list = token list
#   set window size = 3
#   edges: because "There was never" appear together in text, so add edges between "there", "was", "a"; in the same way,
#          edges are also been added between "was","never","a", ...
def create_wordgraph(sxptxt, remove_stopwords=default_remove_stopword, word_window=default_word_window):
    sentences = sxptxt.sentenceset
    g = nk.Graph()

    stopwords = []
    if remove_stopwords == 1:
        if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
            getStopWord()
        stopwords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))

    for sent in sentences:
        words = sent.sentence_text.split()
        for i in range(len(words)):
            if words[i].lower() in stopwords or re.match(r'^[a-zA-Z]+$', words[i]) is None:
                continue
            for j in range(i + 1, i + word_window):
                if j < 0 or j >= len(words):
                    continue
                if words[j].lower() in stopwords or re.match(r'^[a-zA-Z]+$', words[j]) is None:
                    continue
                g.add_edge(words[i].lower(), words[j].lower())
    return g

#######################################################################################
# ----------------------- Some test and demonstration functions --------------------- #
#######################################################################################
def ShowRankedWords():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    wg = WordGraph(pk)
    sorted_word = [[wg.words[wg.idx_w[i]], wg.w[wg.idx_w[i]]]
                   for i in range(len(wg.words))]
    for word in sorted_word:
        print word

def Testread():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    sxptxt = LoadSxptext(pickle_path)
    print sxptxt.sentence_tfidf.word


def TestWordGraph():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = WordGraph(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestWordGraph()
    # ShowRankedWords()

if __name__ == '__main__':
    main()

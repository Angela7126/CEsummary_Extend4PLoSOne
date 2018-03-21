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
class CEBias_WordGraph:
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_cebias,
                 word_window=default_word_window, remove_stopwords=default_remove_stopword):
        self.remove_stopwords = remove_stopwords
        self.word_window = word_window
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.text = LoadSxptext(pickle_path)
        self.s = np.zeros(len(self.text.sentenceset))
        self.w = []
        self.idx_s = []
        self.idx_w = []
        self.words = []
        self.ranked_sentences = []
        self.section2sentence_id_list = {}
        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.page_rank_cebias()
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)

    def page_rank_cebias(self):
        g = create_wordgraph(self.text, self.remove_stopwords, self.word_window)
        pr = nx.pagerank(g)
        for elem in pr.items():
            self.words.append(elem[0])
            self.w.append(elem[1])
        self.idx_w = argsort(-array(self.w)).tolist()
        # -- Get sentence weight array self.s -------
        for sid, sent in enumerate(self.text.sentenceset):
            words = sent.sentence_text.split()
            for word in words:
                word = word.lower()
                if word not in pr.keys():
                    continue
                self.s[sid] += pr[word]
        self.s = normalize(self.s)
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
        # -- rank words, sents index lists --
        self.idx_s = argsort(array(-self.s), axis=0).reshape(len(self.s),1)

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
    g = nx.Graph()
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
    wg = CEBias_WordGraph(pk)
    sorted_word = [[wg.words[wg.idx_w[i]], wg.w[wg.idx_w[i]]]
                   for i in range(len(wg.words))]
    for word in sorted_word:
        print word

def Testread():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    sxptxt = LoadSxptext(pk)
    print sxptxt.sentence_tfidf.word


def TestWordGraphCEBias():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEBias_WordGraph(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
def main():
    TestWordGraphCEBias()
    # ShowRankedWords()

if __name__ == '__main__':
    main()

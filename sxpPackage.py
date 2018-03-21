__author__ = 'sxp'
# -*- coding: UTF-8 -*-
# --------------------------------------------------------------------------------------------------------
# Name:        sxpPackage
# Purpose:     1. Containing sxpText, sxpText2, sxpTFIDF, sxpSectiontTtile,
#                 sxpPara, sxpContext, sxpSent classes. These classes are used to
#                 describe a scientific paper.
#              2. sxpText2: ce_s_man --> manual links' causal-similarity graph
#              3. sxpText2: ce_s_sys --> system links' causal-similarity graph
#              4. sxpText2: ce_man --> sentences weight calculated by PageRanking on ce_s_man
#              5. sxpText2: ce_sys --> sentences weight calculated by PageRanking on ce_s_sys
#              6. _1.pk are sxpText or sxpText2 objects that have no Abstract or Conclusion in sentence_set
#              7. _2.pk are sxpText or sxpText2 objects that have Abstract or Conclusion in sentence_set
# ---------------------------------------------------------------------------------------------------------

from cmyToolkit import *
import networkx as nx
from scipy import *
import numpy as np
import cmyRougeConfig

default_cesim_bias = 0.5
default_remove_stopword = cmyRougeConfig.default_remove_stopword

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class sxpTFIDF:
    ct = None  # vectorizer.fit_transform(corpus) return term-document matrix crs_matrix
    tfidf = None  # transformer.fit_transform(ct) return tf-idf matrix crs_matrix
    word = None  # vectorizer.get_feature_names() return the tokens list in the whole corpus
    weight = None  # tfidf.toarray()

    def GetKeywordCount(self):
        return len(self.word)

    def GetWeightArray(self):
        return self.tfidf.toarray()

    def GetKeyword(self, i):
        return self.word[i]

    def GetXY(self, x, y):
        [r, c] = self.ct.shape
        if x >= c or y >= r:
            return None
        else:
            return [self.ct[x,y],self.tfidf[x,y]]

    def GetCTRow(self, i):
        [r,c] = self.ct.shape
        if i>= r:
            return None
        else:
            return self.ct.getrow(i).toarray()  # numpy.ndarray

    def GetCTCol(self, i):
        [r,c] = self.ct.shape
        if i>= c:
            return None
        else:
            return self.ct.getcol(i).toarray()  # numpy.ndarray

    def GetWeightRow(self, i):
        [r,c] = self.tfidf.shape
        if i>= r:
            return None
        else:
            return self.tfidf.getrow(i).toarray()  # numpy.ndarray

    def GetWeightCol(self, i):
        [r,c] = self.tfidf.shape
        if i>= c:
            return None
        else:
            return self.tfidf.getcol(i).toarray()  # numpy.ndarray

class sxpResult:
    def __init__(self):
        self.importance_sentset = []

class sxpText:
    fname = ''
    title = ''
    abstract = ''
    relatedwork = ''
    conclusion = ''
    reference = ''
    section_id_dict = {}
    section_list = []
    paraset = []
    whole_sectitle = ''
    whole_text = ''
    keycount = None
    para_tfidf = None
    sentence_tfidf = None
    sentenceset = []
    context_set = []
    d_c = None
    c_p = None
    p_s = None
    s_k = None
    t_s = None  # context - sentence
    p_t = None  # paragraph - context
    c_c = None
    man_CE_list = []  # a list: stores manual labeled cause-effect links
    mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
    sys_CE_list = []  # a list: stores pattern matched cause-effect links
    sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id
    def __init__(self):
        self.fname = ''  # stores the original file path, "D:\pythonwork\code\paperparse\paper\papers\P14-1052.xhtml"
        self.title = ''  # stores the paper's title, "A Decision-Theoretic Approach to Natural Language Generation"
        self.abstract = ''  # a unicode string, which stores the paper's abstract content, each sentence ended with a '\n'
        self.relatedwork = ''  # a unicode string, which stores the paper's related work section content, each sentence ended with a '\n'
        self.conclusion = ''  # a unicode string, which stores the paper's conclusion section content, each sentence ended with a '\n'
        self.reference = ''  # a unicode string, which stores the paper's reference content, each sentence ended with a '\n'
        self.section_id_dict ={}  # mapping string section id like "S1.SS2" to auto-increase position id of section in section_list,
                                  # i.e. "S1.SS2" is mapping to 3, and the section_list[3] is the "S1.SS2" section
        self.section_list = []  # a sxpSectionTitle object list, each element correspond to a section in the paper
        self.paraset = []  # "sxpPara" object list, each element correspond to a paragraph in the paper
        self.whole_sectitle = ''  # a unicode string stores all the section names of the paper, each line is the title of a section
        self.whole_text = ''  # a unicode string stores the main body text of the paper, each line is the text of a paragraph. It is used to get the keycount.
        self.keycount = None  # stores the "sxpTextCount" object for current paper
        self.para_tfidf = None  # stores the TFIDF matrix on paragraph level
        self.sentence_tfidf = None  # stores the TFIDF matrix on sentence level
        self.sentenceset = []  # "sxpSent" object list, each element correspond to a sentence in the paper
        self.d_c = None  # document-section matrix
        self.c_p = None  # section-paragraph matrix
        self.p_s = None  # paragraph-sentence matrix
        self.s_k = None  # sentence-keyword matrix
        self.context_set = []  # "sxpContext" object list, each element correspond to a context in the paper.
        self.t_s = None  # context-sentence matrix
        self.p_t = None  # paragraph-context matrix
        self.c_c = None  # section-section matrix (focus on the belongingness between section, subsection, subsubsection)
        self.man_CE_list = []  # a list: stores manual labeled cause-effect links
        self.mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
        self.sys_CE_list = []  # a list: stores pattern matched cause-effect links
        self.sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id

# ---- sxpSectionTitle only focus on: ---- #
# 1. title
# 2. type (i.e. section, subsection)
# 3. id: (1) id_str in text like 's1ss2'; (2) break id_str into id_set = [('S','1'),('SS', '2')]; (3) id -- the index in sxpText.section_list
# 4. level of the section in paper
class sxpSectionTitle:
    title = ''
    id_str = ''
    id_set = ''
    level = 0
    id = 0
    t_type = ''
    def __init__(self):
        self.title = ''
        self.id_str = ''
        self.id_set = ''
        self.level = 0
        self.id = 0
        self.t_type = ''

class sxpPara:
    para_id = ''
    para_text = ''
    para_tuple = []
    para_tfidf = []
    section_title = ''
    sentenceset = []
    context_set = []
    id = 0
    id_sec = 0
    def __init__(self):
        self.para_id = ''
        self.para_text = ''
        self.para_tuple = []
        self.para_tfidf =[]
        self.section_title = ''
        self.sentenceset = []
        self.context_set = []
        self.id = 0
        self.id_sec = 0

class sxpSent:
    sentence_text = ''
    id = 0
    id_para = 0
    id_sec = 0
    manCEidlst = []
    sysCEidlst = []
    def __init__(self):
        self.sentence_text = ''
        self.id = 0
        self.id_para = 0
        self.id_sec = 0
        self.manCEidlst = []
        self.sysCEidlst = []

# ---- A context: ---- #
# 1. is a language unit which is smaller than a paragraph but larger than sentence.
# 2. contains several continuous sentences in a paragraph.
class sxpContext:
    context_txt = ''
    id = 0
    id_para = 0
    id_sec = 0
    context_sent = []
    def __init(self):
        self.id = 0
        self.id_para = 0
        self.id_sec = 0
        self.context_sent = []

class sxpText2:
    fname = ''
    title = ''
    abstract = ''
    relatedwork = ''
    conclusion = ''
    reference = ''
    section_id_dict = {}
    section_list = []
    paraset = []
    whole_sectitle = ''
    whole_text = ''
    keycount = None
    para_tfidf = None
    sentence_tfidf = None
    sentenceset = []
    context_set = []
    d_c = None
    c_p = None
    p_s = None
    s_k = None
    t_s = None  # context - sentence
    p_t = None  # paragraph - context
    c_c = None
    ce_s_man = None  # sentence - sentence matrix, which store manual-extracted cause-effect links' sentences network's edge weight
    ce_s_sys = None  # sentence - sentence matrix, which store algorithm-extracted cause-effect links' sentences network's edge weight
    ce_man = None  # cause-effect sentences' weight which calculated by pagerank
    ce_sys = None  # cause-effect sentences' weight which calculated by pagerank
    man_CE_list = []  # a list: stores manual labeled cause-effect links
    mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
    sys_CE_list = []  # a list: stores pattern matched cause-effect links
    sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id

    def __init__(self, sxptxt, default):
        self.fname = sxptxt.fname  # stores the original file path, "D:\pythonwork\code\paperparse\paper\papers\P14-1052.xhtml"
        self.title = sxptxt.title  # stores the paper's title, "A Decision-Theoretic Approach to Natural Language Generation"
        self.abstract = sxptxt.abstract  # a unicode string, which stores the paper's abstract content, each sentence ended with a '\n'
        self.relatedwork = sxptxt.relatedwork  # a unicode string, which stores the paper's related work section content, each sentence ended with a '\n'
        self.conclusion = sxptxt.conclusion  # a unicode string, which stores the paper's conclusion section content, each sentence ended with a '\n'
        self.reference = sxptxt.reference  # a unicode string, which stores the paper's reference content, each sentence ended with a '\n'
        self.section_id_dict = sxptxt.section_id_dict  # mapping string section id like "S1.SS2" to auto-increase position id of section in section_list,
                                  # i.e. "S1.SS2" is mapping to 3, and the section_list[3] is the "S1.SS2" section
        self.section_list = sxptxt.section_list  # a sxpSectionTitle object list, each element correspond to a section in the paper
        self.paraset = sxptxt.paraset  # "sxpPara" object list, each element correspond to a paragraph in the paper
        self.whole_sectitle = sxptxt.whole_sectitle  # a unicode string stores all the section names of the paper, each line is the title of a section
        self.whole_text = sxptxt.whole_text  # a unicode string stores the main body text of the paper, each line is the text of a paragraph. It is used to get the keycount.
        self.keycount = sxptxt.keycount  # stores the "sxpTextCount" object for current paper
        self.para_tfidf = sxptxt.para_tfidf  # stores the TFIDF matrix on paragraph level
        self.sentence_tfidf = sxptxt.sentence_tfidf  # stores the TFIDF matrix on sentence level
        self.sentenceset = sxptxt.sentenceset  # "sxpSent" object list, each element correspond to a sentence in the paper
        self.d_c = sxptxt.d_c  # document-section matrix
        self.c_p = sxptxt.c_p  # section-paragraph matrix
        self.p_s = sxptxt.p_s  # paragraph-sentence matrix
        self.s_k = sxptxt.s_k  # sentence-keyword matrix
        self.context_set = sxptxt.context_set  # "sxpContext" object list, each element correspond to a context in the paper.
        self.t_s = sxptxt.t_s  # context-sentence matrix
        self.p_t = sxptxt.p_t  # paragraph-context matrix
        self.c_c = sxptxt.c_c  # section-section matrix (focus on the belongingness between section, subsection, subsubsection)
        self.man_CE_list = sxptxt.man_CE_list  # a list: stores manual labeled cause-effect links
        self.mance_sent_id_dict = sxptxt.mance_sent_id_dict  # a dict: map a sentence id to a manual labeled ce link id
        self.sys_CE_list = sxptxt.sys_CE_list  # a list: stores pattern matched cause-effect links
        self.sysce_sent_id_dict = sxptxt.sysce_sent_id_dict  # a dict: map a sentence id to a pattern matched ce link id
        self.ce_s_man = self.MakeCESentMatrix('mance')  # sentence - sentence matrix, which store manual-extracted cause-effect links' sentences network's edge weight
        self.ce_s_sys = self.MakeCESentMatrix('sysce')  # sentence - sentence matrix, which store algorithm-extracted cause-effect links' sentences network's edge weight
        self.ce_man = nx.pagerank(self.ce_s_man)  # cause-effect sentences' weight which calculated by pagerank
        self.ce_sys = nx.pagerank(self.ce_s_sys)  # cause-effect sentences' weight which calculated by pagerank

    # -- normalize a vector -- #
    def normalize(self, w):
        if sum(w) <= 0:
            return w
        w = w / sum(w)
        return w

    # ---- get sentence_sentence causal-similarity graph, we use jaccard similarity between sentences ----
    def MakeCESentMatrix(self, opt, bias=default_cesim_bias, remove_stopword=default_remove_stopword):
        sentences = self.sentenceset
        ce_matrix = np.zeros((len(sentences), len(sentences)), dtype=np.float)
        if opt == 'mance':
            ce_sidlst = self.mance_sent_id_dict.keys()
            CE_list = self.man_CE_list
        elif opt == 'sysce':
            ce_sidlst = self.sysce_sent_id_dict.keys()
            CE_list = self.sys_CE_list
        for ce in CE_list:
            for i in range(len(ce.Staglst)):
                for j in range(i + 1, len(ce.Staglst)):
                    ce_matrix[ce.Staglst[i], ce.Staglst[j]] = 1 * bias
                    ce_matrix[ce.Staglst[j], ce.Staglst[i]] = 1 * bias
        for i in range(len(ce_sidlst)):
            for j in range(i + 1, len(ce_sidlst)):
                si_txt = sentences[ce_sidlst[i]].sentence_text
                sj_txt = sentences[ce_sidlst[j]].sentence_text
                jaccard = jaccard_similarity(si_txt, sj_txt, stopword=remove_stopword)
                ce_matrix[ce_sidlst[i], ce_sidlst[j]] += jaccard * (1-bias)
                ce_matrix[ce_sidlst[j], ce_sidlst[i]] += jaccard * (1-bias)
        for i in range(len(sentences)):
            ce_matrix[i] = self.normalize(ce_matrix[i])
        ceg = nx.Graph()
        for i in range(len(ce_matrix)):
            for j in range(i, len(ce_matrix)):
                if ce_matrix[i, j] > 0:
                    ceg.add_edge(i, j, weight=ce_matrix[i, j])
                if ce_matrix[j, i] > 0:
                    ceg.add_edge(j, i, weight=ce_matrix[j, i])
        return ceg

#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
if __name__ == "__main__":
    fpath = r"E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle\f0001.txt_1.pk"
    sxptxt = LoadSxptext(fpath)
    # for sent in sxptxt.sentenceset:
    #     print dir(sent)
    for ce in sxptxt.mance_sent_id_dict.items():
        print ce
    # print sxptxt.whole_sectitle
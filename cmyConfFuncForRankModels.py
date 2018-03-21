# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nx
import numpy as np
from scipy import *
from cmyToolkit import *
from sxpPackage import *


#######################################################################################
# ---------------------------------- Default Configs -------------------------------- #
#######################################################################################
# ---- default_remove_stopword is the default vaule for 'remove_stopwords' --------------
default_remove_stopword = 0
# ---- default_itertime is the default iteration times --------------
default_itertime = 50
# ---- default_ceopt is the default option for using cause-effect links --------------
default_ceopt = 'sysce'
# ---- default_cesim is the default bias vaule for combining cause-effect links with sentences similarity graph --------------
default_cesim_bias = 0.5
# ---- default_cebias is the default bias value for combining causal-similarity graph with original models --------
default_cebias = 0.65
# ---- default_word_window is the window size of words for building word-graph ranking model --------------
default_word_window = 3

#######################################################################################
# --------------- Functions for generate sent_to_sent graph and matrix -------------- #
#######################################################################################
# -- normalize a vector -- #
def normalize(w):
    if sum(w) <= 0:
        return w
    w = w / sum(w)
    return w


# -- ordered_sentence_id_set(): assign values to section2sentence_id_list -- #
def ordered_sentence_id_set(sxptxt, idx_s):
    ranked_sentences = [sxptxt.sentenceset[idx_s[(i, 0)]] for i in range(len(idx_s))]
    sec_titles = []
    section2sentence_id_list = {}
    for sec in sxptxt.section_list:
        section2sentence_id_list[sec.title] = []
        sec_titles.append(sec.title)
    for sentence in ranked_sentences:
        section_tag = sxptxt.paraset[sentence.id_para].section_title
        if section_tag != '' and section_tag in sec_titles:
            section2sentence_id_list[section_tag].append(sentence.id)
    return ranked_sentences, section2sentence_id_list


# ---- create_graph function: create a sentID-to-sentID word-jaccard similarity graph ---- #
# Input: a sxpText object
# Output: a sentence_sentence graph: each sentence id is a node, the edge weight between nodes is their jaccard similarity
def create_graph(sxptxt, remove_stopword=default_remove_stopword):
    sentences = sxptxt.sentenceset
    # -- Build sentence jaccard similarity matrix --
    g = nx.Graph()
    # use sentence id as graph nodes
    for sent in sentences:
        g.add_node(sent.id)
    # for each pair of sentence, compute their jaccard similarity as the edge weight between them
    for i in range(len(sentences)):
        for j in range(i, len(sentences)):
            sent1 = sentences[i].sentence_text
            sent2 = sentences[j].sentence_text
            jaccard = jaccard_similarity(sent1, sent2, stopword=remove_stopword)
            if jaccard > 0:
                g.add_edge(sentences[i].id, sentences[j].id, weight=jaccard)
                g.add_edge(sentences[j].id, sentences[i].id, weight=jaccard)
    return g


# ---- get sentence_sentence jaccard similarity matrix ----
def MakeSentSentMatrix(sentenceset, remove_stopwords):
    ns = len(sentenceset)
    m = np.zeros((ns, ns), dtype=np.float)
    for i in range(ns):
        for j in range(i, ns):
            sent1 = sentenceset[i].sentence_text
            sent2 = sentenceset[j].sentence_text
            jaccard = jaccard_similarity(sent1, sent2, stopword=remove_stopwords)
            m[i, j] = jaccard
            m[j, i] = jaccard
    return np.matrix(m)


# ---- MakeGraphObjectFromMatrix: create a graph according to a matrix M ---- #
def MakeGraphObjectFromMatrix(M):
    nr, nc = M.shape
    g = nx.DiGraph()
    for i in range(nr):
        g.add_node(i)
    for i in range(nr):
        for j in range(nc):
            jaccard = M[i, j]
            g.add_edge(i, j, weight=jaccard)
    return g


# ---- get sentence_sentence causal-similarity graph, we use jaccard similarity between sentences ----
# Inputs:
# 1. sxptxt: the sxpText object, please refer to sxpPackage.py
# 2. ceopt: the option for cause-effect links.
#           ceopt="mance" means building causal-similarity graph by manually annotated cause-effect links
#           ceopt="sysce" means building causal-similarity graph by automatically extracted cause-effect links
# 3. bias: the bias for combining cause-effect links with Jaccard sentence similarity
# 4. remove_stopword: whether remove stopwords from sentences to calculate Jaccard similarity.
# Outputs:  the causal-similarity graph
def MakeCESimSentGraph(sxptxt, ceopt=default_ceopt, bias=default_cesim_bias, remove_stopword=default_remove_stopword):
    # -- Initial causal-similarity graph --
    ceg = nx.Graph()
    # -- Get Cause-effect links list and sent id list that contains cause-effect links --
    ce_sidlst = sxptxt.mance_sent_id_dict.keys()
    CE_list = sxptxt.man_CE_list
    if ceopt == 'sysce':
        ce_sidlst = sxptxt.sysce_sent_id_dict.keys()
        CE_list = sxptxt.sys_CE_list
    ce_sidlst.sort()
    # -- If current paper does not contain ceopt-type cause-effect links, stop build causal-similarity graph --
    if len(ce_sidlst) == 0:
        return ceg
    # -- If current paper contains cause-effect links, generate causal-similarity graph for it --
    sentences = sxptxt.sentenceset
    ce_matrix = np.zeros((len(sentences), len(sentences)), dtype=np.float)
    # Add cause-effect weight between sentences into ce_matrix with bias
    for ce in CE_list:
        for i in range(len(ce.Staglst)):
            for j in range(i + 1, len(ce.Staglst)):
                ce_matrix[ce.Staglst[i], ce.Staglst[j]] = 1 * bias
                ce_matrix[ce.Staglst[j], ce.Staglst[i]] = 1 * bias
    # Add sentence similarity weight into ce_matrix with (1-bias)
    for i in range(len(ce_sidlst)):
        for j in range(i + 1, len(ce_sidlst)):
            si_txt = sentences[ce_sidlst[i]].sentence_text
            sj_txt = sentences[ce_sidlst[j]].sentence_text
            jaccard = jaccard_similarity(si_txt, sj_txt, stopword=remove_stopword)
            ce_matrix[ce_sidlst[i], ce_sidlst[j]] += jaccard * (1 - bias)
            ce_matrix[ce_sidlst[j], ce_sidlst[i]] += jaccard * (1 - bias)
    # Normalize cause-effect matrix
    for i in range(len(sentences)):
        ce_matrix[i] = normalize(ce_matrix[i])
    # Create causal-similarity graph according to causal-similarity weight matrix
    for i in range(len(ce_matrix)):
        for j in range(i, len(ce_matrix)):
            if ce_matrix[i, j] > 0:
                ceg.add_edge(i, j, weight=ce_matrix[i, j])
            if ce_matrix[j, i] > 0:
                ceg.add_edge(j, i, weight=ce_matrix[j, i])
    return ceg


# -- page_rank: using networkx.pagerank() to rank the graph and assign values to idx_s -- #
def Pagerank_CESimGraph_for_CEBias(cesimgraph, sentnum):
    # using pagerank to get sentence-id to sentence-weight dict from causal-similarity graph
    sid_sw_dict = nx.pagerank(cesimgraph)
    # If the graph is empty, i.e., there has no cause-effect links in this paper, do not need to rank sentences.
    if len(sid_sw_dict) == 0:
        return
    # create all sentence weight according to sid_sw_dict
    sentweight = np.zeros(sentnum)
    for sid, sw in sid_sw_dict.items():
        sentweight[sid] = sw
    return normalize(sentweight)


#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestCESimGraph():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\pickle\f0001.txt_1.pk'
    sxptxt = LoadSxptext(pk)
    cesimgraph = MakeCESimSentGraph(sxptxt)
    sent_id_weight_dict = nx.pagerank(cesimgraph)
    print len(sent_id_weight_dict.values())
    print len(sxptxt.sentenceset)
    # idlst = sorted(sent_id_weight_dict.keys())
    # for id in idlst:
    #     print id, sent_id_weight_dict[id]


def TestSimGraph():
    pk = r'E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\pickle\f0001.txt_1.pk'
    sxptxt = LoadSxptext(pk)
    cesimgraph = create_graph(sxptxt)
    sent_id_weight_dict = nx.pagerank(cesimgraph)
    idlst = sorted(sent_id_weight_dict.keys())
    for id in idlst:
        print id, sent_id_weight_dict[id]

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    TestCESimGraph()
    # TestSimGraph()
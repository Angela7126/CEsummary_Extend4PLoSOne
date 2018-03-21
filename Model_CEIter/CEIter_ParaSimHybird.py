# -*- coding: UTF-8 -*-

### Notification:
###     sxpHybirdGraph implement the GS+SubPara model, i.e. combing the GS model with the SubPara model.
### 1. obtain a sentence-to-sentence distance matrix s_s by computing the Jaccard distance of sentence pairs in a paper.
### 2. obtain a PageRank weight vector x using s_s, the iteration function is:
###     (1) x = alpha * x * s_s + alpha * sw * dangling_weights + (1 - alpha) * per
###     (2) x = beta1*x + beta2 * w_s.T * w
###     (3) s = x
###    here:
###         x: the sentence weight vector --
###             in (1) it is first kind of sentence weight obtained from pagerank;
###             in (2) it is combined sentence weight
###         s: the sentence weight vector
###         w: the word weight vector
###         w_s: is the word_sentence matrix
###         alpha: is a constant coefficient, empirically set as 0.85
###         dangling_weights, per: is dangling node vector, default as array(1.0/s_s.shape()[0]).
###         per: is the personal adjusted weight vector, default as array(1.0/s_s.shape()[0]).
###         sw: the summed weight of all dangling nodes in s_s
###         beta1, beta2: is constant coefficients, empirically set as 0.5

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
import networkx as nx
import numpy as np
from sxpPackage import *
from cmyToolkit import *
from cmyConfFuncForRankModels import *

# The default bias for hybrid Para model and SimGraph model
default_bias = 0.5

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class CEIter_ParaSimHybird:
    # remove_stopwords: 0 means with stopwords; 1 means remove stopwords
    def __init__(self, pickle_path, ceopt=default_ceopt, cesim_bias=default_cesim_bias, cebias=default_ceiter,
                 remove_stopwords=default_remove_stopword, iteration_times=default_itertime):
        self.w_s = None
        self.s_p = None
        self.p_c = None
        self.t_p = None
        self.s_t = None
        self.w = []
        self.s = []
        self.p = []
        self.c = []
        self.t = []
        self.idx_w = []
        self.idx_s = []
        self.idx_p = []
        self.idx_c = []
        self.idx_t = []
        self.words = []
        self.times = iteration_times
        self.ceopt = ceopt
        self.cebias = cebias
        self.cesimbias = cesim_bias
        self.remove_stopwords = remove_stopwords
        self.text = LoadSxptext(pickle_path)
        self.s_s = []  # stores a Jaccard distance matrix between sentences
        self.section2sentence_id_list = {}
        self.ranked_sentence = []
        self.mancesimgraph = MakeCESimSentGraph(self.text, "mance", bias=cesim_bias, remove_stopword=remove_stopwords)
        self.syscesimgraph = MakeCESimSentGraph(self.text, "sysce", bias=cesim_bias, remove_stopword=remove_stopwords)

        if remove_stopwords == 0:
            self.get_parameters_with_stopwords()  # assign values to words, w_s, s_p, p_c
        elif remove_stopwords == 1:
            self.get_parameters_without_stopwords()

        w = matrix(random.rand(len(self.words))).T
        s = matrix(random.rand(len(self.text.sentenceset))).T
        self.s_s = MakeSentSentMatrix(self.text.sentenceset, remove_stopwords)
        self.iterationhybird_ceiter(w, s)
        self.rank_weight()  # get idx_w, idx_s, idx_p, idx_c
        self.ranked_sentences, self.section2sentence_id_list = ordered_sentence_id_set(self.text, self.idx_s)


    def get_parameters_with_stopwords(self):
        self.words = self.text.sentence_tfidf.word
        self.w_s = matrix(self.text.s_k.toarray()).T
        self.s_p = matrix(self.text.p_s.toarray()).T
        self.p_c = matrix(self.text.c_p.toarray()).T
        self.t_p = matrix(self.text.p_t.toarray()).T
        self.s_t = matrix(self.text.t_s.toarray()).T
        nw, ns = self.w_s.shape
        n_p, nc = self.p_c.shape
        nt, n_p = self.t_p.shape
        ns, nt = self.s_t.shape
        # print 'nw', nw, 'ns', ns, 'nt', nt, 'np', n_p,  'nc', nc
        self.w = matrix(np.zeros((1, nw), dtype=np.float))
        self.s = matrix(np.zeros((1, ns), dtype=np.float))
        self.p = matrix(np.zeros((1, n_p), dtype=np.float))
        self.c = matrix(np.zeros((1, nc), dtype=np.float))
        self.t = matrix(np.zeros((1, nt), dtype=np.float))

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


    # -- rank_weight_CEBias: get idx_w, idx_s, idx_p, idx_c -- #
    def rank_weight(self):
        self.idx_w = argsort(array(-self.w), axis=0)
        self.idx_p = argsort(array(-self.p), axis=0)
        self.idx_c = argsort(array(-self.c), axis=0)
        self.idx_t = argsort(array(-self.t), axis=0)
        self.idx_s = argsort(array(-self.s), axis=0)

    # -- Get CE sentence * sentence matrix according to opt --
    def GetCEMatrix(self):
        ce_graph = self.mancesimgraph
        if self.ceopt == 'sysce':
            ce_graph = self.syscesimgraph
        ce_matrix = np.zeros((len(self.text.sentenceset), len(self.text.sentenceset)), dtype=np.float)
        for n, nbrs in ce_graph.adjacency_iter():
            for nbr, eattr in nbrs.items():
                ce_matrix[(n, nbr)] = eattr['weight']
        ce_matrix = NormMatrixByRow(np.matrix(ce_matrix))
        return ce_matrix

    def update_sentence_weight_with_ce(self, w, s, ce_s_matrix):
        s = self.w_s.T * w * (1 - self.cebias) + ce_s_matrix * s * self.cebias
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
        sec = self.p_c.T * p
        sec = normalize(sec)
        return sec

    def update_word_weight_bycontext(self, w, s, t,p):
        # w = self.w_s * s + self.w_s * self.s_t * self.t_p * p #this is the mostly used one in previous experiments
        w = self.w_s * s + self.w_s*self.s_t*t + self.w_s * self.s_t * self.t_p * p  # SubPara Model
        w = normalize(w)
        return w

    def iterationhybird_ceiter(self, w, s, bias=default_bias):
        M = self.s_s
        s_num = M.shape[0]
        tol = 1.0e-6
        alpha, max_iter, S_S, x, per, dangling_weights, is_dangling = PreparePageRankMatrix(M, alpha=0.85, max_iter=self.times, p=None, alreadysym=False)
        # alpha is a constant coefficient
        # max_iter is the maximum iteration times
        # S_S is the preprocessed sentence distance matrix
        # x is PageRank weight vector
        # per is the personal adjusted weight vector
        # dangling_weights is the weights vector for dangling nodes in x
        # is_dangling is a 1D array storing all dangling nodes' index
        ce_s_matrix = self.GetCEMatrix()
        for i in range(max_iter):
            # -- update sentence weight --
            xlast = x.copy()  # get last updated x
            sw = sum(xlast[is_dangling])  # sum all dangling nodes weight
            x = alpha * S_S * xlast + alpha * sw * dangling_weights + (1 - alpha) * per  # update x as first kind of sentence weight
            s = self.w_s.T * w  # update s using words weight as second kind of sentence weight
            x = (1 - bias) * x + bias * s  # combine two kinds of sentence weight
            x = x * (1 - self.cebias) + (ce_s_matrix * x) * self.cebias
            s = normalize(x)  # update sentence weight
            # -- update other weight --
            t = self.update_context_weigth(s)
            p = self.update_paragraph_weight_bycontext(t)
            sec = self.update_section_weight(p)
            w = self.update_word_weight_bycontext(w, s, t, p)  # this is the latest one that incorporate context
            # -- if current sentence weight not changed much, regard it have converged and break iteration --
            err = sum(abs(x-xlast))
            if err < s_num * tol:
                break
        # -- assign values to HybridGraph object's attributes ---
        self.w = w
        self.s = s
        self.t = t
        self.p = p
        self.c = sec


#######################################################################################
# ----------------- Functions to Process Matrixs and PageRank Configs --------------- #
#######################################################################################
# ---- FindDanglingNodes: find the dangling nodes index ---- #
# Dangling Node: a node whose degree equal to 0 in a graph
def FindDanglingNodes(M, axis_id=1):
    S = M.sum(axis=axis_id)  # sum each row
    sel = np.where(S == 0)  # if a S[i,0] == 0, means sentence i is not linked to other, it is a dangling node
    return sel[0]  # return dangling sentences' id.

# ---- NormalizeMatrix: normalize each row vector in M ---- #
def NormalizeMatrix(M, axis_id = 1):
    # -- sum each row & assign 1.0 to dangling node --
    # Dangling Node: a node whose degree equal to 0 in a graph
    S = M.sum(axis=axis_id)
    sel = np.where(S==0)
    S[sel] = 1.0
    # -- normalize each row in M --
    rown = M.shape[0]
    nm = M.copy()
    for r in range(rown):
        nm[r, :] = nm[r, :]/S[r]
    return nm

# ---- MakeSymmetricMatrix: change M to a symmetric matrix ---- #
def MakeSymmetricMatrix(M, mode='half'):
    # -- if mode = half, the non-symmetric position will be half of its value --
    if mode == 'half':
        s = (M+M.T)/2.0
    # -- if mode = merg, the non-symmetric position will be the original value --
    if mode == 'merg':
        s = M.T.copy()
        for index, x in np.ndenumerate(s):
            if s[index] == 0:
                s[index] = M[index]
            elif M[index] == 0:
                s[index] = s[index]
            else:
                s[index] = (s[index] + M[index])/2.0
    return s

# ---- MakeAdjacentMatrix: change M to a adjacent matrix ---- #
def MakeAdjacentMatrix(M):
    dm = M.copy()
    sel = np.where(dm > 0.0)
    dm[sel] = 1
    return dm

# ---- PreparePageRankMatrix: prepare all parameters that need in our hybrid-pagerank process ---- #
# Input:
#   1. M: a matrix object storing sentences distance.
#   2. alpha: a constant coefficient, default as  0.85
#   3. max_iter: the maximum iteration times, default as 100
#   4. p: the dangling node vector, default as None
#   5. alreadysym: a bool variable to indicate whether M is a symmetric Matrix
# Output:
#   1. alpha is a constant coefficient
#   2. max_iter is the maximum iteration times
#   3. norm_M is the processed sentence distance matrix
#   4. x is a PageRank node weight vector
#   5. p is the personal adjusted weight vector, 1* s_num
#   6. dangling_weights is the weights vector for all dangling nodes in x, 1* s_num,
#   7. is_dangling is a 1D array storing all dangling nodes' index
def PreparePageRankMatrix(M, alpha=0.85, max_iter=100, p=None, alreadysym=True):
    s_num = M.shape[0]  # s_num record the sentence node in matrix
    # -- prepare adjacent matrix with edge weight--
    if not alreadysym:
        M = MakeSymmetricMatrix(M, mode='merg')  # make it undirected so that it can be used to rank sentence like nx.pagerank
    norm_M = NormalizeMatrix(M, 1)  # normalize M on row vector
    # -- prepare pagerank node weight vector --
    x = matrix(np.ones((s_num, 1), dtype=np.float)*1.0/s_num)
    # -- prepare vectors about dangling node --
    if p is None:
        p = matrix(np.repeat(1.0/s_num, s_num)).T
    dangling_weights = matrix(np.repeat(1.0/s_num, s_num)).T
    is_dangling = FindDanglingNodes(norm_M, axis_id=0)
    return alpha, max_iter, norm_M, x, p, dangling_weights, is_dangling

# ---- MyPageRankMatT: run pagerank only on sentence distance matrix, not involves iteration of paper structure ---- #
def MyPageRankMatT(M,alpha=0.85,max_iter=100, p=None, alreadysym=True):
    alpha, max_iter, S_S, x, per, dangling_weights, is_dangling = PreparePageRankMatrix(M, alpha=alpha, max_iter=max_iter,p=p, alreadysym=alreadysym)
    s_num = M.shape[0]
    tol = 1.0e-6
    for _ in range(max_iter):
        xlast = x.copy()
        sw = sum(xlast.T[is_dangling])
        x = alpha * xlast*S_S + alpha * sw * dangling_weights + (1 - alpha) * per
        err = sum(abs(x-xlast))
        if err < s_num*tol:
            return x, S_S
    return x, S_S

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestParaSimHybridCEIter():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEIter_ParaSimHybird(pk)
    topksent = 10
    ranked_sentences = model.ranked_sentences
    for idx in range(topksent):
        print '----------------'
        print idx, ranked_sentences[idx].sentence_text

def TestRankSentence():
    pk = os.path.join(kg_dir, "pickle", "f0001.txt_1.pk")
    model = CEIter_ParaSimHybird(pk)
    nr, nc = model.s_s.shape
    # -- get sentence similarity by create_graph function and rewrite it in gm matrix --
    g = create_graph(pk)
    gm = matrix(np.zeros((nr, nr), dtype=np.float))
    for i in range(nr):
        for j in g[i]:
            gm[i, j] = g[i][j]['weight']
    # -- check if gm is same to model.s_s --
    print "-------- check difference between matrix and graph -----------"
    for i in range(nr):
        for j in range(nr):
            if gm[i, j] != model.s_s[i, j]:
                if j in g[i]:
                    print i, j, "model.s_s[i, j] =", model.s_s[i, j], "gm[i, j] =", gm[i, j], "gij =",g[i][j]['weight']
                else:
                    print j, 'not in g[%d]' % i, 'but in m[i,j] is', model.s_s[i, j]
    # -- show ranked sentence index only involve sentence distance matrix, without iteration on paper structure --
    r, W1 = MyPageRankMatT(model.s_s, alreadysym=False)
    temp_idx_s = argsort(r.flatten()).tolist()
    temp_idx_s.reverse()
    print "------- only involve s_matrix idx_s: ---------"
    print temp_idx_s
    print "------- check whether W1 is normalized ----------"
    for i, temp in enumerate(array(np.sum(W1, 1)).flatten().tolist()):
        if abs(temp - 1.0) > 1.0e-6:
            print "%d row is not normalized," %i, temp
    # -- show ranked sentence index combine sentence distance matrix and iteration on paper structure --
    print " ------ my model's idx_s ------------ "
    print model.idx_s.tolist()
    # -- preprocess matrix --
    gm = MakeSymmetricMatrix(gm, mode='merg')
    gm = NormalizeMatrix(gm, 1)
    norm_g = MakeGraphObjectFromMatrix(gm)
    # -- check the preprocessed matrix is normalized and is same to W1 --
    print "------- check whether gm is normalized ----------"
    for i, temp in enumerate(array(np.sum(gm, 1)).flatten().tolist()):
        if abs(temp - 1.0) > 1.0e-6:
            print "%d row is not normalized," %i, temp
    print "------ check difference between gm and W1 -------"
    for i in range(nr):
        for j in range(nr):
            if gm[i, j] != W1[i, j]:
                print i, j, "gm[i, j] =", gm[i, j], "W1[i, j] =", W1[i, j]
    # -- get and show networkx model's pagerank result --
    pr = nx.pagerank(norm_g)
    print " ------ networkx's idx_s ------------ "
    pageweight = [pageweight for node, pageweight in pr.items()]
    g_idx_s = argsort(array(pageweight), axis=0).tolist()
    g_idx_s.reverse()
    print g_idx_s


def TestPageRankMatrix():
    # -- create matrix and preprocess it --
    # M = matrix([[1.0,1.0,0.0,1.0], [1.0,0.0,0.0,0.0], [0.0,0.0,0.0,0.0], [1.0,1.0,0.0,1.0]])
    M = matrix(np.random.rand(10, 10))
    print '--------- matrix m -----------'
    print M
    print '---------- symmetrized m -----------'
    M = MakeSymmetricMatrix(M, mode='merg')
    print M
    print '---------- normalized matrix -------------'
    M = NormalizeMatrix(M)
    print M
    nr, nc = M.shape
    # -- create a sentence distance graph from this matrix, and check whether it is same with matrix --
    g = MakeGraphObjectFromMatrix(M)
    gc = len(g)
    print "row_num =", nr, "column_num =", nc, "node_num in graph =", gc
    for i in range(nr):
        for j in g[i]:
            gij = g[i][j]
            if M[i, j] != gij['weight']:
                print i, j, M[i, j], gij['weight']
    # -- run networkx model's pagerank on sentence distance graph --
    v = nx.pagerank(g)
    print '---- vpagerank -----'
    print v.values()
    # -- run our rewrite pagerank on sentence adjacent matrix --
    # we hope it will be the equal implementation of nx.pagerank
    v = MyPageRankMatT(M)
    print '-------- vmypagerank ------------'
    print v[0]

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    # TestPageRankMatrix()
    # TestRankSentence()
    TestParaSimHybridCEIter()
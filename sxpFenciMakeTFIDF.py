# -------------------------------------------------------------------------------
# Name:        sxpFenciMakeTFIDF
# Purpose:
#
# Author:      sunxp
#
# Created:     07-04-2015
# Copyright:   (c) sunxp 2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import jieba
import re
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.sparse import csr_matrix
from sxpPackage import sxpTFIDF

#######################################################################################
# ---------------------- Some string pre-processing functions ----------------------- #
#######################################################################################
# ---- This function checks whether a pieces of text is a "mark" (mainly punctuations) ---- #
def isMark(mstr):
    seg = mstr.decode('utf-8')
    if seg ==u'' or seg == u'\r' or seg == u'\n' or seg == u'\t' or seg == u'=' or seg == u'[' or seg == u']' or seg == u'(' or seg == u')':
        return True
    if seg ==u'*' or seg == u':' or seg == u'.' or seg == u',' or seg == u'!' or seg == u'{' or seg == u'}' or seg == u'<' or seg == u'>':
        return True
    if seg == u'~' or seg == u'@' or seg == u'#' or seg == u'$' or seg == u'%' or seg == u'^' or seg == u'&' or seg == u';' or seg == u'?':
        return True
    if seg == u'\'' or seg == u'\"' or seg == u'-' or seg == u'+' or seg == u'\\' or seg == u'/' or seg == u'|' or seg == u'`':
        return True
    if seg == u'\'' or seg == u'\"' or seg == u'-' or seg == u'+' or seg == u'\\' or seg == u'/' or seg == u'|' or seg == u'`':
        return True
    if seg == u'，' or seg == u'。' or seg == u'：' or seg == u'；' or seg == u'（' or seg == u'）' or seg == u'“' or seg == u'”':
        return True
    if seg == u'【' or seg == u'】' or seg == u'——' or seg == u'？' or seg == u'！' or seg == u'‘' or seg == u'《' or seg == u'》':
        return True
    if seg == u'…' or seg == u'、':
        return True
    return False

# ---- Function SegStr: ---- #
# 1. splits the input 'strcontent' into words, ' ', and punctuation.
# 2. only encodes segments that are not marks (see "IsMark") and also contain words into utf-8, and appends them into result = []
# 3. return "result" as the final output
def SegStrSet(strcontent):
    seg_list = jieba.cut(strcontent, cut_all=False)
    result = []
    for seg in seg_list:
        seg = ''.join(seg.split()).strip()  # delete ' ' in seg
        useg = seg.encode('utf-8')  # encode seg into utf-8
        r = re.search('\w+', seg)  # check whether seg contains words
        if not isMark(useg) and not r:  # if useg is not a mark and it contains words
            result.append(useg)
    return result

# ---- Function SegStr: ---- #
# 1. splits the input 'strcontent' into words, ' ', and punctuation.
# 2. only encodes segments that are not marks (see "IsMark") into utf-8, and append them into result = []
# 3. join the segments in result with ' ' together
def SegStr(strcontent):
    seg_list = jieba.cut(strcontent, cut_all=False)
    result = []
    for seg in seg_list:
        useg = seg.encode('utf-8')
        if not isMark(useg):
           result.append(seg.encode("utf-8"))
    segstr = ' '.join(result)
    if isinstance(segstr,unicode):
        segstr = segstr.decode('utf-8')
    return segstr

# ---- Function SegStrComplex: ---- #
# 1. splits the input 'strcontent' into words, ' ', and punctuation.
# 2. encodes each of them into utf-8.
# 3. then stringing them together, and add a " " at the beginning.
#
# for example: strcontent = "Next, try stringing words together."
#   1. strcontent is split as seg_list = ["Next", ",", " ", "try", " ", "stringing", " ", "words", " ", "together", "."]
#   2. encode each piece in seg_list into utf-8
#   3. string them up as strspace = u" Next, try stringing words together"
def SegStrComplex(strcontent):
    seg_list = jieba.cut(strcontent, cut_all=False)
    strspace= ' '
    for seg in seg_list:
        useg = seg.encode('utf-8')
        strspace = strspace + useg
    if isinstance(strspace,unicode):
        strspace = strspace.decode('utf-8')
    return strspace

#######################################################################################
# ------------------------------ Make TFIDF for corpus ------------------------------ #
#######################################################################################
def MakeTFIDFForCorpus(docset):
    print 'begin to load and fenci file'
    corpus = []
    sxptfidf = sxpTFIDF()

    # ---- process each doc content and append them into corpus ----
    for docstr in docset:
        segcontent = SegStrComplex(docstr)
        corpus.append(segcontent)

    # ---- MakeTFIDF ----
    print 'begin to make tfidf'
    # 1. Convert text documents to a matrix of token counts
    # "fit_transform" Learn the vocabulary dictionary and return term-document matrix.
    # "get_feature_names()" return tokens list in corpus
    vectorizer = CountVectorizer(analyzer="word",
                             tokenizer=None,
                             preprocessor=None,
                             token_pattern=u'(?u)\\b\S+\\b',
                             stop_words=None)
    sxptfidf.ct = vectorizer.fit_transform(corpus)  # get term-doc matrix and store in sxptfidf.ct
    sxptfidf.word = vectorizer.get_feature_names()  # get tokens list and store in sxptfidf.word
    # for w in sxptfidf.word:
    #   print w
    # 2. Transform a count matrix to a normalized tf or tf-idf representation
    # "fit_transform" take term-doc matrix as input and calculate the tf-idf matrix
    transformer = TfidfTransformer()
    sxptfidf.tfidf = transformer.fit_transform(sxptfidf.ct)  # get tf-idf matrix and store in sxptfidf.tfidf
    # 3.Transform a crs_matrix tfidf value to array
    sxptfidf.weight = sxptfidf.tfidf.toarray()
    print 'finished'
    return sxptfidf

#######################################################################################
# -------------------------------- Some test functions ------------------------------ #
#######################################################################################
def TestTFIDF():
    docset = [u'hello this is a U.S. test, and we are 你好 going to  let the test 100 run', u'we can make a simple analysis in this work']
    seg = SegStrComplex(docset[0])
    print seg
    sxptfidf = MakeTFIDFForCorpus(docset)
    kn = sxptfidf.GetKeywordCount()
    for i in range(kn):
        print sxptfidf.GetKeyword(i)
        #print type(sxptfidf.GetCTCol(i))

def TestNumpyMatrix():
    a = np.eye(5, 5)
    a[0,3]=2
    a[3,0]=2
    a[4,2]=2
    a[3,2]=2

    a = csr_matrix(a)
    print a
    dense = np.asarray(a.todense())
    column = np.asarray(a.getcol(2).todense()).reshape(-1)

    print "dense"
    # operations on full dense matrix
    print "1"
    print csr_matrix( np.vstack([ line for line in dense if line[2] == 1 ]) )
    print "2"
    print csr_matrix( np.vstack([ line for line in dense if line[2] == 0 ]) )

    print "sparse"
    # Operations on sparse matrix
    result1 = []
    result2 = []
    for irow in range(a.shape[0]):
        if column[irow] == 1:
            [ result1.append( (irow,indice) ) for indice in a[irow].indices   ]
        else :
            [ result2.append( (irow,indice) ) for indice in a[irow].indices   ]

    print result1,result2

    result3 =[]
    print 'my sparse visit'
    for irow in range(a.shape[0]):
        [result3.append((irow, indice)) for indice in a[irow].indices]
    print result3
    print 'my sparse visit 1'
    a = np.matrix('1 2; 3 4 ; 5 6')
    a = csr_matrix(a)
    print a
    b = a.getrow(1)
    b = a.getcol(1)
    nzero = b.nonzero()
    r = nzero[0]
    c = nzero[1]
    print r
    print c

    for i in range(len(r)):
        x = r[i]
        y = c[i]
        print a[x, y]

#######################################################################################
# -------------------------------- Main functions ----------------------------------- #
#######################################################################################
def main():
    TestTFIDF()

if __name__ == '__main__':
    main()
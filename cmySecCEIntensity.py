__author__ = 'sxp'
# -*- coding: UTF-8 -*-
# --------------------------------------------------------------------------------------------------------
# Name:        cmySecCEIntensity
# Purpose:     1. Define cmySecCE class
# ---------------------------------------------------------------------------------------------------------

from sxpPackage import *
from cmyToolkit import *
import sxpProcessParaText
import sxpFenciMakeTFIDF
import networkx as nx
import copy
from scipy import *
from scipy.sparse import csr_matrix
import numpy as np

#######################################################################################
# ------------------------------------- Classes ------------------------------------- #
#######################################################################################
class cmySecCE:
    sec_id_str = ''
    sec_id_lst = []
    level = 1
    t_type = 'section'
    whole_text = ''
    sec_title = ''
    abstract = ''
    conclusion = ''
    section_list = []
    paraset = []
    context_set = []
    sentenceset = []
    keycount = None
    para_tfidf = None
    sentence_tfidf = None
    c_p = None
    p_s = None
    s_k = None
    t_s = None  # context - sentence
    p_t = None  # paragraph - context
    c_c = None
    sec_id_dict = {}   # dictionary object that map original section id to cmySecCE's section id
    para_id_dict = {}  # dictionary object that map original para id to cmySecCE's para id
    cont_id_dict = {}  # dictionary object that map original context id to cmySecCE's context id
    sent_id_dict = {}  # dictionary object that map original sentence id to cmySecCE's sentence id
    mance_id_dict = {}  # map mance_id in sxpText2 to mance_id in current cmySecCE
    sysce_id_dict = {}  # map sysce_id in sxpText2 to sysce_id in current cmySecCE
    ce_s_man = None  # sent-sent matrix, which store manual causal links' sentences network's edge weight
    ce_s_sys = None  # sent-sent matrix, which store automatic causal links' sentences network's edge weight
    ce_man = None  # cause-effect sentences' weight which calculated by pagerank
    ce_sys = None  # cause-effect sentences' weight which calculated by pagerank
    man_CE_list = []  # a list: stores manual labeled cause-effect links
    mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
    sys_CE_list = []  # a list: stores pattern matched cause-effect links
    sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id

    # -------------------------------------------------------------------------------------------------------------
    #   sxptxt: a sxpText2 object.
    #   sec_id_str: is the section str for current section, such as s1
    #   sec_id_lst: sec_id_lst is a list that store the section's and subsections' id that belong to current section
    #   para_id: paragraphs' id list that belongs to this section
    #   cont_id: contexts' id list belonging to this section
    #   sent_id: sentences' id list belongint to this section
    # -------------------------------------------------------------------------------------------------------------
    def __init__(self, sxptxt, sec_id_str, sec_id, para_id, cont_id, sent_id, mance_id, sysce_id):
        # --------------------------------------------- Initialize ------------------------------------------------
        self.sec_id_dict = {}  # dictionary object that map original section id to cmySecCE's section id
        self.para_id_dict = {}  # dictionary object that map original para id to cmySecCE's para id
        self.cont_id_dict = {}  # dictionary object that map original context id to cmySecCE's context id
        self.sent_id_dict = {}  # dictionary object that map original sentence id to cmySecCE's sentence id
        self.mance_id_dict = {}  # map mance_id in sxpText2 to mance_id in current cmySecCE
        self.sysce_id_dict = {}  # map sysce_id in sxpText2 to sysce_id in current cmySecCE
        self.mance_sent_id_dict = {}  # a dict: map a sentence id to a manual labeled ce link id
        self.sysce_sent_id_dict = {}  # a dict: map a sentence id to a pattern matched ce link id
        self.man_CE_list = []
        self.sys_CE_list = []
        self.sentenceset = []
        self.context_set = []
        self.paraset = []
        self.section_list = []
        self.whole_text = ""
        self.sec_title = ""
        self.abstract = ""
        self.conclusion = ""

        man_CE_list = sxptxt.man_CE_list[:]
        sys_CE_list = sxptxt.sys_CE_list[:]
        sentenceset = sxptxt.sentenceset[:]
        context_set = sxptxt.context_set[:]
        paraset = sxptxt.paraset[:]
        section_list = sxptxt.section_list[:]

        # ------------------------------------- id mapping dictionary objects --------------------------------------
        for idx, sid in enumerate(sent_id):
            self.sent_id_dict[sid] = idx
        for idx, tid in enumerate(cont_id):
            self.cont_id_dict[tid] = idx
        for idx, pid in enumerate(para_id):
            self.para_id_dict[pid] = idx
        for idx, cid in enumerate(sec_id):
            self.sec_id_dict[cid] = idx
        for idx, manid in enumerate(mance_id):
            self.mance_id_dict[manid] = idx
        for idx, sysid in enumerate(sysce_id):
            self.sysce_id_dict[sysid] = idx

        print "---------- Original id list ------------"
        print "sent id:", sent_id
        print "cont id:", cont_id
        print "para id:", para_id
        print "sec id:", sec_id
        print "mance_id:", mance_id
        print "sysce_id:", sysce_id
        print "------- Check Mapping id dict ----------"
        print "sent id dict:", self.sent_id_dict.items()
        print "cont id dict:", self.cont_id_dict.items()
        print "para id dict:", self.para_id_dict.items()
        print "sec id dict:", self.sec_id_dict.items()
        print "mance_id dict:", self.mance_id_dict.items()
        print "sysce_id dict:", self.sysce_id_dict.items()
        print "----------------------------------------"

        print "..... Create Man_CE_List ...."
        for manid in mance_id:
            tempmance = man_CE_list[manid]
            tempmance.manCEid = self.mance_id_dict[manid]
            for idx, sid in enumerate(tempmance.Staglst):
                newsid = self.sent_id_dict[sid]
                tempmance.Staglst[idx] = newsid
                if newsid not in self.mance_sent_id_dict.keys():
                    self.mance_sent_id_dict[newsid] = [tempmance.manCEid]
                elif tempmance.manCEid not in self.mance_sent_id_dict[newsid]:
                    self.mance_sent_id_dict[newsid].append(tempmance.manCEid)
            self.man_CE_list.append(tempmance)

        print ".... Create sys_CE_List ...."
        for sysid in sysce_id:
            tempsysce = sys_CE_list[sysid]
            tempsysce.sysCEid = self.sysce_id_dict[sysid]
            for idx,sid in enumerate(tempsysce.Staglst):
                newsid = self.sent_id_dict[sid]
                tempsysce.Staglst[idx] = newsid
                if newsid not in self.sysce_sent_id_dict.keys():
                    self.sysce_sent_id_dict[newsid] = [tempsysce.sysCEid]
                elif tempsysce.sysCEid not in self.sysce_sent_id_dict[newsid]:
                    self.sysce_sent_id_dict[newsid].append(tempsysce.sysCEid)
            self.sys_CE_list.append(tempsysce)

        print ".... Creat sentenceset ...."
        for sid in sent_id:
            tempsent = sentenceset[sid]
            tempsent.id = self.sent_id_dict[sid]
            tempsent.id_para = self.para_id_dict[tempsent.id_para]
            tempsent.id_sec = self.sec_id_dict[tempsent.id_sec]
            tempsent.manCEidlst.sort()
            tempsent.sysCEidlst.sort()
            for idx, manid in enumerate(tempsent.manCEidlst):
                if manid not in mance_id:
                    break
                tempsent.manCEidlst[idx] = self.mance_id_dict[manid]
            for idx, sysid in enumerate(tempsent.sysCEidlst):
                if sysid not in sysce_id:
                    break
                tempsent.sysCEidlst[idx] = self.sysce_id_dict[sysid]
            self.sentenceset.append(tempsent)

        print ".... Creat context_set ...."
        for tid in cont_id:
            tempcont = context_set[tid]
            tempcont.id = self.cont_id_dict[tid]
            tempcont.id_para = self.para_id_dict[tempcont.id_para]
            tempcont.id_sec = self.sec_id_dict[tempcont.id_sec]
            self.context_set.append(tempcont)

        print ".... Creat paraset ...."
        for pid in para_id:
            temppara = paraset[pid]
            temppara.id = self.para_id_dict[pid]
            temppara.id_sec = self.sec_id_dict[temppara.id_sec]
            self.paraset.append(temppara)

        print ".... Creat sectionset ...."
        for cid in sec_id:
            tempsection = section_list[cid]
            tempsection.id = self.sec_id_dict[cid]
            self.section_list.append(tempsection)

        # --------------------------------------- section text and titile ---------------------------------------------
        self.sec_id_str = sec_id_str
        self.sec_id_lst = sec_id

        print ".... Get Whole_text ...."
        for sent in self.sentenceset:
            self.whole_text = self.whole_text + ' ' + sent.sentence_text
        self.whole_text = self.whole_text.strip()

        print ".... Get sec_title ...."
        for sec in self.section_list:
            if len(self.sec_title) == 0:
                self.sec_title = sec.title
            else:
                self.sec_title = self.sec_title + '\n' + sec.title

        # -------------------------------------- Keywords and tfidf value -----------------------------------------
        print ".... Get Keywords ...."
        self.keycount = sxpProcessParaText.ExtractKeyCount(self.whole_text)  # stores the "sxpTextCount" object for current paper

        print ".... Get para_tfidf ...."
        para_textset = []
        for para in self.paraset:
            para_textset.append(para.para_text)
        self.para_tfidf = sxpFenciMakeTFIDF.MakeTFIDFForCorpus(para_textset) # stores the TFIDF matrix on paragraph level

        print ".... Get sent_tfidf ...."
        sent_textset = []
        for sent in self.sentenceset:
            sent_textset.append(sent.sentence_text)
        self.sentence_tfidf = sxpFenciMakeTFIDF.MakeTFIDFForCorpus(sent_textset)  # stores the TFIDF matrix on sentence level

        # ---------------------------------------- Matrix ---------------------------------------------
        # section-section matrix (focus on the belongingness between section, subsection, subsubsection)
        print ".... Create C_C matrix ...."
        self.c_c = csr_matrix((len(sec_id), len(sec_id)), dtype=float64)
        for cid in sec_id:
            for cjd in sec_id:
                ccid = self.sec_id_dict[cid]
                ccjd = self.sec_id_dict[cjd]
                if ccid == ccjd:
                    self.c_c[ccid, ccjd] = 1.0
                else:
                    self.c_c[ccid, ccjd] = sxptxt.c_c[cid, cjd]
                    self.c_c[ccjd, ccid] = sxptxt.c_c[cjd, cid]

        print ".... Create C_P matrix ...."
        self.c_p = csr_matrix((len(sec_id), len(para_id)), dtype=float64)  # section-paragraph matrix
        for para in self.paraset:
            c = para.id_sec
            p = para.id
            self.c_p[c, p] = 1.0

        print ".... Create P_S matrix ...."
        self.p_s = csr_matrix((len(para_id), len(sent_id)), dtype=float64)  # paragraph-sentence matrix
        for sent in self.sentenceset:
            p = sent.id_para
            s = sent.id
            self.p_s[p, s] = 1.0

        print ".... Create S_K matrix ...."
        self.s_k = csr_matrix(self.sentence_tfidf.tfidf)  # sentence-keyword matrix

        print ".... Create P_T matrix and T_S matrix ...."
        self.p_t = csr_matrix((len(para_id), len(cont_id)), dtype=float64)  # paragraph-context matrix
        self.t_s = csr_matrix((len(cont_id), len(sent_id)), dtype=float64)  # context-sentence matrix
        for para in self.paraset:
            p = para.id
            for cont in para.context_set:
                t = cont.id
                self.p_t[p, t] = 1.0
                for sent in cont.context_sent:
                    s = sent.id
                    self.t_s[t, s] = 1.0

        # -------------------------------- Cause-effect graph and sentences' weight ------------------------------------
        print ".... Create Causal-Similarity Graphs ...."
        self.ce_s_man = self.MakeCESentMatrix('mance')  # sent-sent matrix, manual causal links' causal-similarity graph
        self.ce_s_sys = self.MakeCESentMatrix('sysce')  # sent-sent matrix, automatic causal links' causal-sim graph
        self.ce_man = nx.pagerank(self.ce_s_man)  # cause-effect sentences' weight which calculated by pagerank
        self.ce_sys = nx.pagerank(self.ce_s_sys)  # cause-effect sentences' weight which calculated by pagerank

    # -- normalize a vector -- #
    def normalize(self, w):
        if sum(w) <= 0:
            return w
        w = w / sum(w)
        return w

    # ---- get sentence_sentence jaccard similarity matrix self.s_s ----
    def MakeCESentMatrix(self, opt):
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
                    ce_matrix[ce.Staglst[i], ce.Staglst[j]] = 0.5
                    ce_matrix[ce.Staglst[j], ce.Staglst[i]] = 0.5
        for i in range(len(ce_sidlst)):
            for j in range(i + 1, len(ce_sidlst)):
                si_txt = sentences[ce_sidlst[i]].sentence_text
                sj_txt = sentences[ce_sidlst[j]].sentence_text
                jaccard = jaccard_similarity(si_txt, sj_txt)
                ce_matrix[ce_sidlst[i], ce_sidlst[j]] += jaccard
                ce_matrix[ce_sidlst[j], ce_sidlst[i]] += jaccard
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
# --------------------------- Some demonstration functions -------------------------- #
#######################################################################################
def ShowCmySecSentLst(sentenceset):
    for sent in sentenceset:
        print "\t\t\t", "sent_id =", sent.id
        print "\t\t\t", "sent_paraid =", sent.id_para
        print "\t\t\t", "sent_secid =", sent.id_sec
        print "\t\t\t", "sent_text =", sent.sentence_text
        print "\t\t\t", "sysCEidlst =", sent.sysCEidlst, "manCEidlst =", sent.manCEidlst
        print "\t\t\t+++++++++++++++++++++++++++++++++++++++++++++"


def ShowCmySecContextLst(context_set):
    for ctxt in context_set:
        print '\t\t', "cont_id =", ctxt.id
        print '\t\t', "cont_paraid =", ctxt.id_para
        print '\t\t', "cont_secid =", ctxt.id_sec
        print '\t\t', "cont_text =", ctxt.context_txt
        print '\t\t\t+++++++++++++++ sent list:', len(ctxt.context_sent), '+++++++++++++++++++'
        ShowCmySecSentLst(ctxt.context_sent)
        print "\t\t..............................................."


def ShowCmySecParaLst(paraset):
    for p in paraset:
        print "\t-------------------------------------------------"
        print '\t', "para_id =", p.id
        print '\t', "para_secid =", p.id_sec
        print '\t', "para_text =", p.para_text
        print '\t', "para_tuple =", p.para_tuple
        print '\t\t.................. context list:', len(p.context_set), '....................'
        ShowCmySecContextLst(p.context_set)
        # print '\t\t\t++++++++++++++++++ sent list:', len(p.sentenceset), '+++++++++++++++++++++++'
        # ShowCmySecSentLst(p.sentenceset)


def ShowCmySecSecLst(section_list):
    print "======================================================"
    print "Section List:", len(section_list)
    for sec in section_list:
        print "\t-------------------------------------------------"
        print '\t', "sec_id =", sec.id
        print '\t', "id_str =", sec.id_str
        print '\t', "title =", sec.title
        print '\t', "level =", sec.level
        print '\t', "t_type =", sec.t_type
        print '\t', "id_set =", sec.id_set
    print "======================================================"
    print


def ShowCmySecCEInfo(SecCE):
    print "************************************************************"
    print "SecIDstr = ", SecCE.sec_id_str
    print "SecIDlst =", SecCE.sec_id_lst
    print "Whole text =", SecCE.whole_text
    print "Sectitle =", SecCE.sec_title
    print "Abstract =", SecCE.abstract
    print "Conclusion =", SecCE.conclusion
    print "************************************************************"
    print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's section id to cmySecCE's section id"
    # for itm in SecCE.sec_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # ShowCmySecSecLst(SecCE.section_list)
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's para id to cmySecCE's para id"
    # for itm in SecCE.para_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "======================================================"
    # print "Paraset List:", len(SecCE.paraset)
    # ShowCmySecParaLst(SecCE.paraset)
    # print "======================================================"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's cont id to cmySecCE's cont id"
    # for itm in SecCE.cont_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "======================================================"
    # print "Context set:", len(SecCE.context_set)
    # ShowCmySecContextLst(SecCE.context_set)
    # print "======================================================"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's sent id to cmySecCE's sent id"
    # for itm in SecCE.sent_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "======================================================"
    # print "Sentence set:", len(SecCE.sentenceset)
    # ShowCmySecSentLst(SecCE.sentenceset)
    # print "======================================================"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's mance id to cmySecCE's mance id"
    # for itm in SecCE.mance_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping cmySecCE's sent id to cmySecCE's mance id", len(SecCE.mance_sent_id_dict)
    # for itms in SecCE.mance_sent_id_dict.items():
    #     print itms
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "======================================================"
    # print "Man CE List:", len(SecCE.man_CE_list)
    # for mance in SecCE.man_CE_list:
    #     print "\t-------------------------------------------------"
    #     print "\tman_ce_id", mance.manCEid
    #     print "\tpattern", mance.main_token
    #     print "\tsent id lst", mance.Staglst
    # print "======================================================"
    # print
    #
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    print "ManCE sentence weight list:"
    for sw in sorted(SecCE.ce_man.items(), key=lambda d: d[1], reverse=True):
        print "\t......................................."
        print '\t', SecCE.sentenceset[sw[0]].sentence_text
        print '\t', sw[1]
        print "\t......................................."
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping sxptxt's sysce id to cmySecCE's sysce id"
    # for itm in SecCE.sysce_id_dict.items():
    #     print itm
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "Mapping cmySecCE's sent id to cmySecCE's sysce id"
    # for itms in SecCE.sysce_sent_id_dict.items():
    #     print itms
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print
    #
    # print "======================================================"
    # print "Sys CE List:", len(SecCE.sysce_CE_list)
    # for sysce in SecCE.sysce_CE_list:
    #     print "\t-------------------------------------------------"
    #     print "\tsys_ce_id", sysce.sysCEid
    #     print "\tpattern", sysce.pt
    #     print "\tsent id lst", sysce.Staglst
    # print "======================================================"
    # print
    #
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    # print "SysCE sentence weight list:"
    # for sw in sorted(SecCE.ce_sys.items(), key=lambda d: d[1], reverse=True):
    #     print "\t......................................."
    #     print '\t', SecCE.sentenceset[sw[0]].sentence_text
    #     print '\t', sw[1]
    #     print "\t......................................."
    # print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    #
    # print "p_t matrix:"
    # print SecCE.p_t
    # print "t_s matrix:"
    # print SecCE.t_s
    # print "c_c matrix:"
    # for row in range(len(SecCE.section_list)):
    #     print SecCE.section_list[row].title
    #     for col in SecCE.c_c[row].indices:
    #         print "\t", SecCE.section_list[col].title


#######################################################################################
# ------------------ Create cmySecCE object for each section in a paper ------------- #
#######################################################################################
def CreateSecCEObject(sxptxt):
    secstr_lst = []
    cmySecCE_lst = []

    secstr_secid_dict = {}
    for itm in sxptxt.section_id_dict.items():
        tempstr = itm[0].split('.')
        if secstr_secid_dict.has_key(tempstr[0]):
            secstr_secid_dict[tempstr[0]].append(itm[1])
        else:
            secstr_secid_dict[tempstr[0]] = [itm[1]]
            secstr_lst.append(tempstr[0])

    for secstr in secstr_lst:
        if secstr_secid_dict.has_key(secstr):
            secstr_secid_dict[secstr].sort()

    secstr_paraid_dict = {}
    for para in sxptxt.paraset:
        tempstr = sxptxt.section_list[para.id_sec].id_str.split('.')
        if secstr_paraid_dict.has_key(tempstr[0]):
            secstr_paraid_dict[tempstr[0]].append(para.id)
        else:
            secstr_paraid_dict[tempstr[0]] = [para.id]
    for secstr in secstr_lst:
        if secstr_paraid_dict.has_key(secstr):
            secstr_paraid_dict[secstr].sort()
            # print secstr, secstr_paraid_dict[secstr]

    secstr_contid_dict = {}
    for cont in sxptxt.context_set:
        tempstr = sxptxt.section_list[cont.id_sec].id_str.split('.')
        if secstr_contid_dict.has_key(tempstr[0]):
            secstr_contid_dict[tempstr[0]].append(cont.id)
        else:
            secstr_contid_dict[tempstr[0]] = [cont.id]
    for secstr in secstr_lst:
        if secstr_contid_dict.has_key(secstr):
            secstr_contid_dict[secstr].sort()
            # print secstr, secstr_contid_dict[secstr]

    secstr_sentid_dict = {}
    for sent in sxptxt.sentenceset:
        tempstr = sxptxt.section_list[sent.id_sec].id_str.split('.')
        if secstr_sentid_dict.has_key(tempstr[0]):
            secstr_sentid_dict[tempstr[0]].append(sent.id)
        else:
            secstr_sentid_dict[tempstr[0]] = [sent.id]
    for secstr in secstr_lst:
        if secstr_sentid_dict.has_key(secstr):
            secstr_sentid_dict[secstr].sort()
            # print secstr, secstr_sentid_dict[secstr]

    secstr_manceid_dict = {}
    for mance in sxptxt.man_CE_list:
        sid_l = mance.Staglst[0]
        sid_r = mance.Staglst[-1]
        cid_l = sxptxt.sentenceset[sid_l].id_sec
        cid_r = sxptxt.sentenceset[sid_r].id_sec
        secstr_l = sxptxt.section_list[cid_l].id_str.split('.')[0]
        secstr_r = sxptxt.section_list[cid_r].id_str.split('.')[0]
        if secstr_l != secstr_r:
            continue
        if secstr_manceid_dict.has_key(secstr_l):
            secstr_manceid_dict[secstr_l].append(mance.manCEid)
        else:
            secstr_manceid_dict[secstr_l] = [mance.manCEid]
    for secstr in secstr_lst:
        if secstr_manceid_dict.has_key(secstr):
            secstr_manceid_dict[secstr].sort()

    secstr_sysceid_dict = {}
    for sysce in sxptxt.sys_CE_list:
        sid_l = sysce.Staglst[0]
        sid_r = sysce.Staglst[-1]
        cid_l = sxptxt.sentenceset[sid_l].id_sec
        cid_r = sxptxt.sentenceset[sid_r].id_sec
        secstr_l = sxptxt.section_list[cid_l].id_str.split('.')[0]
        secstr_r = sxptxt.section_list[cid_r].id_str.split('.')[0]
        if secstr_l != secstr_r:
            continue
        if secstr_sysceid_dict.has_key(secstr_l):
            secstr_sysceid_dict[secstr_l].append(sysce.sysCEid)
        else:
            secstr_sysceid_dict[secstr_l] = [sysce.sysCEid]
    for secstr in secstr_lst:
        if secstr_sysceid_dict.has_key(secstr):
            secstr_sysceid_dict[secstr].sort()

    for secstr in secstr_lst:
        if not secstr_secid_dict.has_key(secstr):
            continue
        if not secstr_paraid_dict.has_key(secstr):
            continue
        if not secstr_contid_dict.has_key(secstr):
            continue
        if not secstr_sentid_dict.has_key(secstr):
            continue
        
        print
        print "\t\t=========== Processing section:", secstr, "============="
        sec_id = secstr_secid_dict[secstr]
        para_id = secstr_paraid_dict[secstr]
        cont_id = secstr_contid_dict[secstr]
        sent_id = secstr_sentid_dict[secstr]
        if secstr_manceid_dict.has_key(secstr):
            mance_id = secstr_manceid_dict[secstr]
        else:
            mance_id = []
        if secstr_sysceid_dict.has_key(secstr):
            sysce_id = secstr_sysceid_dict[secstr]
        else:
            sysce_id = []
        secce = cmySecCE(sxptxt, secstr, sec_id, para_id, cont_id, sent_id, mance_id, sysce_id)
        cmySecCE_lst.append(secce)
    print "\t\t ==================================================="
    return cmySecCE_lst, secstr_lst


def KGpk2SecCE(kg_fname_lst):
    fname_secstr_dict = {}
    for kgfn in kg_fname_lst:
        print "********** Current Processing file:", kgfn, "************"
        print "Load pk file ..."
        sxptxtfp = os.path.join(kg_dir, 'pickle', kgfn+'_2.pk')
        sxptxt = LoadSxptext(sxptxtfp)
        print "Create SecCE objects ..."
        (cmySecCE_lst, secstr_lst) = CreateSecCEObject(sxptxt)
        print
        print "~~~~~~~~~~~~~~~~~~~~ Dump SecCE objects into pickle files ~~~~~~~~~~~~~~~~~~~~"
        for secce in cmySecCE_lst:
            print "Dumping SecCE pickle for section:", secce.sec_id_str
            seccefp = os.path.join(kg_dir, 'pickle_SecCE', kgfn+'.'+secce.sec_id_str+'.pk')
            StoreSxptext(secce, seccefp)
        fname_secstr_dict[kgfn] = secstr_lst
    fname_secstrlst_dict_fp = os.path.join(DICpkdir, 'KGFname_SecStrlst_dict.pk')
    StoreSxptext(fname_secstr_dict, fname_secstrlst_dict_fp)


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
if __name__ == "__main__":
    pk_path = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_SecCE_temp\f0002.txt.abstract.pk'
    SecCE = LoadSxptext(pk_path)
    ShowCmySecCEInfo(SecCE)
    # kg_fname_lst = ['f0001.txt', 'f0002.txt', 'f0003.txt', 'f0014.txt', 'f0015.txt',
    #                 'f0016.txt', 'f0027.txt', 'f0028.txt', 'f0029.txt']
    # KGpk2SecCE(kg_fname_lst)
    # fpath = r"E:\Programs\Eclipse\CE_relation\CEsummary\kg\pickle_SecCE\f0001.txt_abstract.pk"
    # secce = LoadSxptext(fpath)
    # print secce.c_c
    #
    # for mance in sxptxt.man_CE_list:
    #     print mance.Staglst
    #     print mance.manCEid
    #     print mance.main_token
    #     print mance.cw_span
    #     print mance.ew_span
    #     print "----------------------"
    # CreateSecCEObject(sxptxt)
    # # for sent in sxptxt.sentenceset:
    # #     print dir(sent)
    # secstrid = sxptxt.section_id_dict.items()
    # secstrid.sort()
    # for ce in secstrid:
    #     print ce[0].split('.')
        # print sxptxt.whole_sectitle
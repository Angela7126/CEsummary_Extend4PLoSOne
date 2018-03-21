# -------------------------------------------------------------------------------
# Name:        cmyPaperConvert
# Purpose:     1. Convert "Paper" object list storing at ./PK/DIC/KGPaperList.pk file
#                 into "sxpText" objects list
#              2. Paper class please refer to ./cmyPackage.py
#              3. sxpText_to_sxpText2: Converts sxpText objects into sxpText2 objects,
#                 "sxpText" class and "sxpText2" refer to ./sxpPackage.py
#              4. Compared with sxpText, sxpText2 added manually annotated and
#                 automatically extracted cause-effect links
# -------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import numpy as np
from scipy.sparse import csr_matrix
from scipy import *
from cmyToolkit import *
from cmyPackage import *
from sxpPackage import *
import sxpFenciMakeTFIDF
import sxpProcessParaText

#######################################################################################
# --------------------------- Some demonstration functions -------------------------- #
#######################################################################################
def ShowSxpTextFileInfo(sxptxt):
    print "************************************************************"
    print type(sxptxt.fname), "Fname = ", sxptxt.fname
    print type(sxptxt.title), "Ftitle =", sxptxt.title
    # for itms in sxptxt.sysce_sent_id_dict.items():
    #     print itms
    # for itms in sxptxt.mance_sent_id_dict.items():
    #     print itms
    # print type(sxptxt.whole_sectitle), "whole_sectitle =", sxptxt.whole_sectitle
    # print type(sxptxt.whole_text), "whole_text =", sxptxt.whole_text
    # print "Abstract:\n", type(sxptxt.abstract), len(sxptxt.abstract)
    # print sxptxt.abstract
    # print
    # print "Related work:\n", type(sxptxt.relatedwork), len(sxptxt.relatedwork)
    # print sxptxt.relatedwork
    # print
    # print "Conclusion:\n", type(sxptxt.conclusion), len(sxptxt.conclusion)
    # print sxptxt.conclusion
    # print
    # print "sxpText.reference:\n", type(sxptxt.reference), len(sxptxt.reference)
    # print sxptxt.reference
    # print
    # print "sxpText.section_id_dict:\n", type(sxptxt.section_id_dict), len(sxptxt.section_id_dict)
    # print sorted(sxptxt.section_id_dict.iteritems(), key = lambda asd:asd[1], reverse=False)
    # print
    # print "sxpText.section_list:"
    # for sec in sxptxt.section_list:
    #     print "\t================================================="
    #     print '\t', type(sec.title), "title =", sec.title
    #     print '\t', type(sec.id_str), "id_str =", sec.id_str
    #     print '\t', type(sec.id_set), "id_set =", sec.id_set
    #     print '\t', type(sec.level), "level =", sec.level
    #     print '\t', type(sec.id), "id =", sec.id
    #     print '\t', type(sec.t_type), "t_type =", sec.t_type
    # print
    # print "sxpText.paraset:", len(sxptxt.paraset)
    # for p in sxptxt.paraset:
    #     print "\t---------------------------------------------------"
    #     print '\t', type(p.para_id), "para_id =", p.para_id
    #     print '\t', "para_text ="
    #     print '\t', p.para_text
    #     print '\t', type(p.para_tuple), "para_tuple =", p.para_tuple
    #     print '\t', type(p.para_tfidf), "para_tfidf =", p.para_tfidf
    #     print '\t', type(p.section_title), "section_title", p.section_title
    #     print '\t', type(p.id), "id =", p.id
    #     print '\t', type(p.id_sec), "id_sec", p.id_sec
    #     print '\t', type(p.context_set), "context_set: len =", len(p.context_set)
    #     for ctxt in p.context_set:
    #       print "\t\t...................................................."
    #       print '\t\t', type(ctxt.context_txt), "text =", ctxt.context_txt
    #       print '\t\t', type(ctxt.id), "id =", ctxt.id
    #       print '\t\t', type(ctxt.id_para), "id_para =", ctxt.id_para
    #       print '\t\t', type(ctxt.id_sec), "id_sec =", ctxt.id_sec
    #       print '\t\t', "sent_id =", [ssss.id for ssss in ctxt.context_sent]
    #     print
    #     print '\t\t\t', type(p.sentenceset), "sentenceset: len =", len(p.sentenceset)
    #     for sent in p.sentenceset:
    #         print "\t\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++"
    #         print "\t\t\t", type(sent.id), "id =", sent.id
    #         print "\t\t\t", type(sent.id_para), "id_para =", sent.id_para
    #         print "\t\t\t", type(sent.id_sec), "id_sec =", sent.id_sec
    #         print "\t\t\t", type(sent.sentence_text), "text =", sent.sentence_text
    #     print
    # print "sxpText.context_set:", len(sxptxt.context_set)
    # for ctxt in sxptxt.context_set:
    #     print "\t...................................................."
    #     print '\t', type(ctxt.id), "id =", ctxt.id
    #     print '\t', type(ctxt.id_para), "id_para =", ctxt.id_para
    #     print '\t', type(ctxt.id_sec), "id_sec =", ctxt.id_sec
    #     print '\t', "sent_id =", [ssss.id for ssss in ctxt.context_sent]
    # print
    print "sxpText.sentenceset:", len(sxptxt.sentenceset)
    for sent in sxptxt.sentenceset[73:74]:
        print "\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++"
        print "\t\t", type(sent.id), "id =", sent.id
        print "\t\t", type(sent.id_para), "id_para =", sent.id_para
        print "\t\t", type(sent.id_sec), "id_sec =", sent.id_sec
        print "\t\t", type(sent.sentence_text), "text =", sent.sentence_text
        # print "\t\t", "sysCEidlst =", sent.sysCEidlst
        # print "\t\t", "manCEidlst =", sent.manCEidlst
    print
    # print "sxpText.p_t matrix:"
    # print sxptxt.p_t
    # print "sxpText.t_s matrix:"
    # print sxptxt.t_s
    # print "sxpText.c_c matrix:"
    # for row in range(len(sxptxt.section_list)):
    #     print sxptxt.section_list[row].title
    #     for col in sxptxt.c_c[row].indices:
    #         print "\t", sxptxt.section_list[col].title

#######################################################################################
# ------------------------------- Toolkit about string ------------------------------ #
#######################################################################################
def IsAbstract(strtitle):
    patstr = u'^abstract'
    strtitle = strtitle.strip().lower()
    findpos = SearchProcess(patstr, strtitle)
    if len(findpos) > 0 and strtitle.count(' ') == 0:
        return 1
    else:
        return 0

def IsRelatedWork(strtitle):
    patstr = u'^related work'
    strtitle = strtitle.strip().lower()
    findpos = SearchProcess(patstr, strtitle)
    if len(findpos) > 0 and strtitle.count(' ') == 1:
        return 1
    else:
        return 0

def IsConclusion(strtitle):
    patstr = u'^conclusion|^summary'
    strtitle = strtitle.strip().lower()
    findpos = SearchProcess(patstr, strtitle)
    if len(findpos) > 0 and strtitle.count(' ') == 0:
        return 1
    else:
        return 0

def TestIsAbstractConclusion():
    s = 'Abstract'
    print IsAbstract(s)
    s = 'Summarys'
    print IsConclusion(s)
    s = "Related   Works"
    print IsRelatedWork(s)

def SegSent(s):
    patstr = u',|\.|\:|\?|，|。|：|？|！|；'
    pattern = re.compile(patstr)
    ss = pattern.split(s)
    return ss

def SearchSentProcess(patstr, s, pat_name, pi):
    sent_list = SegSent(s)
    sent_pos_list = []
    i = 0
    for eachs in sent_list:
        sent_pos = SearchProcess(patstr, eachs, 'n', pat_name, pi)
        for eachsubpos in sent_pos:
            eachsubpos.extend([i])
            sent_pos_list.append(eachsubpos)
        i += 1
    return sent_pos_list

def SearchProcess(patstr, s, sent='y', pat_name='', pi=0):
    if sent == 'y':
        return SearchSentProcess(patstr, s, pat_name, pi)
    pattern = re.compile(patstr)
    match = pattern.search(ProcessString(s))
    pattern_pos = []
    while match:
        tg = match.groups()
        tgtxt = match.group()
        posd = match.span()
        match = pattern.search(s, posd[1])
        pattern_pos.append([tgtxt, posd, tg, pat_name, pi, 0])
    return pattern_pos

def ProcessString(strss):
    strss = re.sub('[ \s\t\r\n]+', ' ', strss)
    strss = ReplaceNonEnglishCharacter(strdecode(strss))
    return strss.strip()

def ProcessAbsConcString(strss):
    strss = re.sub('[ \s\t\r\n]+', ' ', strss)
    strss = ReplaceNonEnglishCharacter(strdecode(strss))
    return strss.strip() + '**.\n'

#######################################################################################
# ---------------------------- Parse Section Network -------------------------------- #
#######################################################################################
def ParseSectionNetwork(sxptxt):
    cs = len(sxptxt.section_id_dict)
    c_c = csr_matrix(np.zeros((cs, cs), dtype=np.float))

    for sxpsec1 in sxptxt.section_list:
        int_id1 = sxpsec1.id
        if len(sxpsec1.id_set) == 0:
            continue
        for sxpsec2 in sxptxt.section_list:
            int_id2 = sxpsec2.id
            if len(sxpsec2.id_set) == 0 and int_id1 == 0:
                c_c[0, int_id2] = 1.0  # the last section is an unknown section with no title and section id
            if int_id2 == int_id1:
                continue
            prefix_len = CompareTwoIDs(sxpsec1.id_set, sxpsec2.id_set)
            if prefix_len == len(sxpsec1.id_set) and len(sxpsec2.id_set) == len(sxpsec1.id_set) + 1:
                c_c[int_id2, int_id1] = 1.0
            else:
                if prefix_len == len(sxpsec1.id_set) and len(sxpsec2.id_set) == len(sxpsec1.id_set):
                    c_c[int_id2, int_id1] = 1.0
    c_c = c_c + c_c.T
    return c_c

def CompareTwoIDs(sec_id1,sec_id2):
    n1 = len(sec_id1)
    n2 = len(sec_id2)
    if sec_id1[0][0] == u'abstract':
        return 0  # means no coverage and no direct child relation because it is the abstract section
    else:
        if n2 < n1:
            return 0
        else:
            if n2 == n1:
                if sec_id1[0][0] == u'top':
                    return 1  # means that the top section belongs to the root of the document, which is section 0
                else:
                    return 0  # means that two sections are both top, so they do not belong to each other
            else:
                dist = ComputePrefix(sec_id1, sec_id2)
                return dist

def ComputePrefix(sec_id1, sec_id2):
    n1 = len(sec_id1)
    n2 = len(sec_id2)
    cl = 0
    if n2 >= n1:
        cl = 0
        for i in range(n1):
            s1 = sec_id1[i]
            s2 = sec_id2[i]
            if s1[0] == s2[0] and s1[1] == s2[1]:
                cl += 1
            else:
                break
    if n2 < n1:
        cl = 0
        for i in range(n2):
            s1 = sec_id1[i]
            s2 = sec_id2[i]
            if s1[0] == s2[0] and s1[1] == s2[1]:
                cl += 1
            else:
                break
    return cl

#######################################################################################
# -------------------------- Convert Paper to sentText ------------------------------ #
#######################################################################################
# ---- This function assigns values for sxpSectionTitle object ---- #
def BuildsxpSecTitleObj(sec_title, id_str, id_set, level, sec_id, tp):
    sxpsec = sxpSectionTitle()
    sxpsec.title = ProcessString(sec_title)
    sxpsec.id_str = ProcessString(id_str)
    sxpsec.id_set = id_set[:]
    sxpsec.level = level
    sxpsec.id = sec_id
    sxpsec.t_type = tp
    return sxpsec

# ---- This function assigns values for sxpPara object ---- #
def BuildsxpParaObj(para_id, para_tuple, section_title, pid, id_sec):
    tpara = sxpPara()
    tpara.para_id = para_id
    tpara.para_tuple = para_tuple
    tpara.section_title = section_title
    tpara.id = pid
    tpara.id_sec = id_sec
    return tpara

# ---- This function assigns values for sxpContext object ---- #
def BuildsxpContextObj(context_id, id_para, id_sec, tempcontext):
    para_context = sxpContext()
    para_context.id = context_id
    para_context.id_para = id_para
    para_context.id_sec = id_sec
    para_context.context_sent = tempcontext
    return para_context

# ---- This function assigns values for sxpSent object ---- #
def BuildsxpSentObj(text, id, id_para, id_sec, manCEidlst, sysCEidlst):
    tsent = sxpSent()
    tsent.sentence_text = ProcessString(text)
    tsent.id = id
    tsent.id_para = id_para
    tsent.id_sec = id_sec
    tsent.manCEidlst = manCEidlst
    tsent.sysCEidlst = sysCEidlst
    return tsent


def is_relevant(sentences, s, t, stopw=False, punc=False):
    max_dis = 0

    for eachs in sentences:
        sim = Similarity(eachs.sentence_text, s, stopw, punc)
        if sim > max_dis:
            max_dis = sim

    if max_dis > t:
        return True
    return False

# ---- PaperObj2sxpTextObj convert a "Paper1" object (see cmyAddCEid.py) to "sxpText" object (see sxpPackage_not_change.py) ---- #
# Input:
#   1. paper -- a "Paper1" object;
#   2. addAbsConc -- bool var means whether adds Abstract and Conclusion into paragraph set and sentence set
# Output: a "sxpText" object for paper
def PaperObj2sxpTextObj(paper, addAbsConc = True):
    sxptxt = sxpText()
    sec_id = 0
    p_id = 0
    t_id = 0
    sent_id = 0

    # ==================== Convert File Information ======================
    print "\tconvert file name and paper title ..."
    sxptxt.fname = os.path.join(kg_dir, "files", paper.Ftag+".txt")
    sxptxt.title = ProcessString(paper.Ftitle.strip(u'\ufeff'))
    print "\tconvert abstract ..."
    for p_abs in paper.Abstract:
        sxptxt.abstract += ProcessAbsConcString(p_abs.text)
    print "\tconvert reference ..."
    for idx,p_ref in enumerate(paper.Refer):
        sxptxt.reference += ('\n' if idx > 0 else '') + ProcessString(p_ref.text)

    # ==================== Convert Each Section ======================
    print "\tconvert each section ..."
    # ------ Create the top section title as the root of sxptxt.section_list ------
    print "\t\tTop ..."
    top = BuildsxpSecTitleObj(sxptxt.title, 'top',[['top', '0']], 0, sec_id, 'document')
    sxptxt.whole_sectitle = top.title
    sxptxt.section_list.append(top)
    sxptxt.section_id_dict[top.id_str] = sec_id
    sec_id += 1
    # ------------------ Convert Abstract ---------------------------
    # ---- Create a sxpSecTitle object for Abstract push into sxptxt.section_list ----
    print "\t\tAbstract ..."
    abs = BuildsxpSecTitleObj('Abstract', 'abstract', [['abstract', '0']], 1, sec_id, 'abstract')
    sxptxt.whole_sectitle += '\n' + abs.title
    sxptxt.section_list.append(abs)
    sxptxt.section_id_dict[abs.id_str] = sec_id
    sec_id += 1
    # ---- if current file has abstract, create a sxpPara object "tpara" for Abstract ----
    for p in paper.P_list:
        if p.Ctag > 0:
            break
        tpara = BuildsxpParaObj('abstract', ['abstract', 'abstract'], abs.title, p_id, abs.id)
        tempcontext, tempt_id = [], t_id
        # ---- Create a sxpSent object "tsent" for each sentence in Abstract and append it into tpara.sentenceset ----
        for abs_sent in p.slist:
            tsent = BuildsxpSentObj(abs_sent.text, sent_id, p_id, abs.id, abs_sent.manCEidlst, abs_sent.sysCEidlst)
            tpara.para_text += ' ' + tsent.sentence_text
            tpara.sentenceset.append(tsent)
            # -- if addAbsConc = True, also append "tsent" into sxptxt.sentenceset
            if addAbsConc:
                sxptxt.sentenceset.append(tsent)
                sent_id += 1
            # ---- Context Check: check whether tsent belongs to tempcontext ---- #
            # -- Yes: append tsent into tempcontext
            if len(tempcontext) == 0 or is_relevant(tempcontext, tsent.sentence_text, 0.06):
                tempcontext.append(tsent)
            # -- No: create a sxpContext Obj for tempcontext and append it into tpara.context_set,  and reset tempcontext as [tsent]
            else:
                tpara.context_set.append(BuildsxpContextObj(tempt_id, p_id, abs.id, tempcontext))
                tempt_id = tempt_id + 1
                tempcontext = [tsent]
        tpara.para_text = tpara.para_text.strip()
        sxptxt.whole_text = tpara.para_text
        if len(tempcontext) > 0:
            tpara.context_set.append(BuildsxpContextObj(tempt_id, p_id, abs.id, tempcontext))
            tempt_id = tempt_id + 1
        # ---- if addAbsConc==True and current file has abstract,push tpara into sxptxt.paraset ----
        if addAbsConc:
            sxptxt.paraset.append(tpara)
            p_id += 1
            sxptxt.context_set.extend(tpara.context_set)
            t_id = tempt_id
    # ------------------- Convert the remain sections ----------------------------
    for sec in paper.C_list:
        print "\t\t"+sec.Ctitle +" ..."
        # ---- if current section is "Related Work" or "Conclusion", add its content to sxptxt.relatedwork or .conclusion ----
        if IsRelatedWork(sec.Ctitle):
            for p in sec.plist:
                for s in p.slist:
                    sxptxt.relatedwork += ProcessAbsConcString(s.text)
        elif IsConclusion(sec.Ctitle):
            for p in sec.plist:
                for s in p.slist:
                    sxptxt.conclusion += ProcessAbsConcString(s.text)
        # ---- Create sxpSecTitle object for current section ----
        sid = str(sec.Ctag)
        sxpsec = BuildsxpSecTitleObj(sid+' '+sec.Ctitle, 's'+sid, [('S', sid)], 1, sec_id, 'section')
        sxptxt.whole_sectitle += '\n'+sxpsec.title
        sxptxt.section_list.append(sxpsec)
        sxptxt.section_id_dict[sxpsec.id_str] = sec_id
        sec_id += 1
        # -------- Convert each subsection --------
        for subsec in sec.sclist:
            print "\t\t\t" + [subsec.SCtitle, str(subsec.SCtag)][subsec.SCtitle == None] + " ..."
            # ---- create sxpSecTitle object for subsections of current section ----
            if subsec.SCtitle is not None:
                ssid = str(subsec.SCtag)
                sxpsubsec = BuildsxpSecTitleObj(
                    sid + '.' + ssid + ' '+subsec.SCtitle,
                    sxpsec.id_str + '.ss' + ssid,
                    sxpsec.id_set + [('SS', ssid)],
                    2, sec_id, 'subsection'
                )
                sxptxt.whole_sectitle += '\n' + sxpsubsec.title
                sxptxt.section_list.append(sxpsubsec)
                sxptxt.section_id_dict[sxpsubsec.id_str] = sec_id
                sec_id += 1
            # ---- processing paragraphs and sentences in current subsection ----
            countpara = 1  # countpara points that the paragraph is the ?th paragraph in current section
            for p in subsec.plist:
                # ---- create a sxpPara object tpara for current paragraph ----
                p_sec = sxptxt.section_list[-1]
                tpara = BuildsxpParaObj(p_sec.id_str+'.p'+str(countpara), [p_sec.id_str, 'p'+str(countpara)], p_sec.title, p_id, p_sec.id)
                tempcontext, tempt_id = [], t_id
                # ---- for each sentence in abstract, create a sxpSent object for it and push it into sxptxt.sentenceset and current paragraph's sentenceset ----
                for s in p.slist:
                    # ---- create a sxpSent object tsent for current sentence ----
                    tsent = BuildsxpSentObj(s.text, sent_id, p_id, p_sec.id, s.manCEidlst, s.sysCEidlst)
                    tpara.para_text += ' ' + tsent.sentence_text
                    tpara.sentenceset.append(tsent)
                    # ---- if current section is not conclusion or addAbsConc==True, push tsent into sxptxt.sentenceset ----
                    if not IsConclusion(sec.Ctitle) or addAbsConc:
                        sxptxt.sentenceset.append(tsent)
                        sent_id += 1
                    # ---- Context Check: check whether tsent belongs to tempcontext ---- #
                    # -- Y: append tsent into tempcontext
                    if len(tempcontext) == 0 or is_relevant(tempcontext, tsent.sentence_text, 0.06):
                        tempcontext.append(tsent)
                    # -- N: create a sxpContext Obj for tempcontext and append it into tpara.context_set,  and reset tempcontext as [tsent]
                    else:
                        tpara.context_set.append(BuildsxpContextObj(tempt_id, p_id, p_sec.id, tempcontext))
                        tempt_id = tempt_id + 1
                        tempcontext = [tsent]

                tpara.para_text = tpara.para_text.strip()
                sxptxt.whole_text += '\n' + tpara.para_text
                if len(tempcontext) > 0:
                    tpara.context_set.append(BuildsxpContextObj(tempt_id, p_id, p_sec.id, tempcontext))
                    tempt_id = tempt_id + 1
                # ---- if current section is not conclusion or addAbsConc==True, push tpara into sxptxt.paraset ----
                if not IsConclusion(sec.Ctitle) or addAbsConc:
                    sxptxt.paraset.append(tpara)
                    countpara += 1
                    p_id += 1
                    sxptxt.context_set.extend(tpara.context_set)
                    t_id = tempt_id

    # =======================  Get man_CE_list; mance_sent_id_dict; sys_CE_list; sysce_sent_id_dict ====================
    sxptxt.man_CE_list = paper.man_CE_list
    sxptxt.sys_CE_list = paper.sys_CE_list
    for idx in range(len(sxptxt.man_CE_list)):
        sxptxt.man_CE_list[idx].Staglst = []
    for idx in range(len(sxptxt.sys_CE_list)):
        sxptxt.sys_CE_list[idx].Staglst = []
    for sent in sxptxt.sentenceset:
        if len(sent.manCEidlst) > 0:
            sxptxt.mance_sent_id_dict[sent.id] = sent.manCEidlst
        if len(sent.sysCEidlst) > 0:
            sxptxt.sysce_sent_id_dict[sent.id] = sent.sysCEidlst
        for manceid in sent.manCEidlst:
            sxptxt.man_CE_list[manceid].Staglst.append(sent.id)
        for sysceid in sent.sysCEidlst:
            sxptxt.sys_CE_list[sysceid].Staglst.append(sent.id)
    # ======================= Get keycount ===========================
    print "\tget keycount ..."
    sxptxt.keycount = sxpProcessParaText.ExtractKeyCount(sxptxt.whole_text)
    print "\t.................................................\n"

    # ======================= MakeTFIDF ===========================
    print "\tmake paragraph TFIDF ..."
    para_textset = []
    for sxppara in sxptxt.paraset:
        para_textset.append(sxppara.para_text)
    sxptxt.para_tfidf = sxpFenciMakeTFIDF.MakeTFIDFForCorpus(para_textset)
    print "\t.................................................\n"

    print "\tmake sentence TFIDF ..."
    sentence_textset = []
    for sxpst in sxptxt.sentenceset:
        sentence_textset.append(sxpst.sentence_text)
    sxptxt.sentence_tfidf = sxpFenciMakeTFIDF.MakeTFIDFForCorpus(sentence_textset)
    print "\t.................................................\n"

    # ======================= Build Matrix ===========================
    print "\tbuild matrix ..."
    cs = len(sxptxt.section_id_dict)  # because we have 0 as the global doc and 1 as the section from the
    ps = len(sxptxt.paraset)
    ss = len(sxptxt.sentenceset)
    ks = len(sxptxt.sentence_tfidf.word)
    ts = len(sxptxt.context_set)
    print "\t\tcs =", cs, "ps =", ps, "ss =", ss, "ks =", ks, "ts =", ts

    print '\t\td_c matrix'
    sxptxt.d_c = csr_matrix(np.ones((1, cs), dtype=np.float))
    print "\t\t.................................................\n"

    print '\t\tc_c matrix'
    sxptxt.c_c = ParseSectionNetwork(sxptxt)
    print "\t\t.................................................\n"

    print '\t\tbuilding c_p matrix'
    sxptxt.c_p = csr_matrix((cs, ps), dtype=float64)
    print "\t\tc_p.shape:", sxptxt.c_p.shape
    for para in sxptxt.paraset:
        c = para.id_sec
        p = para.id
        sxptxt.c_p[c, p] = 1.0
    print "\t\t.................................................\n"

    print '\t\tp_s matrix'
    sxptxt.p_s = csr_matrix((ps, ss), dtype=float64)
    for sent in sxptxt.sentenceset:
        p = sent.id_para
        s = sent.id
        sxptxt.p_s[p, s] = 1.0
    print "\t\t.................................................\n"

    print '\t\ts_k matrix'
    sxptxt.s_k = csr_matrix(sxptxt.sentence_tfidf.tfidf)
    print "\t\t.................................................\n"

    print '\t\tbuilding p_t matrix and t_s matrix'
    sxptxt.p_t = csr_matrix((ps, ts), dtype=float64)
    sxptxt.t_s = csr_matrix((ts, ss), dtype=float64)
    print "\t\tp_t.shape:", sxptxt.p_t.shape
    print "\t\tt_s.shape:", sxptxt.t_s.shape
    for para in sxptxt.paraset:
        p = para.id
        for cont in para.context_set:
            t = cont.id
            sxptxt.p_t[p, t] = 1.0
            for eachs in cont.context_sent:
                s = eachs.id
                sxptxt.t_s[t, s] = 1.0
    print "\t\t.................................................\n"

    ShowSxpTextFileInfo(sxptxt)
    # ================= Dump pickle file for sxptxt and return it as output ===================
    temppicklefp = os.path.join(kg_dir, "pickle", paper.Ftag + '.txt_2.pk' if addAbsConc else paper.Ftag + ".txt_1.pk")
    StoreSxptext(sxptxt, temppicklefp)
    return sxptxt

# ---- CEPaper2sxpText: ---- #
# 1. Converts Paper objects list storing at paperpkfp into sxpText objects list;
# 2. Stores the sxpText objects list in sxptxtpkfp
def CEPaper2sxpText(paperpkfp, sxptxtpkfp, addAbsConc):
    PaperList = Loadpickle(paperpkfp)
    sxpTextList = []
    for curpaper in PaperList:
        print "Converting ", curpaper.Ftag
        sxpTextList.append(PaperObj2sxpTextObj(curpaper, addAbsConc))
    # StoreSxptext(sxpTextList, sxptxtpkfp)
    return sxpTextList

# ---- sxpText_to_sxpText2: ---- #
# 1. Converts sxpText objects list storing at 'sxptxtpkfp' into sxpText2 objects list;
# 2. Stores the changed sxpText2 objects list in 'sxptxtpkfp2'
def sxpText_to_sxpText2(sxptxtpkfp, sxptxtpkfp2, pkfnamept = ""):
    if not os.path.exists(sxptxtpkfp2):
        os.makedirs(sxptxtpkfp2)
    sxptxtList = sxpGetDirFileList(sxptxtpkfp)[0]
    for sxpfp in sxptxtList:
        if not re.match(pkfnamept, sxpfp):
            continue
        print "processing", sxpfp
        sxptxt = LoadSxptext(os.path.join(sxptxtpkfp, sxpfp))
        sxptxt2 = sxpText2(sxptxt)
        StoreSxptext(sxptxt2, os.path.join(sxptxtpkfp2, sxpfp))

#######################################################################################
# --------------------------------- Main function  ---------------------------------- #
#######################################################################################
if __name__ == '__main__':
    # TestIsAbstractConclusion()
    # paperpkfp = os.path.join(DICpkdir, "KGCEPaperList.pk")
    # sxptxtpkfp = os.path.join(acl_dir, "pickle")
    # sxpTextList = CEPaper2sxpText(paperpkfp, sxptxtpkfp, True)
    # sxptxtpkfp2 = os.path.join(acl_dir, "pickle_CEnet1")
    # sxpText_to_sxpText2(sxptxtpkfp, sxptxtpkfp2)
    fp = r'E:\Programs\Eclipse\CE_relation\CEsummary_new\kgmance\pickle\f0001.txt_2.pk'
    # fpt = r"E:\Programs\Eclipse\CE_relation\CEsummary\PK\pickle\P14-1011.xhtml_2.pickle"
    # fp = r"E:\Programs\Eclipse\CE_relation\CEsummary\acl\pickle\P14-1008.xhtml_2.pickle"
    sxptxt = Loadpickle(fp)
    # sxptxt = LoadSxptext(fp)
    # sxptxt = Loadpickle(fpt)
    # ShowSxpTextFileInfo(sxptxt)
    print sxptxt.sentenceset[0].sentence_text.split(' ')

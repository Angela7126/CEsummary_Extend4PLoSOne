# -*- coding: UTF-8 -*- 

#######################################################################################
# --------------------------------- Function Introduce ------------------------------ #
#######################################################################################
# This functions set intends to:
# 1. Read causal_links.txt files and convert it into patterns.
# 2. sort the patterns according to some order
# 3. Design all check functions to judge whether a sequence of tokens satisfied the definition of some group
# 4. match the sentences with patterns

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import nltk
import re
import operator
from sxpTextAddCE import *
from cmyPackage import *
from sxpPackage import *
from cmyToolkit import *
from cmyPaperConvert import *
from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn
from bs4 import BeautifulSoup
import copy

ctxtdir = os.path.join(os.path.curdir, "CheckTXT")
acltxtdir = os.path.join(acl_dir, "CETxtXls")
aclpercedir = os.path.join(acl_dir, "CEPerDic")
ductxtdir = os.path.join(duc_dir, "CETxtXls")

# --------- people hypernym set ------------------
PEOPLE = ('person', 'individual', 'someone', 'somebody', 'mortal', 'soul', 'being', 'human', 'hominid', 'humans', 'man',
          'mankind')
### ---- stanford_parser java package ----  
os.environ['STANFORD_PARSER'] = r'D:\jars\stanford-parser.jar'
os.environ['STANFORD_MODELS'] = r'D:\jars\stanford-parser-3.5.2-models.jar'
### ---- JAVA_HOME path ----
java_path = r"C:\Program Files\Java\jdk1.8.0_45\bin\java.exe"
os.environ['JAVAHOME'] = java_path
### ---- initiate a parser ---- 
parser = stanford.StanfordParser(model_path=r"D:\jars\englishPCFG.ser.gz")


#######################################################################################
# --------------------------- Some demonstration functions -------------------------- #
#######################################################################################
### ---- show each pattern ----
def ShowPatterns(Patterns):
    for p in Patterns:
        if not isinstance(p, pattern):
            raise TypeError("ShowPatterns: This is not a pattern!")
        print str(p.pfreq) + "  " + str(p.main_token) + " ---- " + str(p.constraints)
        # print p.cases;


### ---- show cause or effect ----
def ShowCorE(c_e):
    if not isinstance(c_e, CorE):
        raise TypeError("ShowCorE: This is not a CorE!")
    print "--CorE_ParserTree:"
    print c_e.PTree
    print "--CorE_LvsIdx:", c_e.span


### ---- show CElinks ----
def ShowCELink(celink):
    if not isinstance(celink, CELink):
        raise TypeError("ShowCElink: This is not a CElink!")
    print "Pattern:"
    ShowPatterns([celink.pt])
    print "ParserTree:"
    for pt in celink.PTreelst:
        print pt
    print "Cause:"
    ShowCorE(celink.cause)
    print "Effect:"
    ShowCorE(celink.effect)


### ---- show Sentence Number covered by CE links ----
def ShowCESentNum(CElistpath, txtcorpdir):
    CElist = Loadpickle(CElistpath)
    fnamelist = Get_file_pathes(txtcorpdir)
    TotalCESentNum = 0
    for idx, CEset in enumerate(CElist):
        curCESentNum = 0
        for ce in CEset:
            curCESentNum += len(ce.sInfo)
        TotalCESentNum += curCESentNum
        print os.path.split(fnamelist[idx])[-1], "CESentNum = ", curCESentNum
    print "TotalCESentNum = ", TotalCESentNum


### ---- print CE sets in CEList into .txt type file for human observation ----
def CElst2TXT(CEList, CE_txt_path):
    txtCE = codecs.open(CE_txt_path, 'w', 'utf8')
    for i in range(len(CEList)):
        txtCE.write("************************************************************\n")
        txtCE.write("f%04d" % (i + 1) + ": Cause-Effect links\n")
        txtCE.write("************************************************************\n\n")
        CEset = CEList[i]
        for j in range(len(CEset)):
            txtCE.write("CASE: " + str(j + 1) + '\n')
            ce = CEset[j]
            txtCE.write("Stag: ")
            for ceSentInfo in ce.sInfo:
                txtCE.write("%d " % ceSentInfo.Stag)
            txtCE.write("\n")
            txtCE.write(
                "\tPattern: " + '%d' % ce.pt.pfreq + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
            sentTXT = []
            for PT in ce.PTreelst:
                sentTXT.extend(PT.leaves())
            txtCE.write("\tsentTXT: " + ' '.join(sentTXT) + '\n')
            txtCE.write("\tCause: " + ' '.join(ce.cause.PTree.leaves()) + '\n')
            txtCE.write("\tEffect: " + ' '.join(ce.effect.PTree.leaves()) + '\n\n')
    txtCE.close()
    return


### ---- print CE cases in CE set into .txt type file for human observation ----
def CEset2TXT(CEset, CE_txt_path):
    txtCE = codecs.open(CE_txt_path, 'w', 'utf8')
    txtCE.write("************************************************************\n")
    txtCE.write(os.path.split(CE_txt_path)[-1] + ": Cause-Effect links\n")
    txtCE.write("************************************************************\n\n")
    for idx, ce in enumerate(CEset):
        txtCE.write("CASE: " + str(idx) + '\n')
        txtCE.write("Stag: ")
        for ceSentInfo in ce.sInfo:
            txtCE.write("%d " % ceSentInfo.id)
        txtCE.write("\n")
        txtCE.write(
            "\tPattern: " + '%d' % ce.pt.pfreq + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
        sentTXT = []
        for PT in ce.PTreelst:
            sentTXT.extend(PT.leaves())
        txtCE.write("\tsentTXT: " + ' '.join(sentTXT) + '\n')
        txtCE.write("\tCause: " + ' '.join(ce.cause.PTree.leaves()) + '\n')
        txtCE.write("\tEffect: " + ' '.join(ce.effect.PTree.leaves()) + '\n\n')
    txtCE.close()
    return

### ---- print CE cases in CE set into .txt type file for human observation ----
def sysCElst2TXT(sysCElst, Sentlst, CE_txt_path):
    txtCE = codecs.open(CE_txt_path, 'w', 'utf8')
    txtCE.write("************************************************************\n")
    txtCE.write(os.path.split(CE_txt_path)[-1] + ": Cause-Effect links\n")
    txtCE.write("************************************************************\n\n")
    for ce in sysCElst:
        txtCE.write("CASE: " + str(ce.sysCEid) + '\n')
        txtCE.write("Stag: ")
        for sid in ce.Staglst:
            txtCE.write("%d " % sid)
        txtCE.write("\n")
        txtCE.write(
            "\tPattern: " + '%d' % ce.pt.pfreq + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
        sentTXT = []
        for sid in ce.Staglst:
            sentTXT.append(Sentlst[sid].sentence_text)
        txtCE.write("\tsentTXT: " + ' '.join(sentTXT) + '\n')
        txtCE.write("\tCause: " + str(ce.cw_span) + '\n')
        txtCE.write("\tEffect: " + str(ce.ew_span) + '\n\n')
    txtCE.close()
    return

def ShowSxpTextFileInfo(sxptxt):
    print "************************************************************"
    print type(sxptxt.fname), "Fname = ", sxptxt.fname
    print type(sxptxt.title), "Ftitle =", sxptxt.title
    print type(sxptxt.whole_sectitle), "whole_sectitle =", sxptxt.whole_sectitle
    print type(sxptxt.whole_text), "whole_text =", sxptxt.whole_text
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
    print "sxpText.paraset:", len(sxptxt.paraset)
    for p in sxptxt.paraset:
        print "\t---------------------------------------------------"
        print '\t', type(p.para_id), "para_id =", p.para_id
        print '\t', "para_text ="
        print '\t', p.para_text
        print '\t', type(p.para_tuple), "para_tuple =", p.para_tuple
        print '\t', type(p.para_tfidf), "para_tfidf =", p.para_tfidf
        print '\t', type(p.section_title), "section_title", p.section_title
        print '\t', type(p.id), "id =", p.id
        print '\t', type(p.id_sec), "id_sec", p.id_sec
        print '\t', type(p.context_set), "context_set: len =", len(p.context_set)
        for ctxt in p.context_set:
            print "\t\t...................................................."
            print '\t\t', type(ctxt.context_txt), "text =", ctxt.context_txt
            print '\t\t', type(ctxt.id), "id =", ctxt.id
            print '\t\t', type(ctxt.id_para), "id_para =", ctxt.id_para
            print '\t\t', type(ctxt.id_sec), "id_sec =", ctxt.id_sec
            print '\t\t', "sent_id =", [ssss.id for ssss in ctxt.context_sent]
        print
        print '\t\t\t', type(p.sentenceset), "sentenceset: len =", len(p.sentenceset)
        for sent in p.sentenceset:
            print "\t\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++"
            print "\t\t\t", type(sent.id), "id =", sent.id
            print "\t\t\t", type(sent.id_para), "id_para =", sent.id_para
            print "\t\t\t", type(sent.id_sec), "id_sec =", sent.id_sec
            print "\t\t\t", type(sent.sentence_text), "text =", sent.sentence_text
            print "\t\t\t", type(sent.sysCEidlst), "sysCEidlst =", sent.sysCEidlst
        print
        # print "sxpText.context_set:", len(sxptxt.context_set)
        # for ctxt in sxptxt.context_set:
        #     print "\t...................................................."
        #     print '\t', type(ctxt.context_txt), "text =", ctxt.context_txt
        #     print '\t', type(ctxt.id), "id =", ctxt.id
        #     print '\t', type(ctxt.id_para), "id_para =", ctxt.id_para
        #     print '\t', type(ctxt.id_sec), "id_sec =", ctxt.id_sec
        #     print '\t', "sent_id =", [ssss.id for ssss in ctxt.context_sent]
        # print
        # print "sxpText.sentenceset:", len(sxptxt.sentenceset)
        # for sent in sxptxt.sentenceset:
        #     print "\t\t+++++++++++++++++++++++++++++++++++++++++++++++++++++"
        #     print "\t\t", type(sent.id), "id =", sent.id
        #     print "\t\t", type(sent.id_para), "id_para =", sent.id_para
        #     print "\t\t", type(sent.id_sec), "id_sec =", sent.id_sec
        #     print "\t\t", type(sent.sentence_text), "text =", sent.sentence_text
        # print


#######################################################################################
# ------------------------------- Pattern Process ----------------------------------- #
#######################################################################################
### ---- TXT2Patterns process the causal_links.txt into "pattern" type object list ----  
def TXT2Patterns():
    causaltxt = ReadFile(os.path.join(corpdir, 'causal_links.txt'))
    causal_txt_lines = causaltxt.splitlines()
    Patterns = []
    ptid = 0
    for txt in causal_txt_lines:
        ### ---- if a line is a empty string, skip it ----
        if len(txt) == 0 or re.match(ur"[\s]+$", txt):
            continue
        ### ---- if a line started with '#', it is a comment line, skip it ----
        if re.match(ur"#", txt):
            continue
        ### ---- get the 3-level type for each pattern ----
        ptidx = [int(i) for i in list((re.match(ur'(\d+) (\d+) (\d+) (\d+) (\d+)', txt)).groups())]
        ### ---- get pattern text for each pattern ----
        ptxt = re.search(ur'(?<={)(.+)(?=})', txt).group(0)
        ### ---- get example text list for each pattern ---- 
        etxt = re.findall(ur'(?<=\[)([^\]]+)(?=\])', txt)
        ### ---- create a 'pattern' type object and append it into "Patterns" list ----
        Patterns.append(pattern(ptidx[0], ptidx[1], ptidx[2:], ptxt, etxt, ptid))
        ptid += 1
    Dumppickle(os.path.join(DICpkdir, 'Patterns.pk'), Patterns)
    return Patterns


### ---- Split the Patterns List by the length of main_token ----
def SptPtnlst_mtlen(Patterns, mtlen):
    SptPatterns = [[]]
    PtnSptDic, newIdx = {}, 1

    ptidx = 0
    while ptidx < len(Patterns):
        mtlst = ListFlatten(Patterns[ptidx].main_token)
        if len(mtlst) != mtlen:
            ptidx += 1
            continue
        mt = ' '.join(mtlst)
        if mt in PtnSptDic:
            SptPatterns[PtnSptDic[mt]].append(Patterns[ptidx])
        else:
            PtnSptDic[mt], newIdx = newIdx, newIdx + 1
            SptPatterns.append([Patterns[ptidx]])
        del Patterns[ptidx]

    while Patterns != []:
        mtlst = ListFlatten(Patterns[0].main_token)
        InsertFlag = False
        for i in range(len(mtlst) - mtlen + 1):
            mt = mtlst[i] if mtlen == 1 else ' '.join(mtlst[i:i + mtlen])
            if mt in PtnSptDic:
                SptPatterns[PtnSptDic[mt]].append(Patterns[0])
                InsertFlag = True
                break
        if not InsertFlag:
            SptPatterns[0].append(Patterns[0])
        del Patterns[0]

    return SptPatterns, PtnSptDic


### ----- check whether two patterns list is same! ----
def Check_Ptnlst_Eq(Patterns, newPatterns):
    if len(Patterns) != len(newPatterns):
        return False

    flag = True
    for ptn in Patterns:
        if ptn not in newPatterns:
            flag = False
    for ptn in newPatterns:
        if ptn not in Patterns:
            flag = False
    return flag


### ---- Order the Patterns list ----            
def OrderPatterns(Patterns, rvsflag):
    cmpfun = operator.attrgetter('pfreq')
    Patterns.sort(key=cmpfun, reverse=rvsflag)
    SptPatterns = [Patterns[:]]
    Spt_mtlst = []
    ### ---- Split the Patterns list by the length of main_tokens in SptSpan
    for SptSpan in range(1, 3):
        tempSptPtns, tempSptDic = SptPtnlst_mtlen(SptPatterns[0], SptSpan)
        Spt_mtlst.extend(tempSptDic.keys())
        SptPatterns[0] = tempSptPtns[0]
        SptPatterns.extend(tempSptPtns[1:])
    ### ---- Sort each split pattern list separately ----
    for ptnlst in SptPatterns:
        ptnlst.sort(reverse=rvsflag)
    ### ---- merge all split pattern list ----
    newPatterns = []
    while SptPatterns != []:
        MaxfrqPtnlst = 0
        Maxfrq = -1
        for i in range(len(SptPatterns)):
            if SptPatterns[i][0].pfreq > Maxfrq:
                Maxfrq = SptPatterns[i][0].pfreq
                MaxfrqPtnlst = i
        newPatterns.append(SptPatterns[MaxfrqPtnlst][0])
        del SptPatterns[MaxfrqPtnlst][0]
        if SptPatterns[MaxfrqPtnlst] == []:
            del SptPatterns[MaxfrqPtnlst]
    ### ---- Check whether the new Patterns list after ordered lost or repeat any pattern ----
    if Check_Ptnlst_Eq(Patterns, newPatterns):
        Dumppickle(os.path.join(DICpkdir, 'Patterns.pk'), newPatterns)
        return newPatterns
    else:
        raise ValueError("OrderPatterns: The Patterns losing or repeat adding element after sort")
        return []


### 'MainTokenRegExp' intend to: create regular expression list for all patterns
### ---- in order to check whether the sentence contains a pattern's main_token ---
### ---- notice that the capture group (.*) is in accordance with Patterns constraints ----
def MainTokenRegExp(Patterns):
    mtRegExpList = []  ### main_token Regular Expression list
    for p in Patterns:
        ### current Regular Expression for current patterns\
        ### if current pattern only have one main_token, find the first appearance of this main_token ----
        if len(p.main_token) == 1 and len(p.main_token[0]) == 1:
            curRegExp = ur'(.*?)'
        ### else, try to match as much as the pattern can ---- 
        else:
            curRegExp = ur'(.*)'
            ### patterns' main_token are broken into pieces, each piece must be matched successive.
        for pi in range(len(p.main_token)):
            ### ---- if current constraint pieces has a class constraint piece, add " " ----            
            for cp in p.constraints[pi]:
                if cp[0] != '(':
                    curRegExp = curRegExp + ur' '
                    break
            ### ---- add current main_token pieces into current Regular Expression -- curRegExp ----
            for ti in range(len(p.main_token[pi])):
                if ti > 0:
                    curRegExp += ur' '
                tokens = p.main_token[pi][ti]
                ### if current token is a string, add it into curRegExp directly
                if type(tokens) == str:
                    if tokens in ['.', '?', ':']:
                        curRegExp += '\\'.encode('utf-8')
                    curRegExp += tokens.encode('utf-8')
                ### if current token is a list, create a "no capture group" (?:token[0]|token[1]|...) for it
                else:
                    curRegExp = curRegExp + ur'(?:'
                    for tempt in range(len(tokens)):
                        if tempt > 0:
                            curRegExp = curRegExp + ur'|'
                        if tokens[tempt] in ['.', '?', ':']:
                            curRegExp = curRegExp + '\\'.encode('utf-8')
                        curRegExp = curRegExp + tokens[tempt].encode('utf-8')
                    curRegExp = curRegExp + ur')'
            ### ---- if pattern is ended with a main_token, stop add "(.*)" ----
            if len(p.main_token) == len(p.constraints) and pi == len(p.main_token) - 1:
                break
            ### ---- if next constraint pieces has a class constraint piece, add " " ----            
            for cp in p.constraints[pi + 1]:
                if cp[0] != '(':
                    curRegExp = curRegExp + ur' '
                    break
            ### ---- if current main_token pieces is not the last one, add (.*?), else add (.*) ----
            if pi < len(p.main_token) - 1:
                curRegExp = curRegExp + ur'(.*?)'
            else:
                curRegExp = curRegExp + ur'(.*)'

        mtRegExpList.append(re.compile(curRegExp, re.I))  ###re.I means ignore upper or lower cases

    Dumppickle(os.path.join(DICpkdir, 'mtRegExpList.pk'), mtRegExpList)
    return mtRegExpList


### 'CheckPatternsCases' intends to:
### 1. Get Patterns: pattern object list.
### 2. Get mtRegExtlst: the Regular Expression list constructed by each pattern's main_tokens
### 3. Check whether each pattern can cope with its cases.
### 4. Recoding CE links extracting by matching each pattern with its cases into './CheckTXT/PatternsTestRecoding.txt' file
def CheckPatternsCases():
    ### ---- get Patterns and mtRegExplst ----
    Patterns = TXT2Patterns()
    Patterns = OrderPatterns(Patterns, True)
    mtRegExplst = MainTokenRegExp(Patterns)

    emptyTree = Tree('ROOT', [])
    plen = len(Patterns)

    TestRecfp = os.path.join(ctxtdir, 'PatternsTestRecoding.txt')
    pt_txt_fp = os.path.join(ctxtdir, 'patterns.txt')
    TestRec = codecs.open(TestRecfp, 'w', 'utf8')
    pt_txt = codecs.open(pt_txt_fp, 'w', 'utf8')

    for pi in range(plen):
        pt = Patterns[pi]
        pt_txt.write('%d' % pt.pfreq + ' %s' % pt.main_token + "----" + ' %s' % pt.constraints + '\n')
        print "*****************************************************"
        print "Processing Pattern ", pi
        ShowPatterns([pt])

        PTset = []
        for str in pt.cases:
            PTset.extend(parser.raw_parse(str))

        for pppt in PTset:
            CEcases = GettingCEcases([pt], [mtRegExplst[pi]], emptyTree, pppt, emptyTree)
            if CEcases == []:
                print "case : ", ' '.join(pppt.leaves()), "cannot match!\n"
            else:
                for ce in CEcases:
                    TestRec.write(
                        "Pattern: " + '%d' % pi + ' %d' % ce.pt.pfreq + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
                    TestRec.write("Cases: " + ' '.join(pppt.leaves()) + '\n')
                    TestRec.write(
                        "Cause: " + ' '.join(ce.cause.PTree.leaves()) + '\n')  # " -- "+ str(ce.cause.span)+'\n');
                    TestRec.write(
                        "Effect: " + ' '.join(ce.effect.PTree.leaves()) + '\n')  # " -- "+ str(ce.effect.span)+'\n');
                    TestRec.write("\n")
    TestRec.close()
    pt_txt.close()


#######################################################################################
# -------------------- Stanford Parser-Tree Leave Span Index ------------------------ #
#######################################################################################

### ---- Given the main_tokens matched txt groups, find their according leave index in parser trees sentPT ----
### ---- leaveIdx: a list, each element is a list containing 2 tuple, representing the start and end idx for each group pieces ----
### ---- and each tuple contains 2 number: 1st number is the PT idx in sentPT; 2nd number means the leave idx in according PT ----   
def Find_leaves_Idx(ptn, sentTXT, groups, TXT_split):
    leaveIdx = []
    if (ptn.constraints)[0] == []:  # and len(groups[0])==0:
        leaveIdx.append([(-1, -1), (-1, -1)])
        del groups[0]

    for g in groups:
        g = g.strip()
        ### if current matching content g is a empty string, append a empty leave index span [(-1,-1),(-1,-1)] into leaveIdx
        if len(g) == 0:
            leaveIdx.append([(-1, -1), (-1, -1)])
            continue
        ### else, find the strings leave index span
        span = []
        sg_Idx = sentTXT.index(g)
        eg_Idx = sg_Idx + len(g) - 1
        ptidx = 1
        while ptidx < len(TXT_split):
            if sg_Idx <= TXT_split[ptidx][0]:
                span.append((ptidx - 1, sentTXT[0:sg_Idx].count(' ') - TXT_split[ptidx - 1][1]))
                break
            ptidx += 1
        while ptidx < len(TXT_split):
            if eg_Idx <= TXT_split[ptidx][0]:
                span.append((ptidx - 1, sentTXT[0:eg_Idx].count(' ') - TXT_split[ptidx - 1][1]))
                break
            ptidx += 1
        leaveIdx.append(span)

    return leaveIdx


### ---- check whether a leave span index is legal ----
def checkLvsIdx(PTlst, LvsIdx, sp):
    ### ---- index should be a nonegtive number 
    if LvsIdx[0][0] < 0 or LvsIdx[0][1] < 0 or LvsIdx[1][0] < 0 or LvsIdx[1][1] < 0:
        return False
    ### ---- start_leave_index should 'before' than end_leave_index
    if LvsIdx[0][0] * sp > LvsIdx[1][0] * sp:
        return False
    if LvsIdx[0][0] == LvsIdx[1][0] and LvsIdx[0][1] * sp > LvsIdx[1][1] * sp:
        return False
    ### ---- start_leave_index and end_leave_index should be found in PTlst
    PTnum = len(PTlst)
    if LvsIdx[0][0] >= PTnum or LvsIdx[1][0] >= PTnum:
        return False
    STlen = len(PTlst[LvsIdx[0][0]].leaves())
    ETlen = len(PTlst[LvsIdx[1][0]].leaves())
    if LvsIdx[0][1] >= STlen or LvsIdx[1][1] >= ETlen:
        return False
    return True


### ---- move a leave index a step 'forward' ----
def movIdxForward(PTlst, Idx, sp):
    tempIdx = list(Idx)
    tempIdx[1] += sp
    if sp > 0 and tempIdx[1] >= len(PTlst[tempIdx[0]].leaves()):
        tempIdx[0] += 1
        tempIdx[1] = 0
    elif sp < 0 and tempIdx[1] < 0:
        tempIdx[0] -= 1
        if tempIdx[0] >= 0:
            tempIdx[1] = len(PTlst[tempIdx[0]].leaves()) - 1
    return tuple(tempIdx)


### ---- extend leave index span ----
def ExtendLvsIdx(curIdx, SL, EL, sp):
    ### sp < 0 means EL -(right)-> SL; sp > 0 means SL -(right)-> EL; need to adjust into SL -(right)-> EL
    if sp < 0:
        SL, EL = EL, SL
    ### if curIdx is a empty tuple, then [SL,EL] is its value;
    if len(curIdx) == 0:
        curIdx = [SL, EL]
    ### if sp >0 then expend curIdx forward
    elif sp > 0:
        curIdx = [curIdx[0], EL]
    ### if sp >0 then expend curIdx forward
    elif sp < 0:
        curIdx = [SL, curIdx[1]]

    return curIdx


#######################################################################################
# ------------------------ Stanford Parser-Tree process ----------------------------- #
#######################################################################################

### ---- Find the SubPT list in PTlst that between index_span (SL, EL) ---- 
def SubPTinSpan(PTlst, SL, EL, sp):
    ### if the span is not correct, showing error "MaxPTinSpan: The leave index span is not correct!":
    if not checkLvsIdx(PTlst, [SL, EL], sp):
        raise IndexError('The Parser Tree span [SL,EL] of PTlst is not correct!')
        return None, SL, EL

    SubPTlst = []  ### SubPTlst store the SubParserTree in span [SL,EL] 
    curPTIdx = SL[0]  ### curPTIdx store the current visit ParserTree Index in ParserTree list PTlst;
    curLvsIdx = SL[
        1]  ### curLvsIdx store the started current Leave Index in PTlst[curPTIdx] that we need to build a subPT 

    ### ---- if (curPTIdx,curLvsIdx) still in leaves index span (SL,EL), continue build subPT ----
    while (curPTIdx * sp < EL[0] * sp) or ((curPTIdx == EL[0]) and curLvsIdx * sp <= EL[1] * sp):
        ### curSubPT_loc: the position of curLvsIdx_th leaves in PTlst[curPTIdx]
        curSubPT_loc = list(PTlst[curPTIdx].leaf_treeposition(curLvsIdx))

        ### ---- if get curSubPT's parent -> curParentPT has no leaves beyond span [(curPTIdx,curLvsIdx),EL] ----
        ### ---- then backtrack, i.e. curSubPT = curParentPT ---- 
        while True:
            ### ---- if curSubPT_loc is empty list, means curSubPT point to the ROOT of PTlst[curPTIdx], cannot continue backtrack ----  
            if curSubPT_loc == []:
                break
            ### ---- get curParentPT_loc: the current Parent Parser Tree location; curParentPT: the current Parent Parser Tree----
            curParentPT_loc = curSubPT_loc[0:-1]
            if curParentPT_loc == []:
                curParentPT = PTlst[curPTIdx]
            else:
                curParentPT = PTlst[curPTIdx][curParentPT_loc]

            ### ---- check whether curParentPT has child that beyond span [(curPTIdx,curLvsIdx),EL] ----
            ### ---- if such a child is not exist, continue backtrack: curSubPT_loc = curParentPT_loc ----

            sibIdx = curSubPT_loc[-1] - sp  ### sibIdx: the sibling index of curSubPT in curParentPT at -sp direction
            ### ---- if such a sibling is not exist ----
            if sibIdx < 0 or sibIdx >= len(curParentPT):
                ### ---- check whether curSubPT has leaves beyond EL ----
                (tempPTIdx, tempLvsIdx) = movIdxForward(PTlst, (curPTIdx, curLvsIdx),
                                                        (len(curParentPT.leaves()) - 1) * sp)
                if (tempPTIdx == EL[0]) and tempLvsIdx * sp > EL[
                    1] * sp:  ### if it has leaves beyond EL, stop backtracking
                    break
                else:  ### if its leaves all in span [(curPTIdx,curLvsIdx),EL], continue backtrack
                    curSubPT_loc = curParentPT_loc
                    ### ---- if such a sibling exist, then stop backtracking ----
            else:
                break
        ### ---- Get final curSubPT, add it into SubPTlst ----
        if curSubPT_loc == []:
            curSubPT = PTlst[curPTIdx]
        else:
            curSubPT = PTlst[curPTIdx][curSubPT_loc]
        SubPTlst.append(curSubPT)
        ### ---- Get next start subPT leave index (curPTIdx,curLvsIdx) ---- 
        if isinstance(curSubPT, Tree):
            (curPTIdx, curLvsIdx) = movIdxForward(PTlst, (curPTIdx, curLvsIdx), len(curSubPT.leaves()) * sp)
        else:
            (curPTIdx, curLvsIdx) = movIdxForward(PTlst, (curPTIdx, curLvsIdx), sp)
            ### ---- If there is only one SubPT in SubPTlst, return it; else build a new ParserTree Tree('ROOT',subPTlst) ----
    if len(SubPTlst) == 1:
        return SubPTlst[0]
    elif sp < 0:
        return Tree('ROOT', SubPTlst[::-1])
    else:
        return Tree('ROOT', SubPTlst)


### ---- if subPT's label doen't satisfy regexp and subPT only has one child, move subPT downward and continue the check ---- 
def PTMoveDownward(subPT, regexp=ur'', flag=False):
    while not flag and isinstance(subPT, Tree):
        if regexp != ur'':
            flag = (True if re.match(regexp, subPT.label()) else False)
        if flag or len(subPT) != 1 or not isinstance(subPT[0], Tree):
            break
        subPT = subPT[0]
    return flag, subPT


#######################################################################################
# ------------------------ Checking a Pattern Constrain piece ----------------------- #
#######################################################################################
### ----------- Get the hypernym's lemma_name of str in WordNet ----
def GetHyperNames(str):
    hypername = []
    for synset in wn.synsets(str):
        hyperset = synset.hypernyms()
        for hs in hyperset:
            hypername.extend(hs.lemma_names())
    return hypername


### ---- checkClass use to check whether a parser-tree can match a class, i.e. '&' ----
def checkClass(subPT, cp, SL, EL, sp, cIdx, eIdx):
    flag = False
    poslst = subPT.pos()  ### poslst is a list of tuple like (pos, word)
    leafTXT = (' '.join(subPT.leaves())).strip().lower()

    if len(cp) == 0:
        raise SyntaxWarning("checkClass: Current class constraint pieces \'" + cp + "\' is empty")
        flag = False
    elif cp[0] == '-' and cp != '--':
        if re.match(ur'-&.*', cp):
            tempflag, tempcIdx, tempeIdx = checkClass(subPT, cp[1:], SL, EL, sp, cIdx, eIdx)
            flag = not tempflag
        else:
            flag = not (leafTXT == cp[1:])
    elif cp[0] != '&':
        flag = (leafTXT == cp)
    elif cp == '&ClauseHead':
        flag = (
            leafTXT in ['that', 'whether', 'if', 'what', 'whatever', 'who', 'whoever', 'whom', 'whose', 'which', 'when',
                        'where', 'how', 'why'])
    elif cp == '&THIS':
        flag = (leafTXT in ['this', 'that', 'these', 'those', 'it', 'which'])
    elif cp == '&this':
        flag = (leafTXT in ['this', 'that', 'these', 'those'])
    elif cp == '&ADJ':
        flag = (
            leafTXT in ['direct', 'same', 'main', 'seperate', 'final', 'alone', 'important', 'major', 'key', 'biggest',
                        'possible', 'only', 'primary'])
    elif cp == '&adj':
        flag = True
        for pos in poslst:
            if not re.match('JJ.*', pos[1]):
                flag = False
                break
    elif cp == '&ADV':
        flag = (leafTXT in ['just', 'also', 'only', 'merely', 'all', 'alone', 'often', 'simply'])
    elif cp == '&adv':
        flag = True
        for pos in poslst:
            if not re.match('RB.*', pos[1]):
                flag = False
                break
    elif cp == '&CAN':
        flag = (leafTXT in ['can', 'could', 'may', 'might', 'will', 'would', 'must', 'should', 'ought to'])
    elif cp == '&BE':
        flag = (leafTXT in ['be', 'being', 'been', 'have been', 'is', 'am', 'are', 'was', 'were'])
    elif cp == '&AND':
        flag = (leafTXT in ['and', 'but', 'so', 'also'])
    elif cp == '&NUM':
        flag = (True if re.match(ur'CD.*', subPT.label(), ) else False) or (
            leafTXT in ['a', 'an', 'several', 'a few', 'some', 'many', 'half'])
    elif cp == '&ONE':
        flag = (leafTXT in ['the', 'a', 'an', 'one', 'another'])
    elif cp == '&OF':
        flag = (leafTXT in ['one of', 'part of'])
    elif cp == '&MODNUM':
        flag = (leafTXT in ['at least', 'at most'])
    elif cp == '&N':
        flag = (True if re.match(ur'NN.*', subPT.label()) else False)
    elif cp == '&V':
        flag = (True if re.match(ur'VB.*', subPT.label()) else False)
    elif cp == '&NP':
        ### ---- check whether subPT is labeled start with 'N' ----
        flag, subPT = PTMoveDownward(subPT, ur'N.*', flag)
        ### ---- check whether subPT is only consisted by 'NP','PP','IN' ----
        if not flag and isinstance(subPT, Tree):
            countNP = 0
            for cursubPT in subPT:
                ttflag, cursubPT = PTMoveDownward(cursubPT)
                flag = isinstance(cursubPT, Tree) and (
                    re.match(ur'N.*', cursubPT.label()) or cursubPT.label() in ['DT', 'PP', 'IN', 'CC'])
                if not flag:
                    break
                if re.match(ur'N.*', cursubPT.label()):
                    countNP += 1
            flag = flag and (countNP > 0) and re.match(ur'N.*', subPT[0].label()) and subPT[-1].label() != 'CC'
    elif cp == '&V-ing':
        while not flag and isinstance(subPT, Tree):
            flag = (True if subPT.label() == 'VP' and ((poslst[0][1] == 'VBG') or (
                poslst[0][1] in ['ADVP', 'RB', 'RBR', 'RBS'] and poslst[1][1] == 'VBG')) else False)
            if flag or len(subPT) > 1:
                break
            subPT = subPT[0]

    elif cp == '&TODO':
        while not flag and isinstance(subPT, Tree):
            flag = (True if subPT.label() == 'VP' and ((poslst[0][1] == 'TO') or (
                poslst[0][1] in ['ADVP', 'RB', 'RBR', 'RBS'] and poslst[1][1] == 'TO')) else False)
            if flag or len(subPT) > 1:
                break
            subPT = subPT[0]
    elif cp in ['&Clause', '&C', '&R']:
        ### ---- subPT is a sentence judged by Stanford-Parser ----
        ### ---- if subPT only has one child, move downward ---- 
        flag, subPT = PTMoveDownward(subPT, ur'S.*', flag)
        ### ---- if subPT is not a sentence judged by Stanford-Parser ----
        if (not flag) and isinstance(subPT, Tree):
            ### ---- if subPT only contains one words or subPT is a noun phrase judged by stanford-parser, it cannot be a sentence ----
            if re.match(ur'N.*', subPT.label()) or len(subPT.leaves()) == 1:
                flag = False
            else:
                ### ---- if all subPT's children's label are 'S.*' and 'CC' ----
                for cursubPT in subPT:
                    flag = isinstance(cursubPT, Tree) and (
                        re.match(ur'S.*', cursubPT.label()) or cursubPT.label() in ['CC', '.', ',', ':'])
                    if not flag:
                        break
                        ### ---- else if one of subPT's children is labeled with 'V.*'  ----
                if not flag:
                    for cursubPT in subPT:
                        flag, cursubPT = PTMoveDownward(cursubPT, ur'(?:VP|VB$|VBZ|VBP|VBN|VBD)', flag)
                        if flag:
                            break
        ### ---- if subPT is clause and cp is &C or &E, should change cause or effect index--cIdx,eIdx ----
        if flag and cp == '&C':
            cIdx = ExtendLvsIdx(cIdx, SL, EL, sp)
        if flag and cp == '&R':
            eIdx = ExtendLvsIdx(eIdx, SL, EL, sp)
    else:
        raise SyntaxWarning("checkClass: Current class constraint pieces \'" + cp + "\' have never seen!")
        flag = False
    return flag, cIdx, eIdx


### ---- checkAddition use to check whether the parser-tree can match the constraints starting and ending with '@' ----
def checkAddition(subPT, cp, SL, EL, sp, cIdx, eIdx):
    flag = False

    if len(cp) == 0:
        raise SyntaxWarning("checkAddition: Current addition constraint pieces \'" + cp + "\' is empty")
        flag = True
    elif cp == 'C':
        flag = True
        cIdx = ExtendLvsIdx(cIdx, SL, EL, sp)
    elif cp == 'R':
        flag = True
        eIdx = ExtendLvsIdx(eIdx, SL, EL, sp)
    elif cp == 'Complete':
        ### ---- if subPT is a sent judged by stanford-parser, i.e. subPT's label is started with S, set flag = True ----
        ### ---- if subPT's label doesn't start with S, and subPT only has one child, move downward ----
        flag, subPT = PTMoveDownward(subPT, ur'S.*')
        ### ---- if subPT's label cannot start with S, check whether subPT contains '.' between words ----
        if not flag:
            for i in range(len(subPT)):
                flag = isinstance(subPT[i], Tree) and [True, subPT[i].label() != '.'][i != len(subPT) - 1]
                if not flag:
                    break
        ### ---- if subPT cannot pass above check, re-parse the subPT's text to generate a new parser-tree ----
        ### ---- if new parser-tree is a sent judged by stanford-parser, and has object and predicate ----
        if flag:
            subPT = (parser.raw_parse(' '.join(subPT.leaves()))).next()
            flag, subPT = PTMoveDownward(subPT, ur'S.*')
            ### ---- If reconstructed subPT is a sentence, check whether it has N.* and V.* and N.* is before V.* ----
            try:
                cursubPT_taglst = [cursubPT.label() for cursubPT in subPT]
            except AttributeError:
                flag = False
            if flag:
                countNP, NPloc_1st = 0, -1
                countVP, VPloc_1st = 0, -1
                for cc in range(len(cursubPT_taglst)):
                    if re.match(ur'N.*', cursubPT_taglst[cc]):
                        if countNP == 0:
                            NPloc_1st = cc
                        countNP += 1
                    elif re.match(ur'V.*', cursubPT_taglst[cc]) and cursubPT_taglst[cc] != ur'VBG':
                        if countVP == 0:
                            VPloc_1st = cc
                        countVP += 1
                flag = (countNP > 0) and (countVP > 0) and (NPloc_1st < VPloc_1st)

    elif cp == 'NCTime':
        POS = subPT.pos()
        for curpos in POS:
            if re.match(ur'N.*', curpos[1]):
                hypername = GetHyperNames(curpos[0])
                for hn in hypername:
                    if re.match(ur'time.*', hn) or re.match(ur'.*time$', hn):
                        return flag, cIdx, eIdx
        flag = True
    elif cp == 'NCPeople':
        POS = subPT.pos()
        for curpos in POS:
            if curpos[1] == 'PRP':
                return flag, cIdx, eIdx
            if re.match(ur'N.*', curpos[1]):
                tempstr = curpos[0]
                Timers = 4
                while Timers > 0:
                    hypername = GetHyperNames(tempstr)
                    if not len(hypername):
                        break
                    for hn in hypername:
                        if hn in PEOPLE:
                            return flag, cIdx, eIdx
                    tempstr = hypername[0]
                    Timers -= 1
        flag = True
    else:
        raise SyntaxWarning("checkAddition: Current addition constraint pieces \'" + cp + "\' have never seen!")
        flag = True

    return flag, cIdx, eIdx


### ---- check whether the PTlst in span [SL,tempEL] can satisfy the class constraint pieces cp ----
def Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx):
    ### --- check if tempEL is still inside the span [SL,EL] ----
    if not checkLvsIdx(PTlst, [tempEL, EL], sp):
        return False, EL, cIdx, eIdx
    ### ---- subPT : the subParserTree in span (SL, tempEL) ---- ### ---- subPT : the subParserTree in span (SL, tempEL) ---- 
    subPT = SubPTinSpan(PTlst, SL, tempEL, sp)
    ### ---- check whether parser tree subPT can satisfy cp ----
    flag, cIdx, eIdx = checkClass(subPT, cp, SL, tempEL, sp, cIdx, eIdx)
    ### ---- if subPT cannot satisfy cp or APlist, return False and remain the original EL ----
    if not flag:
        return False, EL, cIdx, eIdx
    ### ---- if subPT can satisfy a cp, check whether it can satisfy cases in APlst ---- 
    for ap in APlst:
        flag, cIdx, eIdx = checkAddition(subPT, ap, SL, tempEL, sp, cIdx, eIdx)
        if not flag:
            return False, EL, cIdx, eIdx
    ### ---- if subPT can satisfy cp and APlst, return True and return tempEL as newEL ----
    return True, tempEL, cIdx, eIdx


#######################################################################################
# --------------------------------- Pattern Matching -------------------------------- #
#######################################################################################
### 'MatchingClassPiece' function intend to:
### 1. split a constraint piece start with '&' into class_condition_list CPlst and additional_condition_list APlst
### 2. create subtrees that contained by (PTlst,curLvsIdx) 
### 3. check whether one of these subtrees can matching a cp in CPlst and can matching all ap in APlst 
###    1) if exist, i.e. the '&' constraint piece can be successfully matched,  then return 'True' and modify the current_leaves_span_index curLvsIdx
###    2) if not exit, return false and return original curLvsIdx.
### Notices:
### 1. Adopting maximum matching mechanism, i.e., constraint = &NP , string = He feed these beautiful dogs, we need to find "these beautiful dogs" instead of 'dogs','beautiful dogs'. 
### 2. in this matching mechanism may create the cause and effect leaves span, '&C','&R','&NP@C@','&V-ing@C@' ...
def MatchingClassPiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx):
    ### ---- if current leaves index span is illegal, return False ----
    if not checkLvsIdx(PTlst, curLvsIdx, sp):
        return False, curLvsIdx, cIdx, eIdx

    flag = False
    ### ---- get class condition pieces list--> CPlst; additional conditional pieces list--> APlst -----
    if len(consp and '@') > 0:  ### if current constraint pieces 'consp' contains additional condition i.e. '@C@'
        templst = DelEmptyString(re.split('@+', consp))
        CPlst = DelEmptyString(re.split('/+', templst[0]))
        APlst = templst[1:]
    else:  ### if current constraints pieces 'consp' not contains additional condition.
        CPlst = DelEmptyString(re.split('/+', consp))
        APlst = []
    SL = curLvsIdx[0]
    EL = curLvsIdx[1]
    minusflag = False
    ### ---- if has not found subST satisfy consp, and curLvsIdx is a legal leave span ----
    ### ---- get new subPT in span [SL,EL] ---- 
    for cp in CPlst:
        ### ---- if current cp is minus constraint as '-&adj', if it cannot be processed correctly, stop check remaining cp ----
        if cp[0] == '-' and cp != '--':
            minusflag = True
            flag, ttEL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, SL, EL, sp, cIdx, eIdx)
            if not flag:
                break
        ### ----if cp is the class_constraint_pieces that only cover one word ----
        elif cp[0] != '&' or cp in ['&THIS', '&this', '&ClauseHead', '&ADJ', '&ADV', '&AND', '&ONE']:
            flag, EL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, SL, EL, sp, cIdx, eIdx)
        ### ----if cp is the class_constraint_pieces that at most cover two word ----
        elif cp in ['&CAN', '&BE', '&OF', '&MODNUM']:
            for inc in range(0, 2):
                tempEL = movIdxForward(PTlst, SL, sp * inc)
                flag, EL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx)
                if flag:
                    break
        ### ---- if cp is the class_constraint_pieces that doesn't sure cover how many words, but all of them must be the same kind of label ----
        elif cp in ['&adj', '&adv', '&N', '&V', '&NUM']:
            havematched, lastMatchedEL, tempEL = False, SL, SL
            while checkLvsIdx(PTlst, [tempEL, EL], sp):
                tempflag, newEL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx)
                if not tempflag:
                    break
                havematched, lastMatchedEL = True, newEL
                tempEL = movIdxForward(PTlst, tempEL, sp)
            if havematched:
                flag, EL = True, lastMatchedEL
        ### ---- if cp is the class_constraint_pieces that doesn't sure cover how many words, and their label may be different ----
        elif cp in ['&NP', '&V-ing', '&TODO']:
            ### ---- skip the punctuation symbol at the start position ----
            while checkLvsIdx(PTlst, [SL, EL], sp) and SubPTinSpan(PTlst, SL, SL, sp).label() in ['.', ',', ':']:
                SL = movIdxForward(PTlst, SL, sp)
            ### ---- start matching process ----
            havematched, lastMatchedEL, tempEL = False, SL, SL
            while checkLvsIdx(PTlst, [tempEL, EL], sp):
                tempflag, newEL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx)
                if tempflag:
                    havematched, lastMatchedEL = True, newEL
                tempEL = movIdxForward(PTlst, tempEL, sp)
            if havematched:
                flag, EL = True, lastMatchedEL
        ### ---- if cp is a class_constraint_piece that covers a clause, matched by decreasing the span ----
        else:
            tempEL = EL
            while (not flag) and checkLvsIdx(PTlst, [SL, tempEL], sp):
                flag, EL, cIdx, eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx)
                tempEL = movIdxForward(PTlst, tempEL, -sp)
        ### ----if cp is not a minus constrant and can be matched,  stop check the remaining pieces in CPlist ----
        if flag and not minusflag:
            break
            ### ---- we found subPT can match CPlst and APlst, and CPlst not contain minus constraints ----
    ### ---- then move EL a step forward, return 'True' and next LvsIdx ----
    if flag and not minusflag:
        EL = movIdxForward(PTlst, EL, sp)
        return flag, [EL, curLvsIdx[1]], cIdx, eIdx
    ### ---- if CPlist is a minus constraint list and can be matched correctly, return True and original span as next span ----
    elif flag and minusflag:
        return flag, curLvsIdx, cIdx, eIdx
    ##---- if cannot match, then return 'False' ----
    return False, curLvsIdx, cIdx, eIdx


### 'MatchingIgnorePiece' intends to:
### 1. check whether a Ignore constraint piece, i.e. the constraints start with '(' and end with ')', is legal. 
### 2. split the Ignore constraint piece into a list of class constraint pieces and small Ignore constraint pieces
### 3. Get sub_ParserTrees inside leaves span curLvsIdx, check whether they can match each piece we got in step 2:
###    1) If can match, return True and modify the next under checking leaves_span
###    2) If cannot, return False and the current checking leaves_span;
def MatchingIgnorePiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx):
    ### ---- current constraint pieces 'consp' start with '(' and end with ')',delete '(',')' ----
    while len(consp) > 1 and consp[0] == '(' and consp[-1] == ')':
        consp = consp[1:-1]
    ### if '(' and ')' does not paired up at the begin and end of consp, raise error "'(' and ')' doesn't paired up!"
    if re.match(ur'\([^\)]*$', consp) or re.match(ur'[^\(]*\)$', consp):
        raise SyntaxError("When checking ignore constrains: '(' and ')' doesn't paired up!")
        return False, curLvsIdx, cIdx, eIdx
    ### ---- get class condition pieces list--> Iglst ----
    Iglst = DelEmptyString(re.split(' ', consp))
    i = 0
    while i < len(Iglst):
        lenIglst = len(Iglst)
        if Iglst[i][0] == '(':
            j = i
            while j < lenIglst and Iglst[j][-1] != ')':
                j += 1
            tempIglst = Iglst[i:j + 1] if j < lenIglst else Iglst[i:lenIglst]
            Iglst[i] = ' '.join(tempIglst)
            k = (j - i) if j < lenIglst else (j - i - 1)
            while k > 0:
                del Iglst[i + 1]
                k = k - 1
        i = i + 1
    ### ---- Matching Process ----
    SL = curLvsIdx[0]
    EL = curLvsIdx[1]
    ### ---- for each ig in Iglst, check whether PTlst[SL,EL] on can match it, if can change SL to create new Leaves Index Span ----
    for ig in Iglst:
        if len(ig) > 0 and ig[0] == '(':
            flag, tempIvsIdx, cIdx, eIdx = MatchingIgnorePiece(PTlst, ig, [SL, EL], sp, cIdx, eIdx)
        else:
            flag, tempIvsIdx, cIdx, eIdx = MatchingClassPiece(PTlst, ig, [SL, EL], sp, cIdx, eIdx)
        if flag:
            SL = tempIvsIdx[0]
            EL = tempIvsIdx[1]
        elif ig[0] == '-' and not flag:
            return False, [SL, EL], cIdx, eIdx
    return True, [SL, EL], cIdx, eIdx


### 'MatchingConstraints' intend to:
### check whether the parser tree satisfied Patterns[m]'s constraints
###    1) if satisfied, return True, whole sent parser tree(list), cause(CorE), effect(CorE) ----
###    2) if unsatisfied, return False,[],None,None ----
def MatchingConstraints(PTlst, pattern, leavesIdx):
    finalCheck = True
    cIdx = []
    eIdx = []
    C_cons = re.compile(ur'&C.*')
    R_cons = re.compile(ur'&R.*')
    Cons = pattern.constraints  ### pattern's constraints list
    for i in range(len(Cons)):
        curCons = Cons[i]  ### current constraint pieces, a list
        curLvsIdx = leavesIdx[i]  ### current constraint's matching text start_leaf and end_leaf in PTlst;
        sp = 1
        ### ---- current constraint is the first constraint, it should be checked reversely, or----
        if i == 0:
            curCons = curCons[::-1]
            curLvsIdx = curLvsIdx[::-1]
            sp = -sp
        ### ---- current constraint is start with &C or &R and not end with &C or &R, it should be checked reversely ----
        if len(curCons) > 1 and (C_cons.match(curCons[0]) or R_cons.match(curCons[0])) and \
                not C_cons.match(curCons[-1]) and not R_cons.match(curCons[-1]):
            curCons = curCons[::-1]
            curLvsIdx = curLvsIdx[::-1]
            sp = -sp
        ### ---- for each curCons piece, check whether PTlst can fit it ----         
        for consp in curCons:
            if consp[0] == '&':
                finalCheck, curLvsIdx, cIdx, eIdx = MatchingClassPiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx)
            elif consp[0] == '(':
                finalCheck, curLvsIdx, cIdx, eIdx = MatchingIgnorePiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx)
            else:
                raise SyntaxWarning(
                    "MatchingConstraints: Current constraint pieces \'" + consp + "\' have never seen!")
            ### ---- Once PTlst cannot fit the curCons piece, whole constraints matching fall, stop matching ---- 
            if not finalCheck:
                break
        ### ---- if has find unmatched constraints, stop check remain constraits ----
        if not finalCheck:
            break
    return finalCheck, cIdx, eIdx


#######################################################################################
# --------------------------------- Build CE links ---------------------------------- #
#######################################################################################
### 'GettingCEcases' intend to: Build CE links for a ParserTree using patterns
### Input:
###    1. Patterns: a list of pattern we can choose.
###    2. mtRegExpList: a list of re.compile() object constructed by main_tokens of each pattern, is used to match curPT's text and break it into groups.
###    3. curPT: current processing stranford parser tree.
###    4. prePT, nextPT: the pre or next parser tree for curPT to serve as additional material, because some patterns are designed to deal with 2 adjacent sentences.
### Output:
###    CEcases: a list of CElink object that we can extracted from curPT additional with its pre and next parser-tree.
def GettingCEcases(Patterns, mtRegExpList, prePT, curPT, nextPT):
    CEcases = []
    plen = len(Patterns)
    preTXT = ((' '.join(prePT.leaves())).lower()).strip()
    pTxtLen = len(preTXT)
    pLvsLen = len(prePT.leaves())
    curTXT = ((' '.join(curPT.leaves())).lower()).strip()
    cTxtLen = len(curTXT)
    cLvsLen = len(curPT.leaves())
    nextTXT = ((' '.join(nextPT.leaves())).lower()).strip()
    nTxtLen = len(nextTXT)
    nLvsLen = len(nextPT.leaves())
    ### ---- create sentST, sentTXT, sentTXTidx ----
    ### sentPT: adjacent Parser Tree that may formed a CE links
    ### sentTXT: convert the sentST' leaves into a string in sequence
    ### sentTXTidx: store the end_index of each parser_tree_leaves string in sentTXT, in order to check current matching group belonging to which parser_tree
    ### i.e., sentTXT_split_idx[1][0] < txtidx < sentTXT_split_idx[1][1], then txtidx belonging to sentPT[1][1], i.e. curPT
    sentPT = [[curPT],
              [prePT, curPT],
              [curPT, nextPT]
              ]
    sentTXT = [curTXT,
               preTXT + [u' ', u''][pTxtLen == 0] + curTXT,
               curTXT + [u' ', u''][nTxtLen == 0] + nextTXT
               ]
    sentTXT_split_idx = [[(0, 0), (cTxtLen, cLvsLen)],
                         [(0, 0), (pTxtLen, pLvsLen), (pTxtLen + cTxtLen, pLvsLen + cLvsLen)],
                         [(0, 0), (cTxtLen, cLvsLen), (cTxtLen + nTxtLen, cLvsLen + nLvsLen)]
                         ]
    emptyTree = Tree('ROOT', [])

    ### ---- for each pattern ----
    for m in range(plen):
        ### ---- check whether current Sent satisfied Patterns[m]'s main token ----
        if Patterns[m].constraints[0] == []:
            mtResult = mtRegExpList[m].match(curTXT)
        else:
            mtResult = mtRegExpList[m].match(ur' ' + curTXT)
        finalCheck = False
        ### ---- If satisfied Patterns[m]'s main token ----
        if mtResult:
            for i in range(3):
                ### ---- if current pattern cannot cover more than one sentence ----
                # or (i == 2 and len(Patterns[m].main_token) == len(Patterns[m].constraints)):
                if i > 0 and not Patterns[m].moresent:
                    break
                ### ---- Get constraints coordinated text tuples consTxtTup ----
                consTxtTup = [mtstr.strip() for mtstr in mtResult.groups()]
                if i == 1:
                    consTxtTup[0] = preTXT + u' ' + consTxtTup[0]
                elif i == 2:
                    consTxtTup[-1] = curTXT[curTXT.index(consTxtTup[-1]):] + [u' ', u''][nTxtLen == 0] + nextTXT
                ### ---- Get the leave spans for each constrain piece ----
                leavesIdx = Find_leaves_Idx(Patterns[m], sentTXT[i], consTxtTup, sentTXT_split_idx[i])
                finalCheck, cIdx, eIdx = MatchingConstraints(sentPT[i], Patterns[m], leavesIdx)
                ### ---- if it is satisfied, create CELink object and append it into current CE set ----
                if finalCheck:
                    if cIdx == []:
                        cause = CorE(emptyTree, cIdx)
                    else:
                        cause = CorE(SubPTinSpan(sentPT[i], cIdx[0], cIdx[1], 1), cIdx)
                    if eIdx == []:
                        effect = CorE(emptyTree, eIdx)
                    else:
                        effect = CorE(SubPTinSpan(sentPT[i], eIdx[0], eIdx[1], 1), eIdx)
                    CEcases.append(CELink(Patterns[m], sentPT[i], cause, effect))
                    if len(sentPT[i]) == 1:
                        CEcases.extend(GettingCEcases(Patterns, mtRegExpList, emptyTree, cause.PTree, emptyTree))
                        CEcases.extend(GettingCEcases(Patterns, mtRegExpList, emptyTree, effect.PTree, emptyTree))
                    break
        if finalCheck:
            break
    return CEcases


### ---- 'CElinksForCorpus' intend to: create a CEList for the whole Corpus. ----
### Output:
###    CEList: CE Link set list for the whole corpus and each member means the CE Link set for a single paper
def CElinksForKG(paperlist_pk_path, CEList_pk_path):
    ### ---- get pattern list ----
    Patterns = TXT2Patterns()
    Patterns = OrderPatterns(Patterns, True)
    ### ---- get mtRegExplist(main_token RegExp List) for all patterns ----
    mtRegExpList = MainTokenRegExp(Patterns)
    ### ---- CEList store the CElinks for all the corpus ----
    CEList = []
    ### ---- get paper object list of the corpus ----
    FList = Loadpickle(paperlist_pk_path)
    ### ---- For each file, Getting causal sentences ----
    for curfile in FList:
        cursentlst = curfile.S_list
        slen = len(cursentlst)  ### the number of sentences in current file
        curCEset = []

        print "*****************************************"
        print "Processing file:", curfile.Ftag

        for s in range(slen):
            sent = cursentlst[s]
            emptyTree = Tree('ROOT', [])
            if sent.PTree == []:
                continue
            print "sentence: ", sent.Stag
            ### we have checked that each sentence in the corpus is parsed into at most one parser-tree
            curPT = sent.PTree[0]
            prePT = emptyTree if s < 1 or cursentlst[s - 1].PTree == [] else cursentlst[s - 1].PTree[0]
            nextPT = emptyTree if s > slen - 2 or cursentlst[s + 1].PTree == [] else cursentlst[s + 1].PTree[0]
            sentCEset = GettingCEcases(Patterns, mtRegExpList, prePT, curPT, nextPT)
            for sentCE in sentCEset:
                if len(sentCE.PTreelst) == 1:
                    sentCE.sInfo = [sent]
                elif sentCE.PTreelst[0] == sent.PTree[0]:
                    sentCE.sInfo = [sent, cursentlst[s + 1]]
                else:
                    sentCE.sInfo = [cursentlst[s - 1], sent]
            curCEset.extend(sentCEset)
            ### ---- append current files CE set into whole CE set list ----
        print
        print "Length of CEset for current file:", len(curCEset)
        print
        Dumppickle(os.path.join(pkdir, 'CEPerDic', curfile.Ftag + '_CE.pk'), curCEset)
        CEList.append(curCEset)
    Dumppickle(CEList_pk_path, CEList)
    return CEList


def CElinksForACL(papers_dir, sxptxt_dir):
    # ---- get pattern list and mtRegExplist(main_token RegExp List) ----
    Patterns = Loadpickle(os.path.join(DICpkdir, 'Patterns.pk'))
    mtRegExpList = Loadpickle(os.path.join(DICpkdir, 'mtRegExpList.pk'))
    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_dir)[0]
    file_name_pattern = re.compile(u'^P14-\d\d\d\d\.xhtml$')
    emptyTree = Tree('ROOT', [])

    for f in file_list[7:]:
        # ---- if current file name dose not fit the filename pattern of ACL2014 corpus, skip it ----
        if not file_name_pattern.match(f):
            continue
        # ---- Processing sentence pattern matching for current file ----
        print "*****************************************"
        print "Processing file:", f

        # -- get two sxpText objects for each file --
        pkfp1 = os.path.join(sxptxt_dir, f + '_1.pickle')
        sxptxt1 = LoadSxptext(pkfp1)
        sxptxt1.fname = f+'_1'
        sxptxt1.title = f
        pkfp2 = os.path.join(sxptxt_dir, f + '_2.pickle')
        sxptxt2 = LoadSxptext(pkfp2)
        sxptxt2.fname = f+'_2'
        sxptxt2.title = f
        # print sxptxt1.fname, sxptxt1.title, len(sxptxt1.sentenceset)
        # print sxptxt2.fname, sxptxt2.title, len(sxptxt2.sentenceset)

        # -- get sentence list from the sxpText object which include Abstract and Conclusion in its sentence set --
        Sentlst2 = copy.deepcopy(sxptxt2.sentenceset)
        slen2 = len(Sentlst2)
        print "\t-- sxptxt2 total sentences:", slen2, "--"
        Sentlst1 = copy.deepcopy(sxptxt1.sentenceset)
        slen1 = len(Sentlst1)
        print "\t-- sxptxt1 total sentences:", slen1, "--"

        # -- for each sentence, build its Stanford-parser Tree --
        print "\t-- Building Stanford-Parser Tree List for Sentence List --"
        SentPTlst2 = []
        for sent in Sentlst2:
            print "\t\t------- Sentence: ", sent.id, "-----------"
            senttxt = RemoveUStrSpace(sent.sentence_text)
            # print "\t\t", type(senttxt), senttxt
            tempsentPTlst = []
            try:
                tempsentPT = parser.raw_parse(senttxt)
            except:
                pass
            try:
                while True:
                    tempsentPTlst.append(tempsentPT.next())
            except StopIteration:
                pass
            if not tempsentPTlst:
                SentPTlst2.append(emptyTree)
            elif len(tempsentPTlst) == 1:
                SentPTlst2.append(tempsentPTlst[0])
            else:
                SentPTlst2.append(Tree('ROOT', [pt[0] for pt in tempsentPTlst]))
            # print "\t\t\t", list(SentPTlst2[-1])
            print "\t\t\tComplete!"
        StoreSxptext(SentPTlst2, os.path.join(acl_dir, "TempPKFiles", "SentPTlst4CEmatching", f+'_2'))
        # SentPTlst2 = LoadSxptext(os.path.join(acl_dir, "TempPKFiles", "SentPTlst4CEmatching", f+'_2'))

        # -- for each sentence, using Patterns matching to get CELink object list --
        print "\t-- Using Patterns matching to get CELink object list --"
        curCEset2 = []  # a CELink object list
        for s in range(slen2):
            if len(SentPTlst2[s]) == 0:
                continue
            print "\t\t--------- matching sentence: ", Sentlst2[s].id, "------------"
            ### we have checked that each sentence in the corpus is parsed into at most one parser-tree
            curPT = SentPTlst2[s]
            prePT = emptyTree if s < 1 else SentPTlst2[s - 1]
            nextPT = emptyTree if s > slen2 - 2 else SentPTlst2[s + 1]
            sentCEset = []
            try:
                sentCEset = GettingCEcases(Patterns, mtRegExpList, prePT, curPT, nextPT)
            except:
                pass

            for sentCE in sentCEset:
                if len(sentCE.PTreelst) == 1:
                    sentCE.sInfo = [Sentlst2[s]]
                elif sentCE.PTreelst[0] == curPT:
                    sentCE.sInfo = [Sentlst2[s], Sentlst2[s + 1]]
                else:
                    sentCE.sInfo = [Sentlst2[s - 1], Sentlst2[s]]

            if len(sentCEset) > 0:
                curCEset2.extend(sentCEset)
            print "\t\t\tComplete!"
        StoreSxptext(curCEset2, os.path.join(aclpercedir, f + '_2'))
        # curCEset2 = LoadSxptext(os.path.join(acl_dir, "TempPKFiles", "CEsetByMatch", f + '_2'))
        # for idx, ce in enumerate(curCEset2):
        #     print idx, "sent id list:", [sent.id for sent in ce.sInfo]

        # -- Add sys_CE_list (matched CElinks set) and sysce_sent_id_dict (dict mapping sent_id to CE_id) into sxptxt_2
        print "\t-- Add matched CE links set into sxptxt2 object --"
        PK2sysCElist, PK2sysce_sent_id_dict = GetSysCE(curCEset2)
        # for ce in PK2sysCElist:
        #     print ce.sysCEid, ce.Staglst
        # for itm in PK2sysce_sent_id_dict.items():
        #     print itm
        # -- Overwrite the pickle files by new sxptxt2 which add CE information --
        sxptxt2.sys_CE_list = PK2sysCElist
        sxptxt2.sysce_sent_id_dict = PK2sysce_sent_id_dict
        for sidx in range(slen2):
            if PK2sysce_sent_id_dict.has_key(sidx):
                sxptxt2.sentenceset[sidx].sysCEidlst = PK2sysce_sent_id_dict[sidx]
        # for s in sxptxt2.sentenceset:
        #     print s.id, s.sysCEidlst
        StoreSxptext(sxptxt2, pkfp2)
        # -- Write CELink object list in txt file for human checking --
        CEset2TXT(curCEset2, os.path.join(acltxtdir, f + "_2_CE.txt"))
        WriteStrFile(os.path.join(acltxtdir, f + '_2_CESentIDdict.txt'), GetSysCESentIdLst(sxptxt2))


        # -- Add sys_CE_list (matched CElinks set) and sysce_sent_id_dict (dict mapping sent_id to CE_id) into sxptxt_1
        print "\t-- Add matched CE links set into sxptxt1 object --"
        # -- Get the mapping between sentence id of sxptxt_1 and sxptxt_2
        sentid_dict_1to2, sentid_dict_2to1 = GetSentIdDict(Sentlst1, Sentlst2)
        # -- Map elements of PK2sysCElist into PK1sysCElist, and create PK1sysce_sent_id_dict in the same time
        PK1sysCElist = []
        PK1sysce_sent_id_dict = {}
        ceidx = 0
        for sysce in PK2sysCElist:
            # -- If current CE link of PK2sysCElist contains sentences that are excluded from sxptxt1, skip it --
            if not set(sysce.Staglst).issubset(sentid_dict_2to1.keys()):
                continue
            # -- change current CE link's id and containing sentence id list, and add it into PK1sysCElist --
            sysce.sysCEid = ceidx
            for idx, oldsid in enumerate(sysce.Staglst):
                sentid = sentid_dict_2to1[oldsid]
                sysce.Staglst[idx] = sentid
                if PK1sysce_sent_id_dict.has_key(sentid):
                    PK1sysce_sent_id_dict[sentid].append(ceidx)
                else:
                    PK1sysce_sent_id_dict[sentid] = [ceidx]
            PK1sysCElist.append(sysce)
            ceidx += 1

        # -- Overwrite the pickle files by new sxptxt2 which add CE information --
        sxptxt1.sys_CE_list = PK1sysCElist
        sxptxt1.sysce_sent_id_dict = PK1sysce_sent_id_dict
        for sidx in range(slen1):
            if PK1sysce_sent_id_dict.has_key(sidx):
                sxptxt1.sentenceset[sidx].sysCEidlst = PK1sysce_sent_id_dict[sidx]
        # for s in sxptxt1.sentenceset:
        #     print s.id, s.sysCEidlst
        StoreSxptext(sxptxt1, pkfp1)
        # -- Write CELink object list in txt file for human checking --
        sysCElst2TXT(PK1sysCElist, Sentlst1, os.path.join(acltxtdir, f + "_1_CE.txt"))
        WriteStrFile(os.path.join(acltxtdir, f + '_1_CESentIDdict.txt'), GetSysCESentIdLst(sxptxt1))



def BuildDUCsxpText(filefp):
    soup = BeautifulSoup(ReadFile(filefp), "html.parser")
    sxptxt = sxpText()

    Headlst = soup.find_all("head")
    Textlst = soup.find_all("text")

    # -- get .txt file name as sxpText fname --
    sxptxt.fname = soup.docno.string.strip()
    # -- get news title as sxpText title --
    for idx, hd in enumerate(Headlst):
        sxptxt.title += hd.string.strip()
        sxptxt.title += '. '
    sxptxt.title = sxptxt.title.strip()
    if len(sxptxt.title) == 0:
        sxptxt.title = sxptxt.fname
    # -- get whole_text string --
    rawtxt = ""
    for text in Textlst:
        rawtxt += text.string
    rawtxt = re.sub(ur"(?<![\.|\:|\?|。|：|？|！|；])\n+(?! {3,})", ur" ", rawtxt.strip())
    rawtxt = re.sub(ur"(?<=\n)[ |\n]{3,}", ur"", rawtxt)
    sxptxt.whole_text = ProcessString(rawtxt)
    paratxtlst = [ProcessString(paratxt) for paratxt in rawtxt.split('\n')]

    # -- get whole_sectitle, section_id_dict, section_list --
    top = BuildsxpSecTitleObj(sxptxt.title, 'top', [['top', '0']], 0, 0, 'document')
    sxptxt.whole_sectitle = top.title
    sxptxt.section_list.append(top)
    sxptxt.section_id_dict[top.id_str] = top.id
    # -- get paraset --
    sent_id = 0
    context_id = 0
    for para_id, para_txt in enumerate(paratxtlst):
        curpara = BuildsxpParaObj('top', ['top', 'p' + str(para_id)], top.title, para_id, top.id)
        curpara.para_text = para_txt
        sxptxt.paraset.append(curpara)
        context_sents = []
        # -- get each sentenceset --
        senttxtlst = nltk.sent_tokenize(para_txt)
        for senttxt in senttxtlst:
            cursent = sxpSent()
            cursent.sentence_text = senttxt
            cursent.id = sent_id
            cursent.id_para = para_id
            cursent.id_sec = top.id
            sxptxt.sentenceset.append(cursent)
            sent_id += 1
            if len(context_sents) == 0:
                context_sents.append(cursent)
            elif is_relevant(context_sents, senttxt, 0.06):
                context_sents.append(cursent)
            else:
                curcontext = BuildsxpContextObj(context_id, para_id, top.id, context_sents)
                for consent in context_sents:
                    curcontext.context_txt += consent.sentence_text + ' '
                curcontext.context_txt = curcontext.context_txt.strip()
                sxptxt.context_set.append(curcontext)
                context_id += 1
                context_sents = [cursent]
        if len(context_sents) > 0:
            curcontext = BuildsxpContextObj(context_id, para_id, top.id, context_sents)
            for consent in context_sents:
                curcontext.context_txt += consent.sentence_text + ' '
            sxptxt.context_set.append(curcontext)
            context_id += 1
    return sxptxt


def CElinksForDUC(papers_dir, sxptxt_dir):
    ### ---- get pattern list and mtRegExplist(main_token RegExp List) ----
    Patterns = Loadpickle(os.path.join(DICpkdir, 'Patterns.pk'))
    mtRegExpList = Loadpickle(os.path.join(DICpkdir, 'mtRegExpList.pk'))
    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(papers_dir)[0]
    emptyTree = Tree('ROOT', [])
    for f in file_list:
        if not re.match(ur"AP", f):
            continue
        print "*****************************************"
        print "Processing file:", f

        # -- get two sxpText objects for each file --
        pkfp = os.path.join(sxptxt_dir, f)
        filefp = os.path.join(papers_dir, f)
        sxptxt = BuildDUCsxpText(filefp)

        Sentlst = sxptxt.sentenceset
        slen = len(Sentlst)
        SentPTlst = []

        # -- get sentence list from the sxpText object which include Abstract and Conclusion in its sentence set --
        # -- for each sentence, build its Stanford-parser Tree --
        print "\tBuilding Stanford-Parser Tree List for Sentence List"
        for s in range(slen):
            print "\t\t------- Sentence: ", Sentlst[s].id, "-----------"
            senttxt = RemoveUStrSpace(Sentlst[s].sentence_text)
            # print "\t\t", type(senttxt), senttxt
            tempsentPTlst = []
            try:
                tempsentPT = parser.raw_parse(senttxt)
            except:
                pass
            try:
                while True:
                    tempsentPTlst.append(tempsentPT.next())
            except StopIteration:
                pass
            if not tempsentPTlst:
                SentPTlst.append(emptyTree)
            elif len(tempsentPTlst) == 1:
                SentPTlst.append(tempsentPTlst[0])
            else:
                SentPTlst.append(Tree('ROOT', [pt[0] for pt in tempsentPTlst]))
            # print "\t\t\t", list(SentPTlst[-1])
            print "\t\t\tComplete!"
        # -- for each sentence, using Patterns matching to get CELink object list --
        print "\t Total sentences:", slen
        curCEset = []  # a CELink object list
        for s in range(slen):
            if len(SentPTlst[s]) == 0:
                continue
            print "\t\t--------- matching sentence: ", Sentlst[s].id, "------------"
            ### we have checked that each sentence in the corpus is parsed into at most one parser-tree
            curPT = SentPTlst[s]
            prePT = emptyTree if s < 1 else SentPTlst[s - 1]
            nextPT = emptyTree if s > slen - 2 else SentPTlst[s + 1]
            sentCEset = []
            try:
                sentCEset = GettingCEcases(Patterns, mtRegExpList, prePT, curPT, nextPT)
            except:
                pass

            for sentCE in sentCEset:
                if len(sentCE.PTreelst) == 1:
                    sentCE.sInfo = [Sentlst[s]]
                elif sentCE.PTreelst[0] == curPT:
                    sentCE.sInfo = [Sentlst[s], Sentlst[s + 1]]
                else:
                    sentCE.sInfo = [Sentlst[s - 1], Sentlst[s]]

            if len(sentCEset) > 0:
                curCEset.extend(sentCEset)
            print "\t\t\tComplete!"
        # -- Write CELink object list in txt file for human checking --
        CE_txt_path = os.path.join(ductxtdir, f + "_CE.txt")
        CE_pk_path = os.path.join(ductxtdir, f + "_CE.pk")
        CEset2TXT(curCEset, CE_txt_path)
        Dumppickle(CE_pk_path, curCEset)
        # -- Add pattern CE links set -- sys_CE_list to each sxpText object
        # -- Add the dict object storing the mapping between sentence id and pattern matched CE id -- sysce_sent_id_dict
        # to each sxpText object
        PKsysCElist, PKsysce_sent_id_dict = GetSysCE(curCEset)
        sxptxt.sys_CE_list = PKsysCElist
        sxptxt.sysce_sent_id_dict = PKsysce_sent_id_dict
        # -- Add each sentence's cause-effect link id --
        for sent in Sentlst:
            if PKsysce_sent_id_dict.has_key(sent.id):
                sxptxt.sentenceset[sent.id].sysCEidlst = PKsysce_sent_id_dict[sent.id]
        # -- Change sentenceset in each sxpContext object --
        for ctxt in sxptxt.context_set:
            newctxtsent = []
            for csent in ctxt.context_sent:
                newctxtsent.append(sxptxt.sentenceset[csent.id])
            sxptxt.context_set[ctxt.id].context_sent = newctxtsent
        # -- add sentenceset to each sxpPara object --
        for sent in sxptxt.sentenceset:
            sxptxt.paraset[sent.id_para].sentenceset.append(sent)
        # -- add context_set to each sxpPara object --
        for ctxt in sxptxt.context_set:
            sxptxt.paraset[ctxt.id_para].context_set.append(ctxt)

        # ShowSxpTextFileInfo(sxptxt)
        # -- Overwrite the pickle files by new sxpText objects which add CE information --
        StoreSxptext(sxptxt, pkfp)
        WriteStrFile(os.path.join(ductxtdir, f + '_CESentIDdict.txt'), GetSysCESentIdLst(sxptxt))


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    # CheckPatternsCases()
    test = 'acl'
    if test == 'kg':
        # ------ Obtain Cause-Effect Links ------
        paperlist_pk_path = os.path.join(DICpkdir, 'KGPaperList.pk')
        CEList_pk_path = os.path.join(DICpkdir, 'KGCEList.pk')
        CElinksForKG(paperlist_pk_path, CEList_pk_path)
    if test == 'acl':
        # ------ Obtain Cause-Effect Links ------
        papers_dir = os.path.join(acl_dir, "files")
        sxptxt_dir = os.path.join(acl_dir, "pickle")
        CElinksForACL(papers_dir, sxptxt_dir)
    if test == 'duc':
        # ------ Obtain Cause-Effect Links ------
        papers_dir = os.path.join(duc_dir, "files")
        sxptxt_dir = os.path.join(duc_dir, "pickle")
        CElinksForDUC(papers_dir, sxptxt_dir)


if __name__ == "__main__":
    main()
    # for synset in wn.synsets(str):
    #     hyperset = synset.hypernyms()
    #     for hs in hyperset:
    #         hypername.extend(hs.lemma_names())
    # return hypername

############################## Some unused Function #####################################
#
### ---- Check whether the Pattern Order is stable ----
# def CheckPatternOrder(Patterns,reverse):
#     plen = len(Patterns);
#     for i in range(plen)[::-1]:
#         for j in range(i):
#             if (Patterns[j] < Patterns[i]) == reverse:
#                 return False;
#     return True;
#
# ### ------ Check sentence parser-tree -----
# def CheckSentPTinCorpus():
#     file_pk_pathlst = Get_file_pathes(os.path.join(os.getcwd(),"PK","TXT"));
#     flen = len(file_pk_pathlst);
#     errorfilepath = os.path.join(os.getcwd(),'Corpus','errorfile2.txt')
#     errorfile = codecs.open(errorfilepath,'w','utf8')
#     for fp in file_pk_pathlst:
#         curfile = Loadpickle(fp);
#         sentlist = curfile.S_list;
#         errorfile.write(curfile.Ftag+"\n");
#         print curfile.Ftag;
#         for sent in sentlist:
#             if sent.PTree == []:
#                 errorfile.write(str(sent.Stag)+":  "+sent.text+"\n");
#             if len(sent.PTree) > 1:
#                 print sent.Stag,":",sent.text;
#         errorfile.write("\n\n\n\n");
#         print "\n\n\n\n";

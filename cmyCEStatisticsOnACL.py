# -*- coding: UTF-8 -*-

#######################################################################################
# --------------------------------- Function Introduce ------------------------------ #
#######################################################################################
# This functions set intends to:
# Count cause-effect links on each section, and count the percentage of common words that occur both in CE links
# and Abstract & Conclusion section.
# 1. Count the distribution of CE cases on each section for each file:
#    (1) the name of each section;
#    (2) the number of sentences in each section;
#    (3) the number of CE cases in each section extracted by function 'CElinksForSection';
#    (4) the number of sentences that covered by CE cases in each section;
#    (5) the Sentence cover rate in each section;
# 2. Calculate the percent of common words:
#    (1) Build 'FWordDic' object for each file in corpus, please see 'cmyWordsCompare.py' for details;
#    (2) Build 'CoWords' object for each file in corpus, please see 'cmyWordsCompare.py' for details;

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import re
import sys
import nltk
import string
import operator
from nltk.tree import *
from cmyPackage import *
from xlutils.copy import copy as xlscopy


#######################################################################################
# --------------------------- Calculate Word Frequency ------------------------------ #
#######################################################################################
# ---- remove pairs in 'Dic' if their keys in 'Removelist' ----
def DicRemove(Dic, Removelist):
    for r in Removelist:
        if Dic.has_key(r): del Dic[r]
    return Dic


# ---- count the words in text and update values in 'Dic' ----
def Text2WordDic(Dic, text):
    tokens = nltk.word_tokenize(text)
    for t in tokens:
        t = t.lower()
        if not Dic.has_key(t):
            Dic[t] = 1
        else:
            Dic[t] += 1
    return Dic


#######################################################################################
# --------------- Calculate percent of common words in CE and Abs&Conc ----------------#
#######################################################################################
def GetCE_AC_CoWordsPercent(wordic):
    # ----------- Get stop words, Punctions------------
    if not os.path.isfile(os.path.join(pkdir, 'StopW.pk')):
        getStopWord()
    StopW = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
    Puncs = Loadpickle(os.path.join(pkdir, 'Puncs.pk'))
    Removelist = Puncs + StopW
    # ------------Calculate Words Similarity -----------
    # remove Punctions and StopWords from WordDics
    wordic.AbsWordDic = DicRemove(wordic.AbsWordDic, Removelist)
    wordic.ConcWordDic = DicRemove(wordic.ConcWordDic, Removelist)
    wordic.A_CWordDic = DicRemove(wordic.A_CWordDic, Removelist)
    wordic.CEWordDic = DicRemove(wordic.CEWordDic, Removelist)
    # calculate each word's rate in each Dict
    SumAWords = float(sum(wordic.AbsWordDic.values()))
    SumCWords = float(sum(wordic.ConcWordDic.values()))
    SumACWords = float(sum(wordic.A_CWordDic.values()))
    SumCEWords = float(sum(wordic.CEWordDic.values()))
    for a, av in wordic.AbsWordDic.items():
        wordic.AbsWordDic[a] = av / SumAWords
    for c, cv in wordic.ConcWordDic.items():
        wordic.ConcWordDic[c] = cv / SumCWords
    for ac, acv in wordic.A_CWordDic.items():
        wordic.A_CWordDic[ac] = acv / SumACWords
    for ce, cev in wordic.CEWordDic.items():
        wordic.CEWordDic[ce] = cev / SumCEWords
    # calculate common words proportion
    OnAbs = 0
    OnConc = 0
    OnAC = 0
    Abs2CE = 0
    Conc2CE = 0
    AC2CE = 0
    ComWOnAbs = []
    ComWOnConc = []
    ComWOnAC = []
    for a, av in wordic.AbsWordDic.items():
        if wordic.CEWordDic.has_key(a):
            OnAbs += av
            Abs2CE += wordic.CEWordDic[a]
            ComWOnAbs.append(a)
    for c, cv in wordic.ConcWordDic.items():
        if wordic.CEWordDic.has_key(c):
            OnConc += cv
            Conc2CE += wordic.CEWordDic[c]
            ComWOnConc.append(c)
    for ac, acv in wordic.A_CWordDic.items():
        if wordic.CEWordDic.has_key(ac):
            OnAC += acv
            AC2CE += wordic.CEWordDic[ac]
            ComWOnAC.append(ac)

    wAbs = 0.0 if len(wordic.AbsWordDic) == 0 else float(len(ComWOnAbs)) / len(wordic.AbsWordDic)
    wConc = 0.0 if len(wordic.ConcWordDic) == 0 else float(len(ComWOnConc)) / len(wordic.ConcWordDic)
    wAC = 0.0 if len(wordic.A_CWordDic) == 0 else float(len(ComWOnAC)) / len(wordic.A_CWordDic)

    return CoWords(wordic, OnAbs, Abs2CE, OnConc, Conc2CE, OnAC, AC2CE, wAbs, wConc, wAC, ComWOnAbs, ComWOnConc, ComWOnAC)


#######################################################################################
# --------------------------- Some demonstration functions -------------------------- #
#######################################################################################
def CESecDistribution2TXT(wfreq_txt_fp, papertest):
    RecordFile = codecs.open(wfreq_txt_fp, 'w', 'utf8')
    RecordFile.write("Current File: " + papertest.Paperinfo.fname + " " + papertest.Paperinfo.title + "\n\n")
    for CESec in papertest.CESeclst:
        RecordFile.write("Section %d: " % CESec.Ctag + CESec.Ctitle + "\n")
        RecordFile.write("\tSentNum: %d" % len(CESec.Slist) + "\n")
        RecordFile.write("\tCENum: %d" % len(CESec.CElist) + "\n")
        RecordFile.write("\tSentCovered: %d" % len(CESec.CEsent) + "\n")
        RecordFile.write("\tCovered_Rate: %.4f" % (
            float(len(CESec.CEsent)) * 100 / len(CESec.Slist) if len(CESec.Slist) > 0 else 0) + "%\n\n")
    RecordFile.write("#-------------------------------------------------\n\n")

    RecordFile.write("####################### CE links on each Section #########################\n\n")
    RecordFile.write(papertest.Paperinfo.fname + "'s CE cases\n\n")
    for CESec in papertest.CESeclst:
        RecordFile.write("Section %d: " % CESec.Ctag + CESec.Ctitle + " has %d CE cases\n" % len(CESec.CElist))
        for idx, ce in enumerate(CESec.CElist):
            RecordFile.write("\tCASE: %d\n" % (idx + 1))
            RecordFile.write("\tStag: ")
            for sid in ce.Staglst:
                RecordFile.write("%d " % sid)
            RecordFile.write("\n")
            RecordFile.write(
                "\t\tPattern: " + '%d' % ce.pt.pfreq + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
            RecordFile.write("\t\tsentTXT: ")
            for sid in ce.Staglst:
                RecordFile.write(papertest.Paperinfo.sentenceset[sid].sentence_text + '. ')
            RecordFile.write("\n")
            RecordFile.write("\t\tCause: " + str(ce.cw_span) + '\n')
            RecordFile.write("\t\tEffect: " + str(ce.ew_span) + '\n\n')
    RecordFile.write("#-------------------------------------------------\n\n")


def CESecDistribution2Xls(sysce_sec_xlsxfp, papertest):
    oldWB = xlrd.open_workbook(sysce_sec_xlsxfp, formatting_info=True)
    WB = xlscopy(oldWB)
    WS = WB.add_sheet(papertest.Paperinfo.fname + "_SysCEonSec", cell_overwrite_ok='True')
    TitleRow = ['Section ID', 'Section Title', 'SentNum', 'CENum', 'SentCovered', 'Covered_Rate(%)']
    for j in range(len(TitleRow)):
        WS.write(0, j, TitleRow[j], xlwt.easyxf('font: bold on'))
    for j, CESec in enumerate(papertest.CESeclst):
        WS.write(j + 1, 0, "%d" % CESec.Ctag)
        WS.write(j + 1, 1, CESec.Ctitle)
        WS.write(j + 1, 2, "%d" % len(CESec.Slist))
        WS.write(j + 1, 3, "%d" % len(CESec.CElist))
        WS.write(j + 1, 4, "%d" % len(CESec.CEsent))
        WS.write(j + 1, 5, "%.4f" % (float(len(CESec.CEsent)) * 100 / len(CESec.Slist) if len(CESec.Slist) > 0 else 0))
    WB.save(sysce_sec_xlsxfp)

def CoWords2TXT(wfreq_txt_fp, cowords):
    CoWordTXT = codecs.open(wfreq_txt_fp, 'w', 'utf8')
    CoWordTXT.write((cowords.FWDic).Ftag + "\n")
    CoWordTXT.write("OnAbs: %.4f" % (cowords.OnAbs * 100) + "%\n")
    CoWordTXT.write("OnConc: %.4f" % (cowords.OnConc * 100) + "%\n")
    CoWordTXT.write("OnAC: %.4f" % (cowords.OnAC * 100) + "%\n")
    CoWordTXT.write("Abs2CE: %.4f" % (cowords.Abs2CE * 100) + "%\n")
    CoWordTXT.write("Conc2CE: %.4f" % (cowords.Conc2CE * 100) + "%\n")
    CoWordTXT.write("AC2CE: %.4f" % (cowords.AC2CE * 100) + "%\n")
    CoWordTXT.write("WAbs: %.4f" % (cowords.WAbs * 100) + "%\n")
    CoWordTXT.write("WConc: %.4f" % (cowords.WConc * 100) + "%\n")
    CoWordTXT.write("WAC: %.4f" % (cowords.WAC * 100) + "%\n")
    CoWordTXT.write("ComWOnAbs: \n")
    CoWordTXT.write(str(cowords.ComWOnAbs) + "\n")
    CoWordTXT.write("ComWOnConc:  \n")
    CoWordTXT.write(str(cowords.ComWOnConc) + "\n")
    CoWordTXT.write("ComWOnAC:  \n")
    CoWordTXT.write(str(cowords.ComWOnAC) + "\n")
    CoWordTXT.write("#-------------------------------------------------\n\n\n")


def CoWordLst2XLS(CoWordXlsfp, CoWordLst):
    WB = xlwt.Workbook(encoding='utf-8')
    WS = WB.add_sheet('Sys_CE_AC_CoWord', cell_overwrite_ok='True')
    # ------------------Creat sheet WS0-------------------
    TitleRow = ['Ftag', 'OnAbs', 'OnConc', 'OnAC', 'Abs2CE', 'Conc2CE', 'AC2CE', 'WAbs', 'WConc', 'WAC']
    for i in range(len(TitleRow)):
        WS.write(0, i, TitleRow[i], xlwt.easyxf('font: bold on'))
    for i, cowords in enumerate(CoWordLst):
        WS.write(i + 1, 0, (cowords.FWDic).Ftag)
        WS.write(i + 1, 1, "%.4f" % (cowords.OnAbs * 100))
        WS.write(i + 1, 2, "%.4f" % (cowords.OnConc * 100))
        WS.write(i + 1, 3, "%.4f" % (cowords.OnAC * 100))
        WS.write(i + 1, 4, "%.4f" % (cowords.Abs2CE * 100))
        WS.write(i + 1, 5, "%.4f" % (cowords.Conc2CE * 100))
        WS.write(i + 1, 6, "%.4f" % (cowords.AC2CE * 100))
        WS.write(i + 1, 7, "%.4f" % (cowords.WAbs * 100))
        WS.write(i + 1, 8, "%.4f" % (cowords.WConc * 100))
        WS.write(i + 1, 9, "%.4f" % (cowords.WAC * 100))

    WB.save(CoWordXlsfp)

#######################################################################################
# ---------------------- Statistic for each paper in corpus ------------------------- #
#######################################################################################
def PaperTestObjectLst(TextPKfp, PaperTestPKfp, fnameRegx=re.compile(r".+"), ceopt="sysce"):
    print "****************************************************************"
    print "\t\tCount Section-Distribution & Word-Frequency"
    print "****************************************************************"
    PaperTestList = []
    fnamelist = os.listdir(TextPKfp)

    for fname in fnamelist:
        # -- If current file name does not fit the file name filter, skip it --
        if not fnameRegx.match(fname):
            continue

        print "-----------------------------------------------"
        sxptxt = LoadSxptext(os.path.join(TextPKfp, fname))  # current file's 'sxpText' object;
        print "Current file:", sxptxt.fname

        # -- add section level into each sxpSectionTitle object within current sxptxt object -------
        for cidx, sec in enumerate(sxptxt.section_list):
            if sec.id_set == [['top', '0']]:
                continue
            sxptxt.section_list[cidx].level = len(sec.id_set)
        StoreSxptext(sxptxt, os.path.join(TextPKfp, fname))

        # -- Get PaperTest object for current sxptxt object -------
        print "\t -- Get PaperTest object for current file.. --"
        curpapertest = PaperTest(sxptxt)  # current file's 'PaperTest()' object;
        # ---- Build CEonSec object list for each sections for current file ----
        print "\t\tCreate CEonSec object list"
        curpapertest.CESeclst = GetCEonSecLst(sxptxt, ceopt=ceopt)
        # ---- Build FText object and append it into FTextList ----
        print "\t\tCreate FText object"
        curpapertest.ftext = GetFText(sxptxt, ceopt=ceopt)
        # ---- Build 'FWordDic' object as current file's CE_AC Word Dictionary -- CE_AC_WDic ----
        print "\t\tCreate CE_AC_WDic object"
        curpapertest.CE_AC_WDic = GetFWordDict(curpapertest.ftext)
        # ---- Build 'CoWords' object as current file's CE_AC Common Word ratio -- CE_AC_CoWord ----
        print "\t\tCreate CE_AC_CoWord object"
        curpapertest.CE_AC_CoWord = GetCE_AC_CoWordsPercent(curpapertest.CE_AC_WDic)

        StoreSxptext(curpapertest, os.path.join(PaperTestPKfp, fname))
        PaperTestList.append(curpapertest)

    return PaperTestList


def GetCEonSecLst(sxptxt, ceopt="sysce"):
    curCESecList = []  # The list of CEonSec objects, contains first level section, such as "section 1", "section 2", "section 3" ...
    curSlist = sxptxt.sentenceset  # current file's sent list;
    print "\t\t\tNumber of sentences:", len(curSlist)
    curCEset = []
    if ceopt == "sysce":
        curCEset = sxptxt.sys_CE_list  # current file's extracted CE links set
    elif ceopt == "mance":
        curCEset = sxptxt.man_CE_list  # current file's extracted CE links set
    print "\t\t\tNumber of CE links:", len(curCEset)
    # -- Check the correspondence between CE id and its sentence id list --
    # for ce in curCEset:
    #     print "\t\t", ce.sysCEid, ce.Staglst

    # -- step 1: Initialization current file's CEonSec list with each Section's Ctag and Ctitle.
    #            and sort the CEonSec list by its elements' Ctag value in ascending order. --
    Ctag = 0  # the first level section index for building curCESecList --
    SecID2CtagDict = {} # the dict mapping sxpSectionTitle object's id to first level section index in curCESecList --
    for cursec in sxptxt.section_list:
        # -- if current section is 'top' or "acknowledgments" or "references" section, skip it --
        if cursec.level == 0:
            continue
        if re.match(u"acknowledgments", cursec.title.strip().lower()):
            continue
        if re.match(u"references", cursec.title.strip().lower()):
            continue

        # -- if current section is first-level section, new CEonSec object for it --
        if cursec.level == 1:
            curCESecList.append(CEonSec(Ctag, cursec.title))
            Ctag += 1

        # -- if current section is normal section, add SecID2CtagDict element --
        SecID2CtagDict[cursec.id] = curCESecList[-1].Ctag
    # -- Check the mapping between section id and its Ctag index --
    # for cesec in curCESecList:
    #     print "\t\t\t", cesec.Ctag, cesec.Ctitle
    # for sec in sxptxt.section_list:
    #     if SecID2CtagDict.has_key(sec.id):
    #         print "\t\t\t", SecID2CtagDict[sec.id], sec.id, sec.title

    # -- step 2: fill each CEonSec object's sent list. --
    for s in curSlist:
        if not SecID2CtagDict.has_key(s.id_sec):
            continue
        curCESecList[SecID2CtagDict[s.id_sec]].Slist.append(s)
    # -- Check the sentences list in current CEonSec object --
    # for curcesec in curCESecList:
    #     print "\t\t\t", curcesec.Ctag, curcesec.Ctitle
    #     for s in curcesec.Slist:
    #         print "\t\t\t\t", s.id, s.sentence_text

    #-- step 3: fill each CEonSec object's CE list and CEsent list (the sent set construct its CE list);
    #           Notice that we suppose there is no CE case skip two adjacent sections.
    #           So, we use the CE case's first sent's Sec_id as the CE case's Sec_id. --
    SentVisit = [False] * len(curSlist)  # SentVisit: avoid re-add a sent into 'CEonSec' object's CE links list;
    for ce in curCEset:
        # -- if current ce link has no sentence id list, skip it --
        if len(ce.Staglst) == 0:
            continue
        # -- add ce link and its sentences into the corresponding CEonSec object --
        secid = curSlist[ce.Staglst[0]].id_sec
        if SecID2CtagDict.has_key(secid):
            Ctag = SecID2CtagDict[secid]
            curCESecList[Ctag].CElist.append(ce)
            for sid in ce.Staglst:
                if not SentVisit[sid]:
                    SentVisit[sid] = True
                    curCESecList[Ctag].CEsent.append(curSlist[sid])
    # -- Check the cause-effect sentences list in current CEonSec object --
    # for cesec in curCESecList:
    #     print "\t\t\t", cesec.Ctag, cesec.Ctitle
    #     for cesent in cesec.CEsent:
    #         print "\t\t\t\t", cesent.id, cesent.sentence_text

    # step 4: sort the Slist and CEsent list for each CEonSec object by their 'id' value in ascending order
    for j in range(len(curCESecList)):
        curCESecList[j].Slist.sort(key=operator.attrgetter('id'))
        curCESecList[j].CEsent.sort(key=operator.attrgetter('id'))

    return curCESecList


def GetFText(sxptxt, ceopt="sysce"):
    # ---- Abstract sentences text list ----
    AbsText = sxptxt.abstract.split("**.\n")
    # for abs in AbsText:
    #     print abs

    # ---- Conclusion sentences text list ----
    ConcText = sxptxt.conclusion.split("**.\n")
    # for conc in ConcText:
    #     print conc

    # ---- CE cases sentences text list ----
    CEText = []
    CESentIdLst = sxptxt.sysce_sent_id_dict.keys()
    if ceopt == "mance":
        CESentIdLst = sxptxt.mance_sent_id_dict.keys()
    CESentIdLst.sort()
    for sid in CESentIdLst:
        CEText.append(sxptxt.sentenceset[sid].sentence_text)
        # print sid, sxptxt.sentenceset[sid].sentence_text

    # ---- Build FText object and append it into FTextList ----
    return FText(sxptxt.fname, AbsText, ConcText, CEText)


def GetFWordDict(ftxt):
    AbsText = ftxt.AbsText
    ConcText = ftxt.ConcText
    CEText = ftxt.CEText
    # ---- Abstract Word Dictionary ----
    AbsWordDic = {}
    for text in AbsText:
        AbsWordDic = Text2WordDic(AbsWordDic, text)
    # ---- Conclusion Word Dictionary ----
    ConcWordDic = {}
    for text in ConcText:
        ConcWordDic = Text2WordDic(ConcWordDic, text)
    # ---- CE cases Word Dictionary ----
    CEWordDic = {}
    for text in CEText:
        CEWordDic = Text2WordDic(CEWordDic, text)
    # ---- Abstract & Conclusion union Word Dictionary ----
    A_CWordDic = AbsWordDic.copy()
    for k, v in ConcWordDic.items():
        if A_CWordDic.has_key(k):
            A_CWordDic[k] = A_CWordDic[k] + v
        else:
            A_CWordDic[k] = v

    return FWordDic(ftxt.Ftag, AbsWordDic, ConcWordDic, A_CWordDic, CEWordDic)

#######################################################################################
# -------------------------------- Control Functions -------------------------------- #
#######################################################################################
def GetPaperTestLst(key, ceopt, homedir):
    fnameRegx = re.compile(r"^P14-\d+\.xhtml_2.pickle$")
    if key == "kg":
        fnameRegx = re.compile(r"^f\d+\.txt_2.pk$")

    sxpTextPKfp = os.path.join(homedir, "pickle")
    if not os.path.isdir(sxpTextPKfp):
        return

    PaperTestPKfp = os.path.join(homedir, "TempPKFiles", "PaperTestObject")
    if not os.path.isdir(PaperTestPKfp):
        os.mkdir(PaperTestPKfp)

    papertestlst = PaperTestObjectLst(sxpTextPKfp, PaperTestPKfp, fnameRegx, ceopt=ceopt)
    StoreSxptext(papertestlst, os.path.join(homedir, "TempPKFiles", "PaperTestLst.pk"))
    return papertestlst


def ConvertResult2TXTXls(homedir, papertestlst):
    statistic_txtxlsx_fp = os.path.join(homedir, "Statistic_TxtXlsx_Files")
    if not os.path.isdir(statistic_txtxlsx_fp):
        os.mkdir(statistic_txtxlsx_fp)

    sysce_sec_xlsxfp = os.path.join(statistic_txtxlsx_fp, "SysCEonSection.xls")
    book = xlwt.Workbook(encoding='utf-8')
    book.add_sheet('Sheet 1')
    book.save(sysce_sec_xlsxfp)

    CoWordXlsfp = os.path.join(statistic_txtxlsx_fp, "SysCE_CoWord.xls")
    CoWordLst = []

    for papertest in papertestlst:
        sysce_sec_txtfp = os.path.join(statistic_txtxlsx_fp, papertest.Paperinfo.fname+"_sysCEonSec.txt")
        CESecDistribution2TXT(sysce_sec_txtfp, papertest)
        CESecDistribution2Xls(sysce_sec_xlsxfp, papertest)
        wfreq_txtfp = os.path.join(statistic_txtxlsx_fp, papertest.Paperinfo.fname+"_CoWords.txt")
        CoWords2TXT(wfreq_txtfp, papertest.CE_AC_CoWord)
        CoWordLst.append(papertest.CE_AC_CoWord)

    CoWordLst2XLS(CoWordXlsfp, CoWordLst)


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
if __name__ == "__main__":
    key = "acl"
    ceopt = "sysce"

    homedir = acl_dir
    if key == "kg":
        homedir = kg_dir

    papertestlst = GetPaperTestLst(key, ceopt, homedir)
    # papertestlst = LoadSxptext(os.path.join(homedir, "TempPKFiles", "PaperTestLst.pk"))
    ConvertResult2TXTXls(homedir, papertestlst)

    # pkfp = r"E:\Programs\Eclipse\CE_relation\CEsummary_new\acl\pickle\P14-1008.xhtml_2.pickle"
    # sxptxt = LoadSxptext(pkfp)
    # for sec in sxptxt.section_list:
    #     print sec.id, sec.id_set, sec.level, sec.title
    # print sxptxt.abstract
    # print sxptxt.conclusion

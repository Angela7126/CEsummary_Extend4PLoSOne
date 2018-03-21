# -*- coding: UTF-8 -*-

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
# ----------- Original Sentence Ranking Models --------------
from Model_CEfliter.graph_base import GraphBased
from Model_CEfliter.MyModel import MyModel
from Model_CEfliter.MySecContextModel import SecConTextModel
from Model_CEfliter.MySecModel import MySecModel
from Model_CEfliter.MySecTitleNetwork import MySecTitleModel
from Model_CEfliter.sxpContextModel import conTextModel
from Model_CEfliter.sxpHybridGraph import HybridGraph
from Model_CEfliter.tf_idf import TfIdf
from Model_CEfliter.word_graph import WordGraph
# ----------------- CEBias Models --------------------------
from Model_CEbias.MyModel2 import MyModel2
from Model_CEbias.MySecModel2 import MySecModel2
from Model_CEbias.MySecTitleNetwork2 import MySecTitleModel2
from Model_CEbias.graph_base2 import GraphBased2
from Model_CEbias.sxpContextModel2 import conTextModel2
from Model_CEbias.sxpHybridGraph2 import HybridGraph2
from Model_CEbias.tf_idf2 import TfIdf2
from Model_CEbias.word_graph2 import WordGraph2
from Model_CEbias.MySecContextModel2 import SecConTextModel2
# ----------------- CEIter Models --------------------------
from Model_CEiter.MyModel3 import MyModel3
from Model_CEiter.MySecModel3 import MySecModel3
from Model_CEiter.MySecTitleNetwork3 import MySecTitleModel3
from Model_CEiter.sxpContextModel3 import conTextModel3
from Model_CEiter.sxpHybridGraph3 import HybridGraph3
from Model_CEiter.MySecContextModel3 import SecConTextModel3

from sxpPackage import *
from cmyToolkit import *
from cmyDoTestPyrouge import *
from cmySecCEIntensity import cmySecCE
import networkx as nx
import math
from bs4 import BeautifulSoup

# ------------ some dict object ---------------
idname = {'mymodel': '01', 'tfidf': '02', 'graphb': '03', 'graphw': '04', 'context1': '05', 'mysecmodel': '06',
          'myseccontextmodel': '07', 'hybrid': '08', 'sectitle': '09', 'mymodel2': '41', 'tfidf2': '42',
          'graphb2': '43', 'graphw2': '44', 'context2': '45', 'mysecmodel2': '46', 'myseccontextmodel2': '47',
          'hybrid2': '48', 'sectitle2': '49', 'mymodel3': '51', 'context3': '55', 'mysecmodel3': '56',
          'myseccontextmodel3': '57', 'hybrid3': '58', 'sectitle3': '59'}


#######################################################################################
# ----------------- Get comparing summaries and write html files -------------------- #
#######################################################################################
def ProduceSystem(tops, fn, formatsent=0):
    modeltxt = '''<html>\n<head>\n<title>%s</title>\n</head>\n''' % (fn)
    # ---- get sentences list ----
    if type(tops) != list:
        if type(tops) != str and type(tops) != unicode:
            if formatsent == 1:
                return modeltxt
            else:
                return ""
        tops = re.split("(?<=[\.|?|!|;|:])[ |\"]+", tops.strip())
    # ---- change sentences into some format ----
    abstract_str = ''
    for i, sent in enumerate(tops):
        rsent = RemoveUStrSpace(sent)
        if len(rsent) <= 0:
            rsent = 'test sentence is empty'
        if formatsent == 1:
            sentr = '''<a name="%d">[%d]</a> <a href="#%d" id=%d>%s</a>\n''' % (i, i, i, i, rsent)
        if formatsent == 0:
            sentr = rsent + '\n'
        abstract_str += sentr
    # ---- get body text ----
    if formatsent == 1:
        bodytxt = '''<body bgcolor="white">\n%s</body>\n</html>''' % (abstract_str)
    if formatsent == 0:
        bodytxt = abstract_str
    # ---- get whole text and return ----
    if formatsent == 1:
        abstract_str = modeltxt + bodytxt
    if formatsent == 0:
        abstract_str = bodytxt
    return abstract_str


def ProduceModelTemplate(dict, fpdir):
    bodytxt = '''<body bgcolor="white">\n'''
    for id in range(28):
        bodytxt += '''<a name="%s">[%i]</a> <a href="#%s" id=%i></a>\n''' %(id, id, id, id)
    bodytxt += '''</body>\n</html>'''
    for key in dict.keys():
        for secid in dict[key]:
            for tp in ['A','B']:
                fp = os.path.join(fpdir, '.'.join([key, secid, tp, 'html']))
                modeltxt = '''<html>\n<head>\n<title>%s</title>\n</head>\n''' % ('.'.join([key, secid]))
                abstract_str = modeltxt + bodytxt
                WriteStrFile(fp, abstract_str, 'utf-8')



def GetComparingTextLength(model_path):
    fname_topk_dict = {}
    fname_maxstr_dict = {}
    # -- get the model filename list in the path variable --
    file_list = sxpGetDirFileList(model_path)[0]
    print "Preparing comparing text complete"
    # --  get sxpText objects --
    for i, file_name in enumerate(file_list):
        print file_name,

        fset = file_name.split('.')
        fname_secname = '.'.join(fset[0:3])
        if not fset[-1] == 'html' or not re.match(ur'f\d{4}\.txt\..*', fname_secname):
            print "not satisfy requirement of file name!"
            continue

        file_strlen = 0
        file_sentlen = 0
        model_fp = os.path.join(model_path, file_name)

        soup = BeautifulSoup(open(model_fp), "html.parser")
        for a in soup.find_all('a'):
            if a.attrs.has_key('href') and len(a.text) > 2:
                file_sentlen += 1
                file_strlen += len(a.text)

        if file_sentlen > 0 and file_strlen > 0:
            if fname_secname in fname_topk_dict.keys():
                fname_topk_dict[fname_secname].append(file_sentlen)
            else:
                fname_topk_dict[fname_secname] = [file_sentlen]
            if fname_secname in fname_maxstr_dict.keys():
                fname_maxstr_dict[fname_secname].append(file_strlen)
            else:
                fname_maxstr_dict[fname_secname] = [file_strlen]
        print "processed"

    for key in fname_topk_dict.keys():
        fname_topk_dict[key] = math.ceil(float(sum(fname_topk_dict[key])) / len(fname_topk_dict[key]))
    for key in fname_maxstr_dict.keys():
        fname_maxstr_dict[key] = math.ceil(float(sum(fname_maxstr_dict[key])) / len(fname_maxstr_dict[key]))

    return fname_topk_dict, fname_maxstr_dict


#######################################################################################
# -------------------- Ranking for each section pickle file ------------------------- #
#######################################################################################
# ---- evaluate_one_kg_file function : ---- #
# Input:
#   1. fp: the sxpText object pickles directory
#   2. modeltype: a string belongs to ['mymodel', 'tfidf', 'graphb', 'graphw', 'context1', 'mysecmodel', 'myseccontextmodel', 'hybird', 'sectitle']
#   3. topksent: the number of sentences that you want to produced as a summary, default as 10
#   4. useabstr: belongs to [1,2,3], indicate the comparing text type
#               useabstr = 1: use abstract as comparing text
#               useabstr = 2: use conclusion as comparing text
#               useabstr = 3: use abstract + conclusion as comparing text
#   5. maxtxt: belongs to [-1, 0], used as a parameter in output top k sentence:
#               maxtxt = -1 means the length of str in output sentence set is upper bounded by the length of str in its abstraction or conclusion
#               maxtxt = 0 means the number of output sentences is upper bounded by input topksent
#   6. inc_abscon: a bool variable, indicate check the sxpText add abs&conc in its paragraph and sentence set or not added, default as True
# Output:
#   save the top k sentences in a text file at system_path + system_name + system_id
#   save all ranked sentences in a pickle file at system_path + system_name + system_id + "allsent.pk"
def evaluate_all_kg_sec(system_path, pk_path, modeltype='mymodel', ce_opt='mance', bias=0.65, fname_topk_dict={},
                        fname_maxstr_dict={}, useabstr=0, maxstr=2500, topk=25):
    print "model type =", modeltype
    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(pk_path)[0]

    # -- for each file, get its sxpText and run modeltype ranking model on it --
    for i, file_name in enumerate(file_list):
        # ---- get file name ----
        fset = file_name.split('.')
        fname = '.'.join(fset[0:2])
        secname = fset[2]
        if fset[-1] != 'pk':  # if current file is not a pickle file, it is not one of the original papers
            continue

        # ---- Get system summaries directory ----
        system_dir = os.path.join(system_path, fname, secname)
        if not os.path.exists(system_dir):
            os.makedirs(system_dir)

        # ---- get the upper bound of a system summary's str number ----
        if fname_maxstr_dict.has_key(fname + '.' + secname):
            maxstr = fname_maxstr_dict[fname + '.' + secname]
        if fname_topk_dict.has_key(fname + '.' + secname):
            topk = fname_topk_dict[fname + '.' + secname]

        print "processing", i, "th paper named as", file_name
        # -- get single pickle file directory --
        pickle_path = os.path.join(pk_path, file_name)
        # ----------- Original Sentence Ranking Models --------------
        if modeltype == 'mymodel':
            model = MyModel(pickle_path)
        if modeltype == 'tfidf':
            model = TfIdf(pickle_path)
        if modeltype == 'graphb':
            model = GraphBased(pickle_path)
        if modeltype == 'graphw':
            model = WordGraph(pickle_path)
        if modeltype == 'context1':
            model = conTextModel(pickle_path)
        if modeltype == 'mysecmodel':
            model = MySecModel(pickle_path)
        if modeltype == 'myseccontextmodel':
            model = SecConTextModel(pickle_path)
        if modeltype == 'hybrid':  # sxpHybridGraph.py
            model = HybridGraph(pickle_path)
        if modeltype == 'sectitle':  # MySecTitleNetwork.py
            model = MySecTitleModel(pickle_path)
        # --------------- CEBias Ranking Models -------------------
        if modeltype == 'mymodel2':
            model = MyModel2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'tfidf2':
            model = TfIdf2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'graphb2':
            model = GraphBased2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'graphw2':
            model = WordGraph2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'context2':
            model = conTextModel2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'mysecmodel2':
            model = MySecModel2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'myseccontextmodel2':
            model = SecConTextModel2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'hybrid2':  # sxpHybridGraph.py
            model = HybridGraph2(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'sectitle2':  # MySecTitleNetwork.py
            model = MySecTitleModel2(pickle_path, opt=ce_opt, bias=bias)
        # --------------- CEIter Ranking Models -------------------
        if modeltype == 'mymodel3':
            model = MyModel3(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'context3':
            model = conTextModel3(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'mysecmodel3':
            model = MySecModel3(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'myseccontextmodel3':
            model = SecConTextModel3(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'hybrid3':  # sxpHybridGraph.py
            model = HybridGraph3(pickle_path, opt=ce_opt, bias=bias)
        if modeltype == 'sectitle3':  # MySecTitleNetwork.py
            model = MySecTitleModel3(pickle_path, opt=ce_opt, bias=bias)

        # -- get the .html file's suffix NO. --
        if modeltype in idname.keys():
            idstr = idname[modeltype]

        # -- save original model ranked topk sentences to text --
        topksent_path = os.path.join(system_dir, fname + '.' + secname + '.html.' + idstr)
        topksent_path_2 = os.path.join(system_dir, fname + '.' + secname + '.html.sent.' + idstr)
        tops = model.OutPutTopKSent(topk, useabstr, maxstr)
        st = ProduceSystem(tops, fname + '.' + secname, 1)
        if useabstr < 0:
            WriteStrFile(topksent_path_2, st, 'utf-8')
        else:
            WriteStrFile(topksent_path, st, 'utf-8')

    print "ranking complete"


#######################################################################################
# ------------------- ranking sentences and create pickle files --------------------- #
#######################################################################################
def RankOnKGSec_GetModSysFiles(model_path, system_path, pk_path,  ce_opt='mance', bias=0.65, abstr=0, maxstr=2500, topk=20):
    # ---- Prepare comparing text ----
    # (fname_topk_dict, fname_maxstr_dict) = GetComparingTextLength(model_path)
    # print fname_topk_dict
    # print fname_maxstr_dict
    # Dumppickle(os.path.join(DICpkdir, 'KGsec_topk_dict.pk'), fname_topk_dict)
    # Dumppickle(os.path.join(DICpkdir, 'KGsec_maxstr_dict.pk'), fname_maxstr_dict)
    fname_topk_dict = Loadpickle(os.path.join(DICpkdir, 'KGsec_topk_dict.pk'))
    fname_maxstr_dict = Loadpickle(os.path.join(DICpkdir, 'KGsec_maxstr_dict.pk'))
    model_type_lst = idname.keys()
    for model_type in model_type_lst:
        evaluate_all_kg_sec(system_path, pk_path, model_type, ce_opt, bias, fname_topk_dict, fname_maxstr_dict, abstr, maxstr, topk)

def EvaluateCEsec(model_path, system_path, pk_path, mpt, spt, fh):
    fname_secstr_dict = {}
    file_list = sxpGetDirFileList(pk_path)[0]
    for file_name in file_list:
        fset = file_name.split('.')
        fname = '.'.join(fset[0:2])
        secname = fset[2]
        if fname in fname_secstr_dict.keys():
            fname_secstr_dict[fname].append(secname)
        else:
            fname_secstr_dict[fname] = [secname]

    system_dir = []
    for key in fname_secstr_dict.keys():
        for secstr in fname_secstr_dict[key]:
            system_dir.append(os.path.join(system_path, key, secstr))
    system_idlst = [
        ['01', '02', '03', '04', '05', '06', '07', '08', '09', '41', '42', '43', '44', '45', '46', '47', '48', '49'],
        ['01', '05', '06', '07', '08', '09', '41', '45', '46', '47', '48', '49'],
        ['01', '05', '06', '07', '08', '09', '51', '55', '56', '57', '58', '59']]
    TestCallKGSec(model_path, system_dir, system_idlst, mpt, spt, fh)


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    # ------------ Pickle & Model summaries & System summaries Directory ------------
    pk_path = os.path.join(kg_dir, 'pickle_SecCE')
    model_path = os.path.join(kg_dir, 'model_section_html')
    system_path = os.path.join(kg_dir, 'system_section_mance_html')
    # system_path = os.path.join(kg_dir, 'system_section_sysce_html')
    # system_path = os.path.join(kg_dir, 'system_section_mance_temp_html')
    # system_path = os.path.join(kg_dir, 'system_section_sysce_temp_html')
    # ------------ Model summaries & System summaries pattern ------------------
    mpt = r'f#ID#\.[A-Z]\.html'
    spt = r'^f([a-z|\d|\.]+)\.html(?!\.sent)'
    # spt = r'^f([a-z|\d|\.]+)\.html\.sent'
    # ------------ Prefix of intermediate files -----------------
    fh = 'KGSec_'
    # fh = 'KGSec_sent_'
    # ------------ Parameters Control cause-effect links used --------------
    ce_opt = 'mance'
    # ce_opt = 'sysce'
    bias = 0.65
    # ------------ Parameters Control the length of system summaries ------------
    abstr = 0
    maxstr = 2500
    topk = 25

    RankOnKGSec_GetModSysFiles(model_path, system_path, pk_path, ce_opt, bias, abstr, maxstr, topk)
    EvaluateCEsec(model_path, system_path, pk_path, mpt, spt, fh)


if __name__ == '__main__':
    main()
    # ProduceModelTemplate()
    # model_fp = r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\systemBias_0.1_1\f0001.txt.html.01'
    # soup = BeautifulSoup(open(model_fp), "html.parser")
    # file_sentlen = 0
    # file_strlen = 0
    # for a in soup.body.find_all('a'):
    #     if a.attrs.has_key('href') and len(a.text) > 2:
    #         file_sentlen += 1
    #         file_strlen += len(a.text)
    # print file_sentlen
    # print file_strlen
    # fname_secstr_dict = Loadpickle(os.path.join(DICpkdir, 'KGFname_SecStrlst_dict.pk'))
    # ProduceModelTemplate(fname_secstr_dict, r'E:\Programs\Eclipse\CE_relation\CEsummary\kg\temp')

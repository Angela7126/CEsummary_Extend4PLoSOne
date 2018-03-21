# -*- coding: UTF-8 -*-

# -----------------------------------------------------------------------------------------------
# Name:        cmyRougeConfig  (rewrite from sxpRougeConfig.py)
# Purpose:
#       Generate or Operate the config information for sentence ranking and ROUGE evaluation
#
# Definition of variables:
# 1. conf_name: means config name, describs specific ranking and evaluation requirement, contains:
#               1.1 corpus name, such as 'kg', 'acl', 'duc'
#               1.2 whether sentences of Abstract and Conclusion are added in sentences set,
#                   such as 'inc'(include) and 'exc'(exclude)
#               1.3 whether consider stopwords in sentence ranking, 'withstop' and 'withoutstop'
#               1.4 The metrics for the length of generated summaries, such as "maxword" and "topk"
# 2. conf_dict: means the dict object storing the config informations. Contains:
#               u'NameID': The total ranking models' name_to_ID dict
#               u'config_name': the prefix of name for ROUGE evaluation files.
#               u'dataroot': the corpus' root directory
#               u'outdir': the ROUGE evaluation files' direcotry
#               u"pickle_path": the directory which stores the sxpText object pickle files
#               u"celstpk_path": the directory for 'CELink' objects (see cmyPackage.py) list for each paper.
#               u"model_path": the direcotry which stores the model summaries
#               u"system_path": the direcotry which stores the system summaries
#               u'useabstr': whether we use abstract and conclusion in ranking process
#               u'maxword': the max words of the automatically generated summaries
#               u'strictmax': whether we want the length of automatically generated summaries
#                             strictly obey to 'maxword'
#               u'topksent': the number of sentences we extracted to generate summarise
#                            according to their ranking scores
#               u'remove_stopwords': whether we consider stopwords in ranking process
#               u'plotwho':
#               u'system_modelid_list': The list of model IDs that we want to evaluate
#               u'modelpattern': the regular expression pattern of file name of standard summarizes
#               u'systempattern': the regular expression pattern of file name of automatically
#                                 generated summarizes, it will extract model ID.
#               u'model_filenames_pattern_id': the regular expression pattern of file name of
#                                              standard summarizes, it will extract model IDs.
#               u'system_filename_pattern_id': the regular expression pattern of file name
#                                              of automatically generated summarizes.
#               u'pickle_file_pattern_id': the regular expression pattern of file name of
#                                           sxpText pickle file
#
# -----------------------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import sys
import numpy as np
import xlrd
import xlsxwriter
# import cmyParseRougeScore
from cmyToolkit import *
# --------- set some folder path ------------------
corpdir = os.path.join(os.getcwd(), "Corpus")
pkdir = os.path.join(os.getcwd(), "PK")
DICpkdir = os.path.join(pkdir, "DIC")

kg_dir = os.path.join(os.getcwd(), "kg")
acl_dir = os.path.join(os.getcwd(), "acl")
duc_dir = os.path.join(os.getcwd(), "duc")


#######################################################################################
# ------------------------- Sentence ranking models Names & ID ---------------------- #
#######################################################################################
# ---- Sentences ranking models' name_to_id dictionary ----
NameID = {#---------------------- Original models -------------------------
          'keyword':'00','Para':'01', 'TFIDF':'02', 'SimGraph':'03',
          'WordGraph':'04','ParaCtx':'05', 'SecPara':'06',
          'SecParaCtx':'07','Hybird':'08', 'SecTitle':'09',
          #-------------------- CE Pure models -------------------------
          'MCESimGraph':'10', 'SCESimGraph':'11', 'MCELocPosSeq':'12', 'SCELocPosSeq':'13',
          'MCELocNegSeq':'14', 'SCELocNegSeq':'15','MCESecLocPosSeq':'16', 'SCESecLocPosSeq':'17',
          'MCESecLocNegSeq':'18', 'SCESecLocNegSeq':'19', 'MCETFIDF':'20', 'SCETFIDF':'21',
          #------------ Manually Annotated Cause-effect Filter models ------------------
          'MCEFilter_Para':'41', 'MCEFilter_TFIDF':'42', 'MCEFilter_SimGraph':'43',
          'MCEFilter_WordGraph':'44', 'MCEFilter_ParaCtx':'45', 'MCEFilter_SecPara':'46',
          'MCEFilter_SecParaCtx':'47', 'MCEFilter_Hybird':'48', 'MCEFilter_SecTitle':'49',
          #------------ Automatically Generated Cause-effect Filter models ------------------
          'SCEFilter_Para':'51', 'SCEFilter_TFIDF':'52', 'SCEFilter_SimGraph':'53',
          'SCEFilter_WordGraph':'54', 'SCEFilter_ParaCtx':'55', 'SCEFilter_SecPara':'56',
          'SCEFilter_SecParaCtx':'57', 'SCEFilter_Hybird':'58', 'SCEFilter_SecTitle':'59',
          #---------------- Manually Annotated Cause-effect combination with Bias ------------
          'MCEBias_Para':'61', 'MCEBias_TFIDF':'62', 'MCEBias_SimGraph':'63',
          'MCEBias_WordGraph':'64', 'MCEBias_ParaCtx':'65', 'MCEBias_SecPara':'66',
          'MCEBias_SecParaCtx':'67', 'MCEBias_Hybird':'68', 'MCEBias_SecTitle':'69',
          # ------------ Automatically Generated Cause-effect combination with Bias ------------
          'SCEBias_Para': '71', 'SCEBias_TFIDF': '72', 'SCEBias_SimGraph': '73',
          'SCEBias_WordGraph': '74', 'SCEBias_ParaCtx': '75', 'SCEBias_SecPara': '76',
          'SCEBias_SecParaCtx': '77', 'SCEBias_Hybird': '78', 'SCEBias_SecTitle': '79',
          #--------- Manually Annotated Cause-effect combination into weight iteration --------
          'MCEIter_Para':'81', 'MCEIter_ParaCtx':'85', 'MCEIter_SecPara':'86',
          'MCEIter_SecParaCtx':'87', 'MCEIter_Hybird':'88', 'MCEIter_SecTitle':'89',
          #--------- Automatically Generated Cause-effect combination into weight iteration --------
          'SCEIter_Para':'91', 'SCEIter_ParaCtx':'95', 'SCEIter_SecPara':'96',
          'SCEIter_SecParaCtx':'97', 'SCEIter_Hybird':'98', 'SCEIter_SecTitle':'99'
          }

# ----- The default model ID list to rank sentences and do ROUGE evaluation -------------
TempMidlst = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
# ----- The default maxwords and top_k_sentences  -----
default_maxw = 100
default_topk = 5
default_topkword = 100
# ---- default_strict_maxw is the default vaule for 'strictmax' --------------
default_strict_maxw = 1
# ---- default_remove_stopword is the default vaule for 'remove_stopwords' --------------
default_remove_stopword = 0
# ---- default_useabstr is the default vaule for 'useabstr' --------------
default_useabstr = 0


# ---------- The Score-Metrics-Matrix to draw excel files and txt files ------------------
ScrMtx_matrix = [['ROUGE-1','Average_P','Average_R','Average_F'],
                 ['ROUGE-2','Average_P','Average_R','Average_F'],
                 ['ROUGE-3','Average_P','Average_R','Average_F'],
                 ['ROUGE-4','Average_P','Average_R','Average_F'],
                 ['ROUGE-L','Average_P','Average_R','Average_F']]

# ---- Get the name_to_id dictionary ----
def GetNameIDDict():
    return NameID

# ---- Get the id_to_name dictionary ----
def GetIDNameDict():
    modelname={}
    for eachkey in NameID.keys():
        idstr = NameID[eachkey]
        modelname[idstr] = eachkey
    return modelname

IDName = GetIDNameDict()

# -------- Get the ranking model ID list for a name list -----------
# 1. The input is the list of sentence ranking model names.
# 2. The output is the list of sentence ranking model ID.
def GetSystemID(modelnamelst):
    modelIDlst =[]
    for modelname in modelnamelst:
        modelIDlst.append(NameID[modelname])
    modelIDlst.sort()
    return modelIDlst

# -------- Get the ranking model name list for a ID list -----------
# 1. The input is the list of sentence ranking model ID.
# 2. The output is the list of sentence ranking model names.
def GetModelNameLst(modelIDlst):
    modelnamelst =[]
    for modelid in modelIDlst:
        modelnamelst.append(IDName[modelid])
    return modelnamelst

#######################################################################################
# ----------------- Ranking & ROUGE Configs on Different Corpus  -------------------- #
#######################################################################################

# ---- Get the raw data root directory and ROUGE score file directory for the corpus --------
def GetDataRootDir(config_name):
    corpus_name = config_name.split('_')[0]
    dataroot = os.path.join(os.getcwd(), corpus_name)
    CheckMkDir(dataroot)
    # Check pyrouge result directory --------
    resultroot = os.path.join(dataroot, "PyrougeResults")
    CheckMkDir(resultroot)
    resultdir = os.path.join(resultroot, config_name)  # r'./PyrougeResults//'
    CheckMkDir(resultdir)
    return dataroot, resultdir

# ---- GetConfPathDic function will get config dictionary about directories ----
# 1. u'dataroot': raw data root directory of the corpus
# 2. u'pickle_path': the 'sxpText' objects (see sxpPackage.py) pickle files directory
# 3. u'celstpk_path': the 'CELink' objects (see cmyPackage.py) list for each paper.
# 4. u'model_html': The standard summarization directory
# 5. u'system_html': The automatically generated summarization directory, './system_html/-different-specific-config-/'
# 6. u'outdir': the directory of ROUGE score files directory, './PyrougeResults/-different-specific-config-/'
def GetConfDirDic(config_name):
    dataroot, resultdir = GetDataRootDir(config_name)
    config_path_dic = {
        u'dataroot': dataroot,
        u'pickle_path': os.path.join(dataroot, r'pickle'),
        u'celstpk_path': os.path.join(dataroot, r'CEPerDic'),
        u'model_path': os.path.join(dataroot, r'model_html'),
        u'system_path': os.path.join(dataroot, r'system_html', config_name),
        u'outdir': resultdir}
    return config_path_dic


# ===================================== For KG corpus ====================================

# ---------- Set file name pattern config dictionary for 'KG39papers' corpus ------------
# For 'pickle_file_pattern_id':
#   xxxx_1.pickle: the sxpText object whoes sentence_set excludes Abstract & Conclusiton sentences.
#   xxxx_2.pickle: the sxpText object whoes sentence_set includes Abstract & Conclusiton sentences.
def GetKGFileNamePatterns(pkopt='exc'):
    kg_fnpt_dict = {u'modelpattern': r'f#ID#.txt.[A-Z].html',
                    u'systempattern': r'^f(\d+).txt.html',
                    u'model_filenames_pattern_id': r'^f(\d+).txt.[A-Z].html',
                    u'system_filename_pattern_id': r'f#ID#.txt.html',
                    u'pickle_file_pattern_id': r'f#ID#.txt_1.pk'}
    if pkopt == 'inc':
        kg_fnpt_dict[u'pickle_file_pattern_id'] = r'f#ID#.txt_2.pk'
    return kg_fnpt_dict


# ---------- Get config dictionary for 'KG39papers' corpus according to conf_name ------------
# conf_name is separated by '_' and usually contains 4 parts, e.g. 'kg_exc_withstop_maxword'
# 1. The first part is the corpus name, such as 'kg', 'acl', 'duc', and 'single'.
# 2. The second part, is whether we include Abstract & Conclusion into ranking, 'inc' or 'exc'.
#    This part only exists for scientific corpus, such as 'kg' and 'acl'
# 3. The third is whether we remove stopwords from sentence texts, 'withstop' or 'withoutstop'.
# 4. The last is the length metric of automatically generated summarization, 'maxword' or 'topk'
# strictmax means whether we need the length of generaged summaries strictly obey to the maxwords
# useabstr means whether we use the length of Abstract as the maxword ----
# 1. useabstr = 0 do not use the length of Abstract as the maxword
# 2. useabstr = 1 uses the length of Abstract as the maxword
# 3. useabstr = 2 uses the length of Conclusion as the maxword
# 4. useabstr = 3 uses the average length of Abstract and Conclusion as the maxword
# 5. useabstr = 4 uses the average length of Abstract, Conclusion and Abstract+Conclusion as the maxword
def GetKGConfDict(conf_name, sys_mid_lst=TempMidlst, maxw=default_maxw, topk=default_topk, strictmax=default_strict_maxw, useabstr=default_useabstr):
    # Get config list from config name
    config_list = conf_name.split('_')
    if not config_list[0].startswith('kg'):
        print ("current config name %s does not fit its config dict building function!" % conf_name)
        return {}
    # Set basic config dict items
    conf_dict = {u'NameID': NameID,
                 u'config_name': conf_name,
                 u'plotwho': '_'.join(config_list[0:2]),
                 u'system_modelid_list': sys_mid_lst,
                 u'maxword': maxw,
                 u'topksent': topk,
                 u'strictmax': strictmax,
                 u'useabstr': useabstr,
                 u'remove_stopwords': 0   # set default remove_stopwords = 0
                 }
    # ---- Get config dict about directories ----
    conf_dict.update(GetConfDirDic(conf_name))
    # ---- Get config dict about file name patterns -----
    pkopt = config_list[1]
    conf_dict.update(GetKGFileNamePatterns(pkopt=pkopt))
    # if we use topk as metric type of summaries's length, set u'maxword' = -1
    if config_list[-1] == 'topk':
        conf_dict[u'maxword'] = -1
    # if we require remove stopwords, then remove_stopwords = 1.
    if config_list[-2] == 'withoutstop':
        conf_dict[u'remove_stopwords'] = 1
    return conf_dict


# ===================================== For ACL corpus ====================================

# ---------- Set file name pattern config dictionary for 'KG39papers' corpus ------------
# For 'pickle_file_pattern_id':
#   xxxx_1.pickle: the sxpText object whoes sentence_set excludes Abstract & Conclusiton sentences.
#   xxxx_2.pickle: the sxpText object whoes sentence_set includes Abstract & Conclusiton sentences.
def GetACLFileNamePatterns(pkopt='exc'):
    acl_fnpt_dict = {u'modelpattern':  r'P14-#ID#.xhtml.[A-Z].html',
                     u"systempattern": r'^P14-(\d+).xhtml.html',  # Note that in real dir, model_id need to be appended to the systempattern
                     u'model_filenames_pattern_id': r'P14-(\d+).xhtml.[A-Z].html',
                     u'system_filename_pattern_id': r'P14-#ID#.xhtml.html',
                     u'pickle_file_pattern_id': r'P14-#ID#.xhtml_1.pickle'}
    if pkopt == 'inc':
        acl_fnpt_dict[u'pickle_file_pattern_id'] = r'P14-#ID#.xhtml_2.pickle'
    return acl_fnpt_dict


# ---------- Get config dictionary for 'ACL2014' corpus according to conf_name ------------
# conf_name is separated by '_' and usually contains 4 parts, e.g. 'acl_exc_withstop_maxword'
# 1. The first part is the corpus name, such as 'kg', 'acl', 'duc', and 'single'.
# 2. The second part, is whether we include Abstract & Conclusion into ranking, 'inc' or 'exc'.
#    This part only exists for scientific corpus, such as 'kg' and 'acl'
# 3. The third is whether we remove stopwords from sentence texts, 'withstop' or 'withoutstop'.
# 4. The last is the length metric of automatically generated summarization, 'maxword' or 'topk'
def GetACLConfDict(conf_name, sys_mid_lst=TempMidlst, maxw=default_maxw, topk=default_topk, strictmax=default_strict_maxw, useabstr=default_useabstr):
    # Get config list from config name
    config_list = conf_name.split('_')
    if not config_list[0].startswith('acl'):
        print ("current config name %s does not fit its config dict building function!" % conf_name)
        return {}
    # Set basic config dict items
    conf_dict = {u'NameID': NameID,
                 u'config_name': conf_name,
                 u'plotwho': '_'.join(config_list[0:2]),
                 u'system_modelid_list': sys_mid_lst,
                 u'maxword': maxw,
                 u'topksent': topk,
                 u'strictmax': strictmax,
                 u'useabstr': useabstr,
                 u'remove_stopwords': 0   # set default remove_stopwords = 0
                 }
    # ---- Get config dict about directories ----
    conf_dict.update(GetConfDirDic(conf_name))
    # ---- Get config dict about file name patterns -----
    conf_dict.update(GetACLFileNamePatterns(pkopt=config_list[1]))
    # if we use topk as metric type of summaries's length, set u'maxword' = -1
    if config_list[-1] == 'topk':
        conf_dict[u'maxword'] = -1
    # if we require remove stopwords, then remove_stopwords = 1.
    if config_list[-2] == 'withoutstop':
        conf_dict[u'remove_stopwords'] = 1
    return conf_dict


# ===================================== For DUC corpus ====================================

# ---------- Set file name pattern config dictionary for 'DUC' corpus ------------
# For 'pickle_file_pattern_id':
#   xxxx_1.pickle: the sxpText object whoes sentence_set excludes Abstract & Conclusiton sentences.
#   xxxx_2.pickle: the sxpText object whoes sentence_set includes Abstract & Conclusiton sentences.
def GetDUCFileNamePatterns(useabstr=default_useabstr):
    duc_fnpt_dict = {u'useabstr': useabstr,
                     u'modelpattern': r'D\d\d\d.P.100.[A-Z].[A-Z].#ID#.html',
                     u'systempattern': r'^(\w+-\w+).html',
                     u'model_filenames_pattern_id': r'D\d\d\d.P.100.[A-Z].[A-Z].(\w+-\w+).html',
                     u'system_filename_pattern_id': r'#ID#.html',
                     u'pickle_file_pattern_id': r'#ID#'}
    return duc_fnpt_dict


# ---------- Get config dictionary for 'DUC' corpus according to conf_name ------------
# conf_name is separated by '_' and usually contains 4 parts, e.g. 'duc_exc_withstop_maxword'
# 1. The first part is the corpus name, such as 'kg', 'acl', 'duc', and 'single'.
# 2. The second part, is whether we include Abstract & Conclusion into ranking, 'inc' or 'exc'.
#    This part only exists for scientific corpus, such as 'kg' and 'acl'
# 3. The third is whether we remove stopwords from sentence texts, 'withstop' or 'withoutstop'.
# 4. The last is the length metric of automatically generated summarization, 'maxword' or 'topk'
def GetDUCConfDict(conf_name, sys_mid_lst=TempMidlst, maxw=default_maxw, topk=default_topk, strictmax=default_strict_maxw, useabstr=default_useabstr):
    # Get config list from config name
    config_list = conf_name.split('_')
    if not config_list[0].startswith('duc'):
        print ("current config name %s does not fit its config dict building function!" % conf_name)
        return {}
    # Set basic config dict items
    conf_dict = {u'NameID': NameID,
                 u'config_name': conf_name,
                 u'plotwho': 'duc',
                 u'system_modelid_list': sys_mid_lst,
                 u'maxword': maxw,
                 u'topksent': topk,
                 u'strictmax': strictmax,
                 u'remove_stopwords': 0   # set default remove_stopwords = 0
                 }
    # ---- Get config dict about directories ----
    conf_dict.update(GetConfDirDic(conf_name))
    # ---- Get config dict about file name patterns -----
    conf_dict.update(GetDUCFileNamePatterns(useabstr=useabstr))
    # if we use topk as metric type of summaries's length, set u'maxword' = -1
    if config_list[-1] == 'topk':
        conf_dict[u'maxword'] = -1
    # if we require remove stopwords, then remove_stopwords = 1.
    if config_list[-2] == 'withoutstop':
        conf_dict[u'remove_stopwords'] = 1
    return conf_dict


# ===================================== For Single file ====================================

# ---------- Set file name pattern config dictionary for 'single' file ------------
# For 'pickle_file_pattern_id':
#   xxxx_1.pickle: the sxpText object whoes sentence_set excludes Abstract & Conclusiton sentences.
#   xxxx_2.pickle: the sxpText object whoes sentence_set includes Abstract & Conclusiton sentences.
def GetSingleFileNamePatterns(useabstr=default_useabstr):
    single_fnpt_dict = {u'useabstr': useabstr,
                        u'modelpattern':  r'testdimension_#ID#.txt.pk.[A-Z].html',
                        u"systempattern" : r'testdimension_(\d+).txt',
                        # Note that in real dir, model_id need to be appended to the systempattern
                        u'model_filenames_pattern_id' : r'testdimension_(\d+).txt.pk.[A-Z].html',
                        u'system_filename_pattern_id' : r'testdimension_#ID#.txt',
                        u'pickle_file_pattern_id': r'testdimension_#ID#.txt.pk'}
    return single_fnpt_dict


# ---------- Get config dictionary for 'single' file according to conf_name ------------
# conf_name is separated by '_' and usually contains 4 parts, e.g. 'single_withstop_maxword'
# 1. The first part is the corpus name, such as 'kg', 'acl', 'duc', and 'single'.
# 2. The second part, is whether we include Abstract & Conclusion into ranking, 'inc' or 'exc'.
#    This part only exists for scientific corpus, such as 'kg' and 'acl'
# 3. The third is whether we remove stopwords from sentence texts, 'withstop' or 'withoutstop'.
# 4. The last is the length metric of automatically generated summarization, 'maxword' or 'topk'
def GetSingleConfDict(conf_name, sys_mid_lst=TempMidlst, maxw=default_maxw, topk=default_topk, strictmax=default_strict_maxw, useabstr=default_useabstr):
    # Get config list from config name
    config_list = conf_name.split('_')
    if not config_list[0].startswith('single'):
        print ("current config name %s does not fit its config dict building function!" % conf_name)
        return {}
    # Set basic config dict items
    conf_dict = {u'NameID': NameID,
                 u'config_name': conf_name,
                 u'plotwho': 'single',
                 u'system_modelid_list': sys_mid_lst,
                 u'maxword': maxw,
                 u'topksent': topk,
                 u'strictmax': strictmax,
                 u'remove_stopwords': 0   # set default remove_stopwords = 0
                 # ----- Keyword bench path is the file paths to store the built keywords_mind_maps -----
                 # u'keyword_bench_path':os.path.join(conf_dict[u'dataroot'],  r'keyword'),
                 # u'keyword_path':os.path.join(conf_dict[u'resultdir'], r'keyword')
                 }
    # ---- Get config dict about directories ----
    conf_dict.update(GetConfDirDic(conf_name))
    # ---- Get config dict about file name patterns -----
    conf_dict.update(GetDUCFileNamePatterns(useabstr=useabstr))
    # if we use topk as metric type of summaries's length, set u'maxword' = -1
    if config_list[-1] == 'topk':
        conf_dict[u'maxword'] = -1
    # if we require remove stopwords, then remove_stopwords = 1.
    if config_list[-2] == 'withoutstop':
        conf_dict[u'remove_stopwords'] = 1
    return conf_dict

# allconf_name_dict is the dict maps conf_name to their conf_dict building function
allconf_name_dict = {
    # ---- config-dict building function for kg corpus ----
    u'kg_exc_withstop_maxword': GetKGConfDict,
    u'kg_exc_withoutstop_maxword': GetKGConfDict,
    u'kg_exc_withstop_topk': GetKGConfDict,
    u'kg_exc_withoutstop_topk': GetKGConfDict,
    u'kg_inc_withstop_maxword': GetKGConfDict,
    u'kg_inc_withoutstop_maxword': GetKGConfDict,
    u'kg_inc_withstop_topk': GetKGConfDict,
    u'kg_inc_withoutstop_topk': GetKGConfDict,
    # ---- config-dict building function for kgmance corpus ----
    u'kgmance_exc_withstop_maxword': GetKGConfDict,
    u'kgmance_exc_withoutstop_maxword': GetKGConfDict,
    u'kgmance_exc_withstop_topk': GetKGConfDict,
    u'kgmance_exc_withoutstop_topk': GetKGConfDict,
    u'kgmance_inc_withstop_maxword': GetKGConfDict,
    u'kgmance_inc_withoutstop_maxword': GetKGConfDict,
    u'kgmance_inc_withstop_topk': GetKGConfDict,
    u'kgmance_inc_withoutstop_topk': GetKGConfDict,
    # ---- config-dict building function for single paper in kg corpus ----
    u'kgsingle_inc_withoutstop_maxword': GetKGConfDict,
    # ---- config-dict building function for acl corpus ----
    u'acl_exc_withstop_maxword': GetACLConfDict,
    u'acl_exc_withoutstop_maxword': GetACLConfDict,
    u'acl_exc_withstop_topk': GetACLConfDict,
    u'acl_exc_withoutstop_topk': GetACLConfDict,
    u'acl_inc_withstop_maxword': GetACLConfDict,
    u'acl_inc_withoutstop_maxword': GetACLConfDict,
    u'acl_inc_withstop_topk': GetACLConfDict,
    u'acl_inc_withoutstop_topk': GetACLConfDict,
    # ---- config-dict building function for duc corpus ----
    u'duc_withstop_maxword': GetDUCConfDict,
    u'duc_withoutstop_maxword': GetDUCConfDict,
    u'duc_withoutstop_topk': GetDUCConfDict,
    u'duc_withstop_topk': GetDUCConfDict,
    # ---- config-dict building function for single file ----
    u'single_inc_withstop': GetSingleConfDict,
    u'single_inc_withoutstop': GetSingleConfDict
}

#######################################################################################
# ----------------- Building and Getting Rouge Result file paths -------------------- #
#######################################################################################
# -------- Get the config dictionary for a specific config name----------
# 1. Check whether the specific config name 'conf_name' have been defined.
# 2. Check the config of summarization length, conf_of_sumlen
#   (1) if conf_of_sumlen is 'maxword', pass maxw to the config dictionary building function.
#   (2) else if conf_of_sumlen is 'topk', pass topk to the config dictionary building function.
#   (3) else, use the default config in dictionary building function.
def GetRougeConfDict(conf_name, sys_mid_lst=TempMidlst, maxw=default_maxw, topk=default_topk, strictmax=default_strict_maxw, useabstr=default_useabstr):
    # ---- check config name ----
    if conf_name not in allconf_name_dict.keys():
        print 'no such name'
        return
    # ---- Get dataroot, resultdir according to conf_name ----
    conf_dict_pk_fp = GetResultFilePath(conf_name, sys_mid_lst, '.conf_dict.pk')
    # ---- If the config dict has already stored, reload it ----
    if os.path.exists(conf_dict_pk_fp):
        conf_dict = LoadSxptext(conf_dict_pk_fp)
    # ---- If the config dict has not be created, create it ----
    else:
        conf_dict = allconf_name_dict[conf_name](conf_name, sys_mid_lst=sys_mid_lst, maxw=maxw, topk=topk, strictmax=strictmax, useabstr=useabstr)
        StoreSxptext(conf_dict, conf_dict_pk_fp)  # store the config dictionary
    return conf_dict

# -------- Get the path of ROUGE evaluation files for a specific config -----------
# ftype is the type of the result file you want to store.
def GetResultFilePath(conf_name, sys_mid_lst=TempMidlst, ftype='.txt'):
    fhead = conf_name + '_' + '_'.join(sys_mid_lst)
    dataroot, resultdir = GetDataRootDir(conf_name)
    rougefpath = os.path.join(resultdir, fhead + ftype)
    return rougefpath

# -------- Get config dict, and .txt, .pk and .xls file paths for ROUGE scores -----------
# Inputs: conf_dict: the dictionary object stores the config information.
# Outputs:
# 1. result_txt_fp: the .txt file path of ROUGE score.
# 2. result_pk_fp: the .pk file path for ROUGE score dict.
# 3. result_xls_fp: the .xls file path to draw ROUGE score as a excel file.
def GetROUGEFilePaths(conf_dict):
    if not conf_dict.has_key(u'config_name'):
        print ("Error! The config dict parameter doesn't contain config_name!")
        return
    conf_name = conf_dict[u'config_name']
    sys_mid_lst = []
    if conf_dict.has_key(u'system_modelid_list'):
        sys_mid_lst = conf_dict[u'system_modelid_list']
    print '-------------', conf_name, '-----------'
    result_xls_fp = GetResultFilePath(conf_name, sys_mid_lst, '.rouge_score.xls')
    result_txt_fp = GetResultFilePath(conf_name, sys_mid_lst, '.txt')
    result_pk_fp = result_txt_fp + '.pk'
    print result_txt_fp
    print result_pk_fp
    print result_xls_fp
    return result_txt_fp, result_pk_fp, result_xls_fp

#######################################################################################
# ------------ Get and Check Configs from config dict for specific usage ------------ #
#######################################################################################
# ------ CheckConfDict: check the file paths in config dictionary for Sentence Ranking -------
def CheckConfDict(conf_dict):
    if not conf_dict.has_key(u'config_name'):
        print ("Error! The config dict parameter doesn't contain config_name!")
        return False

    if not conf_dict.has_key(u'dataroot'):
        corpus_name = conf_dict[u'config_name'].split('_')[0]
        conf_dict[u'dataroot'] = os.path.join(os.getcwd(), corpus_name)

    if not conf_dict.has_key(u'outdir'):
        conf_dict[u'outdir'] = os.path.join(conf_dict[u'dataroot'], "PyrougeResults", conf_dict[u'config_name'])

    if not conf_dict.has_key(u'pickle_path'):
        conf_dict[u'pickle_path'] = os.path.join(conf_dict[u'dataroot'], "pickle")

    if not conf_dict.has_key(u'celstpk_path'):
        conf_dict[u'celstpk_path'] = os.path.join(conf_dict[u'dataroot'], "CEPerDic")

    if not conf_dict.has_key(u'model_path'):
        conf_dict[u'model_path'] = os.path.join(conf_dict[u'dataroot'], "model_html")

    if not conf_dict.has_key(u'system_path'):
        conf_dict[u'system_path'] = os.path.join(conf_dict[u'dataroot'], "system_html", conf_dict[u'config_name'])

    if not conf_dict.has_key(u'system_modelid_list') or conf_dict[u'system_modelid_list'] == []:
        conf_dict[u'system_modelid_list'] = TempMidlst

    if not conf_dict.has_key(u'systempattern'):
        conf_dict[u'systempattern'] = r".+"

    if not conf_dict.has_key(u'modelpattern'):
        conf_dict[u'modelpattern'] = r".+"

    if not conf_dict.has_key(u'model_filenames_pattern_id'):
        conf_dict[u'model_filenames_pattern_id'] = r".+"

    if not conf_dict.has_key(u'system_filename_pattern_id'):
        conf_dict[u'system_filename_pattern_id'] = r".+"

    if not conf_dict.has_key(u'pickle_file_pattern_id'):
        conf_dict[u'pickle_file_pattern_id'] = r".+"

    if not conf_dict.has_key(u'maxword'):
        conf_dict[u'maxword'] = default_maxw

    if not conf_dict.has_key(u'topksent'):
        conf_dict[u'topksent'] = default_topk

    if not conf_dict.has_key(u'strictmax'):
        conf_dict[u'strictmax'] = default_strict_maxw

    if not conf_dict.has_key(u'remove_stopwords'):
        conf_dict[u'remove_stopwords'] = default_remove_stopword

    CheckMkDir(conf_dict[u'dataroot'])
    CheckMkDir(conf_dict[u'outdir'])
    CheckMkDir(conf_dict[u'pickle_path'])
    CheckMkDir(conf_dict[u'model_path'])
    CheckMkDir(os.path.dirname(conf_dict[u'system_path']))
    CheckMkDir(conf_dict[u'system_path'])
    return True


# --------- Get config name from a config dict ----------
def GetConfName(conf_dict):
    if not conf_dict.has_key(u'config_name'):
        print ("Error! The config dict parameter doesn't contain config_name!")
        return ""
    else:
        return conf_dict[u'config_name']

# --------- Get config of summarization model IDs from a config dict -------
def GetConfSysMidLst(conf_dict):
    if not conf_dict.has_key(u'system_modelid_list') or conf_dict[u'system_modelid_list'] == []:
        conf_dict[u'system_modelid_list'] = TempMidlst
    return conf_dict[u'system_modelid_list']

# --------- Get configs about file paths from a config dict ------
def GetConfAboutFileDirs(conf_dict):
    if not conf_dict.has_key(u'system_path'):
        conf_dict[u'system_path'] = os.path.join(conf_dict[u'dataroot'], "system_html", conf_dict[u'config_name'])
    if not conf_dict.has_key(u'model_path'):
        conf_dict[u'model_path'] = os.path.join(conf_dict[u'dataroot'], "model_html")
    if not conf_dict.has_key(u'outdir'):
        conf_dict[u'outdir'] = os.path.join(conf_dict[u'dataroot'], "PyrougeResults", conf_dict[u'config_name'])
    system_path = conf_dict[u'system_path']
    model_path = conf_dict[u'model_path']
    output_path = conf_dict[u'outdir']
    return system_path, model_path, output_path

def GetConfAboutPickleFiles(conf_dict):
    if not conf_dict.has_key(u'pickle_path'):
        conf_dict[u'pickle_path'] = os.path.join(conf_dict[u'dataroot'], "pickle")
    if not conf_dict.has_key(u'celstpk_path'):
        conf_dict[u'celstpk_path'] = os.path.join(conf_dict[u'dataroot'], "CEPerDic")
    if not conf_dict.has_key(u'pickle_file_pattern_id'):
        conf_dict[u'pickle_file_pattern_id'] = r".+"
    pickle_path = conf_dict[u'pickle_path']
    celstpk_path = conf_dict[u'celstpk_path']
    pk_fnamept_id = conf_dict[u'pickle_file_pattern_id']
    return pickle_path, celstpk_path, pk_fnamept_id

# --------- Get configs about file name patterns from a config dict ------
def GetConfAboutSumFnamePt(conf_dict):
    if not conf_dict.has_key(u'systempattern'):
        conf_dict[u'systempattern'] = r".+"
    if not conf_dict.has_key(u'modelpattern'):
        conf_dict[u'modelpattern'] = r".+"
    system_pattern = conf_dict[u'systempattern']
    model_pattern = conf_dict[u'modelpattern']
    return system_pattern, model_pattern

# --------- Get configs about additional file name patterns from a config dict ------
def GetConfAboutAuxSumFnamePt(conf_dict):
    if not conf_dict.has_key(u'system_filename_pattern_id'):
        conf_dict[u'system_filename_pattern_id'] = r".+"
    if not conf_dict.has_key(u'model_filenames_pattern_id'):
        conf_dict[u'model_filenames_pattern_id'] = r".+"
    mod_fnamept_id = conf_dict[u'model_filenames_pattern_id']
    sys_fnamept_id = conf_dict[u'system_filename_pattern_id']
    return sys_fnamept_id, mod_fnamept_id

# --------- Get configs about additional file name patterns from a config dict ------
def GetConfAboutSumLength(conf_dict):
    if not conf_dict.has_key(u'useabstr'):
        conf_dict[u'useabstr'] = default_useabstr
    if not conf_dict.has_key(u'maxword'):
        conf_dict[u'maxword'] = default_maxw
    if not conf_dict.has_key(u'topksent'):
        conf_dict[u'topksent'] = default_topk
    if not conf_dict.has_key(u'strictmax'):
        conf_dict[u'strictmax'] = default_strict_maxw
    if not conf_dict.has_key(u'remove_stopwords'):
        conf_dict[u'remove_stopwords'] = default_remove_stopword
    useabstr = conf_dict[u'useabstr']
    maxword = conf_dict[u'maxword']
    topksent = conf_dict[u'topksent']
    strictmax = conf_dict[u'strictmax']
    remove_stopword = conf_dict[u'remove_stopwords']
    return useabstr, maxword, topksent, strictmax, remove_stopword

#######################################################################################
# ------------------------------ Test Functions ------------------------------------- #
#######################################################################################
def ShowConfDict(conf_dict):
    print "---------------" + conf_dict[u'config_name'] + "-----------------"
    print 'plotwho:', conf_dict[u'plotwho']
    print 'system_modelid_list:', conf_dict[u'system_modelid_list']
    print 'maxword = %d, topk = %d, strictmax = %d, remove_stopwords = %d' % (
    conf_dict[u'maxword'], conf_dict[u'topksent'], conf_dict[u'strictmax'], conf_dict[u'remove_stopwords'])
    print 'dataroot:', conf_dict[u'dataroot']
    print 'pickle_path:', conf_dict[u'pickle_path']
    print 'celstpk_path:', conf_dict[u'celstpk_path']
    print 'model_path:', conf_dict[u'model_path']
    print 'system_path:', conf_dict[u'system_path']
    print 'outdir:', conf_dict[u'outdir']
    print 'modelpattern:', conf_dict[u'modelpattern']
    print 'systempattern:', conf_dict[u'systempattern']
    print 'model_filenames_pattern_id:', conf_dict[u'model_filenames_pattern_id']
    print 'system_filename_pattern_id:', conf_dict[u'system_filename_pattern_id']
    print 'pickle_file_pattern_id:', conf_dict[u'pickle_file_pattern_id']


def TestRougeFilePaths(confnamelst=[], sys_mid_lst=[]):
    for cn in confnamelst:
        conf_dict = GetRougeConfDict(cn, sys_mid_lst)
        GetROUGEFilePaths(conf_dict)


def TestRougeConfDict(confnamelst=[], sys_mid_lst=[]):
    for cn in confnamelst:
        conf_dict = GetRougeConfDict(cn, sys_mid_lst)
        ShowConfDict(conf_dict)

#######################################################################################
# ------------------------------ Main Functions ------------------------------------- #
#######################################################################################
def main():
    kg_confname_lst = ['kg_exc_withstop_maxword']
    model_idlst = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    TestRougeFilePaths(kg_confname_lst, model_idlst)
    # TestRougeConfDict(kg_confname_lst, model_idlst)

if __name__ == '__main__':
    main()
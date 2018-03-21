# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------------------
# Name:        cmyDoPyrougeScoreTest (rewrite from sxpDoPyrougeScoreTest.py)
# Purpose:
# 1. DoRougeEvaluateByConfDict: Do ROUGE evaluate according to the config dictionary
# 2. MakeAllFileCSV: create a csv file which stores the file name and file paths for important files
# 3. GetFileNames: get file paths according to cmd, and cmd serves as key to get file paths
# -------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import pandas as pd
import cmyDoRankSent
from sxpPackage import *
import cmyPyrougeEvaluate
import cmyParseRougeScore
from cmyRougeConfig import *


#######################################################################################
# -------------- Do ROUGE evaluate according to the config dictionary --------------- #
#######################################################################################
# ------- DoRougeEvaluateByConfDict: Do ROUGE evaluate according to the config dictionary -------
# Inputs:
# 1. conf_dict: the config dictionary object which we want to evaluate the ROUGE score
# 2. writexls: writexls = 1 means we want to draw excel file of ROUGE score
# 3. drawfig: drawfig = 1 means we want to draw figures for each ROUGE score type.
#             Note that the parameter drawfig is only useful when writexls = 1.
def DoRougeEvaluateByConfDict(conf_dict, writexls=1, drawfig=1):
    result_txt_fp, result_pk_fp, result_xls_fp = GetROUGEFilePaths(conf_dict)
    cmyPyrougeEvaluate.CallMyPyrouge(conf_dict, result_txt_fp)
    cmyParseRougeScore.ParseScoreTxt2ScoreDic(result_txt_fp, result_pk_fp)
    if writexls == 1:
        print 'Drawing ROUGE score dict into excel file and plotting scores by figures'
        cmyParseRougeScore.ProcessRougeScoreDic2Excel(result_pk_fp, result_xls_fp, drawfig=drawfig)


#######################################################################################
# ----------------------- Functions to get file names and paths --------------------- #
#######################################################################################

# ---------- MakeAllFileCSV: create a csv file which stores the file name and file paths for important files --------
def MakeAllFileCSV(conf_dict):
    mod_sys = cmyPyrougeEvaluate.MyProduceSysModPair(conf_dict)
    print len(mod_sys)

    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    pickle_path, celstpk_path, pk_fnamept_id = GetConfAboutPickleFiles(conf_dict)

    allmodel_file_list = []

    for eachone in mod_sys:
        print "--"
        print eachone
        sys_file_model_list = eachone[0]
        print sys_file_model_list
        model_file_list = eachone[1]
        print model_file_list
        model_filename_list =[]
        for eachmodel in model_file_list:
            modelf = os.path.join(model_path, eachmodel)
            model_filename_list.append(modelf)
        for each_model in sys_file_model_list:
            print each_model
            fid = each_model[0]
            model_id = each_model[1]
            sys_file = each_model[2]
            file_dict = {}
            file_dict['fid'] = fid
            file_dict['model_id'] = str(model_id)
            file_dict['model_name'] = IDName[model_id]
            file_dict['sysfname'] = system_path + '\\' + sys_file
            pkfname = pk_fnamept_id.replace('#ID#', fid)
            file_dict['pkfname'] = os.path.join(pickle_path, pkfname)
            file_dict['allsent'] = file_dict['sysfname'] + 'allsent.pk'
            file_dict['topsentpk'] = file_dict['sysfname'] + 'topsent.pk'
            file_dict['modelfiles'] = model_filename_list
            file_dict['keywordfile'] = os.path.join(conf_dict['keyword_path'], pkfname +'key.pk')
            allmodel_file_list.append(file_dict)
    for each in allmodel_file_list:
        print each
    df = pd.DataFrame(allmodel_file_list)
    print df.head()
    print df['modelfiles'][0]
    allfilename = os.path.join(output_path, 'allfilelist.csv')
    df.to_csv(allfilename)

# ---------- GetFileNames: get file paths according to cmd, and cmd serves as key to get file paths --------
# Input:
# 1. conf_dict: configure dictionary
# 2. cmd: the key to fetch file paths from csv file
def GetFileNames(conf_dict, cmd="pkfilename"):
    system_id_list = GetConfSysMidLst(conf_dict)
    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    allfilename = os.path.join(output_path, 'allfilelist.csv')

    df = pd.read_csv(allfilename)
    if cmd == 'pkfilename':
        return df['pkfname'].unique()
    if cmd == 'keyfilename':
        return df['keywordfile'].unique()
    if cmd == 'sysfname':
        return df['sysfname']
    if cmd == 'topkfname':
        return df['topsentpk']
    if cmd == 'modeltopk':
        print df['model_id']
        model_sys_dict = {}
        print system_id_list
        for eachtest in system_id_list:
            model_sys = df[df['model_id'] == int(NameID[eachtest])]
            model_sys_dict[NameID[eachtest]] = model_sys  # model_sys['topsentpk']
            print model_sys['topsentpk'].size
        return model_sys_dict


#######################################################################################
# ------ Functions to evaluate topk sentences according to keyword-mind-tree  ------- #
#######################################################################################

# ---------- GetTopkScoreByKeyword: get topk sentences score according to the keywords-mind-tree --------
def GetTopkScoreByKeyword(keywordfilepk, topkfilepk):
    return 0

# ---------- CompareTopkWithKeyword: generates and stores the files information into dicts --------
def CompareTopkWithKeyword(conf_dict):
    conf_name = GetConfName(conf_dict)
    system_path, model_path, out_dir = GetConfAboutFileDirs(conf_dict)
    model_sys_file_dict = GetFileNames(conf_dict, 'modeltopk')
    model_score = []
    for eachmodel, sysfile_df in model_sys_file_dict.items():
        for row_index, row in sysfile_df.iterrows():
             print row
             keywordfilepk = row['keywordfile']
             topkfilepk = row['topsentpk']
             score = GetTopkScoreByKeyword(keywordfilepk, topkfilepk)
             model_score_dict ={}
             model_score_dict['model_id'] = eachmodel
             model_score_dict['score'] = score
             model_score_dict['pkfilename'] = row['pkfname']
             model_score_dict['topsentpk'] = row['topsentpk']
             model_score.append(model_score_dict)
    df = pd.DataFrame(model_score)
    fname = os.path.join(out_dir, conf_name + '.keyscore.csv')
    df.to_csv(fname)


#######################################################################################
# - Functions to control whether ranking sentences or ROUGE evaluate summarizations - #
#######################################################################################
# ------ DoRank: rank sentences in files according to the config dict -------
def DoRank(conf_dict):
    if CheckConfDict(conf_dict):
        cmyDoRankSent.RankSentForSysSum(conf_dict)
    else:
        print "Configs are not correct!! Please check config again!!!"

# ------ RunConfig: generate config dict and ranking sentences or ROUGE evaluate summarizations  -------
def RunConfig(conf_name, sys_mid_lst=TempMidlst, rankthem=0, rougethem=0, maxw=default_maxw, topk=default_topk,
              strictmax=default_strict_maxw, useabstr=default_useabstr, writexls=1, drawfig=1):
    conf_dict = GetRougeConfDict(conf_name, sys_mid_lst, maxw, topk, strictmax, useabstr)
    if rankthem == 1:
        DoRank(conf_dict)
    if rougethem == 1:
        DoRougeEvaluateByConfDict(conf_dict, writexls, drawfig)

#######################################################################################
# ------------------------------ Test Functions ------------------------------------- #
#######################################################################################
def TestOnKGCorpus():
    # conf_name = ['kgmance_inc_withstop_maxword',
    #              'kgmance_inc_withoutstop_maxword',
    #              'kgmance_exc_withstop_maxword',
    #              'kgmance_exc_withoutstop_maxword']
    # sys_mid_lst = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '12', '14', '16', '18', '20']
    # sys_mid_lst = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
    # sys_mid_lst = ['41', '42', '43', '44', '45', '46', '47', '48', '49', '51', '52', '53', '54', '55', '56', '57', '58', '59']
    # sys_mid_lst = ['10', '12', '14', '16', '18', '20']
    # sys_mid_lst = ['11', '13', '15', '17', '19', '21']
    # sys_mid_lst = ['10','11']
    # sys_mid_lst = ['12','13','14','15','16','17','18','19']
    # sys_mid_lst = ['20','21']
    conf_name = ['kgsingle_inc_withoutstop_maxword']
    sys_mid_lst = ['02']
    rankthem = 1
    rougethem = 0
    maxw = 250
    topk = 10
    strictmax = 1
    writexls = 1
    drawfig = 1
    useabstr = 4
    for cfname in conf_name:
         RunConfig(cfname, sys_mid_lst, rankthem, rougethem, maxw, topk, strictmax, useabstr, writexls, drawfig)

def TestOnACLCorpus():
    # conf_name = [u'acl_exc_withstop_maxword',
    #              u'acl_exc_withoutstop_maxword',
    #              u'acl_inc_withstop_maxword',
    #              u'acl_inc_withoutstop_maxword']
    sys_mid_totallst = [['01', '02', '03', '04', '05', '06', '07', '08', '09'],
                        ['11'],
                        ['51', '52', '53', '54', '55', '56', '57', '58', '59'],
                        ['71', '72', '73', '74', '75', '76', '77', '78', '79'],
                        ['91', '95', '96', '97', '98', '99']]
    # sys_mid_lst = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    # sys_mid_lst = ['11']
    # sys_mid_lst = ['51', '52', '53', '54', '55', '56', '57', '58', '59']
    # sys_mid_lst = ['71', '72', '73', '74', '75', '76', '77', '78', '79']
    # sys_mid_lst = ['91', '95', '96', '97', '98', '99']
    cfname = u'acl_exc_withoutstop_maxword'
    rankthem = 1
    rougethem = 0
    maxw = 250
    topk = 10
    strictmax = 1
    writexls = 1
    drawfig = 1
    useabstr = 4
    # for cfname in conf_name:
    for sys_mid_lst in sys_mid_totallst:
         RunConfig(cfname, sys_mid_lst, rankthem, rougethem, maxw, topk, strictmax, useabstr, writexls, drawfig)

def TestMakeAllFileCSV():
    conf_name = 'kg_exc_withstop_maxword'
    MakeAllFileCSV(conf_name)


def TestCompareTopkWithKeyword():
    conf_name = 'kg_exc_withstop_maxword'
    CompareTopkWithKeyword(conf_name)

#######################################################################################
# ------------------------------ Main Functions ------------------------------------- #
#######################################################################################
def main():
    opt = "acl"
    if opt == "kg":
        TestOnKGCorpus()
    elif opt == "acl":
        TestOnACLCorpus()


if __name__ == '__main__':
    main()
    # TestMakeAllFileCSV()
    # TestCompareTopkWithKeyword()
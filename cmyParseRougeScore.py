# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------------------
# Name:        cmyParseRougeScore  (rewrite from sxpParseRougeScore.py)
# Purpose:
# 1. ProcessRougeScoreDic2Excel: write the ROUGE scores into a excel
# 2. ParseScoreTxt2ScoreDic: creates ROUGE score dict, stores in pickle file,
#                            and draws score dict as excel file
# 3. ParseMultiSysOutput: parse the ROUGE score from text into ROUGE score dict
# -------------------------------------------------------------------------------


#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import re
import codecs
import xlrd
import xlsxwriter
import numpy as np
import cmyPlotBar
from cmyToolkit import *
from cmyRougeConfig import *

#######################################################################################
# ------------------------ Functions for Operating Model IDs ------------------------ #
#######################################################################################
# -------- Get summarization model IDs by analyzing the file name ---------
def GetMidsFileName(fname):
    patstr = "(\d\d)"
    pt = re.compile(patstr)
    model_idset = pt.findall(fname)
    return model_idset

# -------- Get summarization model IDs from ROUGE score dictionary object ---------
def GetMidsScrDic(rouge_score_dict):
    modelids = rouge_score_dict.keys()
    modelids.sort()
    return modelids

#######################################################################################
# ------------------------ Functions to Process ROUGE Scores ------------------------ #
#######################################################################################
# -------- ProcessRougeScoreDic2Excel write the ROUGE scores into a excel -------------
# Inputs:
# 1. result_pk_fp: the pickle file path where stores the ROUGE score dictionary object
# 2. result_xls_fp: the excel file path to draw the ROUGE scores for observation
# 3. ROUGEScrMtx: The output layout of the excel. But we require tables are split by
#              Score-type, i.e ROUGE-1, ROUGE-2, ROUGE-3, ROUGE-4, ROUGE-L.
# Output:
# score_name_table_dict: (we dump it as pickle file)
#       The ROUGE score value tables organized by score types.
#       Each key is a score type both contained in ROUGEScrMtx and in the ROUGE score dict at result_pk_fp
#       Each item's value is a list, which contains two parts:
#       1. The first is the header of the score table,
#       2. the second is the score dataset organized by model_name
# score_table_dict_pkfp:
#       the pickle file path which stores the score_table_dict_pkfp
def ProcessRougeScoreDic2Excel(result_pk_fp, result_xls_fp, ROUGEScrMtx=ScrMtx_matrix, drawfig=0):
    # ----- Get the ROUGE score dictionary  ------
    score_dict = LoadSxptext(result_pk_fp)
    # ----- Get the size and names of Model & Score & Metric from the ROUGE score dict ------
    # Get the model id list which is both contained in this ROUGE score dict and in total models set.
    sys_mid_lst = [mid for mid in sorted(score_dict.keys()) if IDName.has_key(mid)]
    model_num = len(sys_mid_lst)    # The number of models in the ROUGE score dict
    score_num = 0                  # The number ROUGE score types (ROUGE-?) in the ROUGE score dict
    metric_num = 0                 # The number of ROUGE metric types (Average-P,R,F) in the ROUGE score dict
    model_id_idx_dict = {}         # Mapping model_id into the location index of model (midx)
    score_name_idx_dict = {}       # Mapping score_type into the location index of score (sidx)
    metric_name_idx_dict = {}      # Mapping metric_type into the location index of metric (kidx)
    # ------- Get the id_to_location_index dictionaries -------
    for midx, modelid in enumerate(sys_mid_lst):  # 02, 03,..
        model_id_idx_dict[modelid] = midx
        score_metric = score_dict[modelid]
        score_keys_lst = score_metric.keys()
        if score_num < len(score_keys_lst):
            score_num = len(score_keys_lst)
        for sidx, scorekey in enumerate(score_keys_lst):
            score_name_idx_dict[scorekey] = sidx
            metric_val = score_metric[scorekey]
            if metric_num < len(metric_val):
                metric_num = len(metric_val)
            for k, val in enumerate(metric_val):
                metric_name_idx_dict[val[0]] = k

    print "ROUGE (model_num, score_num, metric_num) =", (model_num, score_num, metric_num)
    print 'model_id_list: ', sys_mid_lst
    # print 'model_id_idx_dict', model_id_idx_dict
    # print 'score_name_idx_dict', score_name_idx_dict
    # print 'metric_name_idx_dict', metric_name_idx_dict

    # ---------------------- Get the ROUGE score value numpy array ----------------------
    # score_array: is a 3D array storing the ROUGE scores,
    #              the value can be fetched by the location index (model_idx, score_idx, metric_idx)
    score_array = np.ndarray((model_num, score_num, metric_num), dtype=float)
    # ---- Store the score values into score_array ----
    for modelid in sys_mid_lst:  #02, 03,..
        score_metric = score_dict[modelid]
        midx = model_id_idx_dict[modelid]
        for scorekey in score_metric.keys():
            metric_val = score_metric[scorekey]
            sidx = score_name_idx_dict[scorekey]
            for val in metric_val:
                # Here, each val = [metric_name, [score_value, ci_begin, ci_end]], ci is the confidence interval.
                kidx = metric_name_idx_dict[val[0]]
                score_array[midx, sidx, kidx] = val[1][0]

    # ------- Organize the score in precision, recall, and f-score, each is created as a excel table ----------
    workbook = xlsxwriter.Workbook(result_xls_fp)
    worksheet = workbook.add_worksheet()
    score_name_table_dict = {}  # the score_type organized score value tables

    # ---- write the score value into the excel file ----
    rown = 0
    for scrmtx in ROUGEScrMtx:
        # Get the index of this score type in the score_array which is a array storing the ROUGE score values.
        score_type = scrmtx[0]
        if not score_name_idx_dict.has_key(score_type):
            print ("no such %s score type in this ROUGE score dictionary" % score_type)
            continue
        sidx = score_name_idx_dict[score_type]
        # Get metrics list, i.e., [Average-P,Average-R,Average-F]
        metricslst = []
        for mtx in scrmtx[1:]:
            if metric_name_idx_dict.has_key(mtx):
                metricslst.append(mtx)
            else:
                print ("no such %s metric type in this ROUGE score dictionary" % mtx)
        # Use Each line in ROUGEScrMtx as the header, write header into the excel.
        scr_header = [score_type] + metricslst
        for coli, hdr in enumerate(scr_header):
            worksheet.write(rown, coli, hdr)
        # Create a 'table' which stores ROUGE scores in order to draw a figure
        table = []
        # Write each model's value on Metrics: Average-P and Average-R and Average-F
        for modelid in sys_mid_lst:
            rown = rown + 1
            midx = model_id_idx_dict[modelid]
            model_name = IDName[modelid]
            # cur_row stores the information for current 'model_name' under the current 'score_type'
            # The first element of this row is model name as the header
            # The second element of this row is the value list.
            cur_row = [model_name, []]
            worksheet.write(rown, 0, model_name)
            # write each model's score value under each Metrics into excel file.
            for coli, metric_type in enumerate(metricslst):
                kidx = metric_name_idx_dict[metric_type]  # Get the metrics location index
                score_value = score_array[midx, sidx, kidx]  # Get the ROUGE score value
                worksheet.write(rown, coli+1, score_value)  # Write the score into the excel file
                cur_row[1].append(score_value)  # Append the score into current row
            # If the current model is processed over, append the current row into the table
            table.append(cur_row)
        print table
        # For current score_type, add the header and the value table into score_name_table_dict.
        score_name_table_dict[score_type] = [scr_header, table]
        rown = rown + 2  # +2 is in order to leave a blank line in the excel table for better observation.
    workbook.close()
    # Store ROUGE score tables dictionary into pickle file.
    resultdir, pkfname = GetFilePathName(result_pk_fp)
    score_table_dict_pkfp = os.path.join(resultdir, pkfname.split('.')[0] + '.ROUGE_score_table_dict.pk')
    StoreSxptext(score_name_table_dict,  score_table_dict_pkfp)
    # If showfig = 1, we draw figures for the score tables
    if drawfig:
        cmyPlotBar.PlotScoreTables2BarFig(score_table_dict_pkfp, ifshow=0)
    return score_table_dict_pkfp

# ---- ParseScoreTxt2ScoreDic creates ROUGE score dict, stores in pickle file, and draws score dict as excel file ----
# Inputs:
# 1. result_txt_fp: the original ROUGE score text file path.
# 2. result_pk_fp: the pickle file path to store the ROUGE score dict.
# 3. result_xls_fp: the excel file path we want to create.
# Outputs:
# 1. ROUGE_score_dict: ROUGE score dictionary object
#   1.1 each key is a model ID
#   1.2 each value is also a dict, which use score metrics as keys and value is a list of [metric_name, value].
def ParseScoreTxt2ScoreDic(result_txt_fp, result_pk_fp):
    print "==========================================="
    print 'Processing txt file: ', result_txt_fp
    midlst_in_fname = GetMidsFileName(result_txt_fp)
    print 'Model ID list in file name:', midlst_in_fname
    print 'Creating ROUGE score dict ...'
    ROUGE_score_dict = ParseMultiSysOutput(result_txt_fp, midlst_in_fname)
    print 'Storing ROUGE score dict ...'
    StoreSxptext(ROUGE_score_dict, result_pk_fp)
    return

# ---- ParseMultiSysOutput parse the ROUGE score in text form into ROUGE score dict ----
# Inputs:
# 1. result_txt_fp: the ROUGE score text file path
# 2. score_dict: The empty ROUGE score dict which is built by test model IDs.
# Outputs: we add ROUGE scores for each model ID into score_dict, and then return it.
def ParseMultiSysOutput(result_txt_fp, midlst_in_fname):
    # Get ROUGE score content score_txt in result_txt_fp
    score_txt = ReadTextUTF(result_txt_fp)
    # Initiate ROUGE score dict
    ROUGE_score_dict = {}
    # We set parse_pattern to get:
    # (1) model_id: (\d\d); (2) score_type: (ROUGE-\S+); (3) metric_type: (Average_\w); (4) score_value: (\d.\d+)
    # (5) ci_begin, i.e. confidence interval begin: (\d.\d+); (6) ci_end: (\d.\d+)
    #    [---- confidence do not draw in excel ----]
    parse_pattern = re.compile(r'(\d\d) (ROUGE-\S+) (Average_\w):\s+(\d.\d+)\s+' + r"\(95%-conf.int. (\d.\d+) - (\d.\d+)\)")
    # Parse each text line in score_txt
    for line in score_txt.split("\n"):
        # print line
        match = parse_pattern.match(line)
        if match:
            model_id, score_type, metric_type, score_value, ci_begin, ci_end = match.groups()
            print model_id, score_type, metric_type, score_value, ci_begin, ci_end
            mtxval = [metric_type, [score_value, ci_begin, ci_end]]
            if not ROUGE_score_dict.has_key(model_id):
                ROUGE_score_dict[model_id] = {}
            if not ROUGE_score_dict[model_id].has_key(score_type):
                ROUGE_score_dict[model_id][score_type] = []
            ROUGE_score_dict[model_id][score_type].append(mtxval)
            if model_id not in midlst_in_fname:
                print ('Model ID %s is not in file name!' % model_id)
    for mid in midlst_in_fname:
        if not ROUGE_score_dict.has_key(mid):
            print ('Model ID %s in file name are not evaluate in .txt file!' % mid)
    return ROUGE_score_dict


#######################################################################################
# ------------------------------ Test Functions ------------------------------------- #
#######################################################################################
def TestSxpPyrougeScoreXlsFile(result_pk_fp="", result_xls_fp="", drawfig=0):
    if len(result_pk_fp)==0:
        result_pk_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.txt.pk"
    if len(result_xls_fp) == 0:
        result_xls_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.rouge_score_dim.xls"
    ProcessRougeScoreDic2Excel(result_pk_fp, result_xls_fp, drawfig=drawfig)


def TestSxpROUGEScoreTxtFile():
    result_txt_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.txt"
    result_pk_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.txt.pk"
    result_xls_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.rouge_score_dim.xls"
    ParseScoreTxt2ScoreDic(result_txt_fp, result_pk_fp)

#######################################################################################
# ------------------------------ Main Functions ------------------------------------- #
#######################################################################################
def main():
    # TestSxpPyrougeScoreXlsFile()
    TestSxpROUGEScoreTxtFile()

if __name__ == '__main__':
    main()


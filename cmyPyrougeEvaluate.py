#coding=utf-8

# -------------------------------------------------------------------------------
# Name:        cmyPyrougeEvaluate  (rewrite from sxpPyrougeEvaluate.py)
# Purpose:
#   1. RunPaperMyRougeHtml: create MyRouge155 object to get ROUGE evaluation score
#   2. CallMyPyrouge: first check the usability of config dict, and then call RunPaperMyRougeHtml
#   3. MyRouge155.ProduceSysModPair will produce the file name pairs between system and model summaries
#   4. MyProduceSysModPair: first check the usability of config dict, and then call MyRouge155.ProduceSysModPair
# -------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from pyrouge import Rouge155
from pyrouge import MyRouge155
from cmyToolkit import *
from cmyRougeConfig import *

global perlpathname
# perlpathname = r'perl'  # I have add perl_home_dir into the 'Path' of windows environment variables,
                        # so can set the default perl path as r'perl'
perlpathname = r'C:\Program Files (x86)\Perl\bin\perl'


#######################################################################################
# ---------- Call ROUGE to evaluate the automatically generated summaries ----------- #
#######################################################################################
# ------ RunPaperMyRougeHtml: create MyRouge155 object to evaluate the generated summaries --------
def RunPaperMyRougeHtml(system_path, model_path, systempattern,  modelpattern, config_file_path=None, systemidlst=[]):
    r = MyRouge155()
    r.system_dir = system_path
    r.model_dir = model_path
    r.system_filename_pattern = systempattern
    r.model_filename_pattern = modelpattern
    r.config_file = config_file_path
    output = r.evaluate(system_id=systemidlst, conf_path=config_file_path, PerlPath=perlpathname)
    print(output)
    return output


# ------ CallMyPyrouge: first check the usability of config dict, and then call RunPaperMyRougeHtml -------
def CallMyPyrouge(conf_dict, result_txt_fp):
    # --------- Check config dict for ROUGE evaluation -----------
    if not CheckConfDict(conf_dict):
        return
    # --------- Get configs for ROUGE evaluation -----------
    conf_name = GetConfName(conf_dict)
    systemidlst = GetConfSysMidLst(conf_dict)
    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    system_pattern, model_pattern = GetConfAboutSumFnamePt(conf_dict)
    # --------- Check whether config dict contains .xml type of summarization correspondence -----------
    rouge_xml_path = os.path.join(output_path, conf_name + '_' + '_'.join(systemidlst)+ '.rouge_conf.xml')
    # --------- Call ROUGE Evaluation functions
    result_txt = RunPaperMyRougeHtml(system_path, model_path, system_pattern, model_pattern, rouge_xml_path, systemidlst)
    WriteStrFile(result_txt_fp, result_txt, 'utf-8')
    return result_txt

# ------ MyProduceSysModPair: first check the usability of config dict, and then call MyRouge155.ProduceSysModPair -------
# ------ MyRouge155.ProduceSysModPair will produce the file name pairs between system and model summaries ---------------
def MyProduceSysModPair(conf_dict):
    # --------- Check config dict for ROUGE evaluation -----------
    if not CheckConfDict(conf_dict):
        return
    # --------- Get configs for ROUGE evaluation -----------
    systemidlst = GetConfSysMidLst(conf_dict)
    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    system_pattern, model_pattern = GetConfAboutSumFnamePt(conf_dict)
    return MyRouge155.ProduceSysModPair(system_path, model_path, systemidlst, model_pattern, system_pattern)

#######################################################################################
# ---------------------------------- Test Functions --------------------------------- #
#######################################################################################
def Test():
    conf_name = r"kg_exc_withstop_maxword"
    systemidlst = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
    conf_dict = GetRougeConfDict(conf_name, systemidlst)
    result_txt_fp, result_pk_fp, result_xls_fp = GetROUGEFilePaths(conf_dict)
    CallMyPyrouge(conf_dict, result_txt_fp)


#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    Test()

if __name__ == '__main__':
    main()

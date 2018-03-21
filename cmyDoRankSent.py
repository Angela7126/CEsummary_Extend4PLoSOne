# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------------------
# Name:        cmyDoRankSent (rewrite from sxpdorank.py)
# Purpose:
#
# -------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from cmyToolkit import *
from cmyRougeConfig import *
# ---------- Import Original 9 Models -------------
from Model_Original.Para import Para
from Model_Original.TFIDF import TfIdf
from Model_Original.SimGraph import SimGraph
from Model_Original.WordGraph import WordGraph
from Model_Original.ParaCtx import ParaCtx
from Model_Original.ParaSimHybird import ParaSimHybird
from Model_Original.SecParaCtx import SecParaCtx
from Model_Original.SecPara import SecPara
from Model_Original.SecTitle import SecTitle
# ---------- Import CE Pure Models -------------
from Model_CEPure.CESimGraph import CESimGraph
from Model_CEPure.CELocPosSeq import CELocPosSeq
from Model_CEPure.CELocNegSeq import CELocNegSeq
from Model_CEPure.CESecLocPosSeq import CESecLocPosSeq
from Model_CEPure.CESecLocNegSeq import CESecLocNegSeq
from Model_CEPure.CETfIdf import CETfIdf
# ---------- Import CE Filter Models -------------
from Model_CEFilter.CEFilter_Para import CEFilter_Para
from Model_CEFilter.CEFilter_ParaCtx import CEFilter_ParaCtx
from Model_CEFilter.CEFilter_ParaSimHybird import CEFilter_ParaSimHybird
from Model_CEFilter.CEFilter_SecPara import CEFilter_SecPara
from Model_CEFilter.CEFilter_SecParaCtx import CEFilter_SecParaCtx
from Model_CEFilter.CEFilter_SecTitle import CEFilter_SecTitle
from Model_CEFilter.CEFilter_SimGraph import CEFilter_SimGraph
from Model_CEFilter.CEFilter_TfIdf import CEFilter_TfIdf
from Model_CEFilter.CEFilter_WordGraph import CEFilter_WordGraph
# ---------- Import CE Bias Models -------------
from Model_CEBias.CEBias_Para import CEBias_Para
from Model_CEBias.CEBias_ParaCtx import CEBias_ParaCtx
from Model_CEBias.CEBias_ParaSimHybird import CEBias_ParaSimHybird
from Model_CEBias.CEBias_SecPara import CEBias_SecPara
from Model_CEBias.CEBias_SecParaCtx import CEBias_SecParaCtx
from Model_CEBias.CEBias_SecTitle import CEBias_SecTitle
from Model_CEBias.CEBias_SimGraph import CEBias_SimGraph
from Model_CEBias.CEBias_TfIdf import CEBias_TfIdf
from Model_CEBias.CEBias_WordGraph import CEBias_WordGraph
# ---------- Import CE Iter Models -------------
from Model_CEIter.CEIter_Para import CEIter_Para
from Model_CEIter.CEIter_ParaCtx import CEIter_ParaCtx
from Model_CEIter.CEIter_ParaSimHybird import CEIter_ParaSimHybird
from Model_CEIter.CEIter_SecPara import CEIter_SecPara
from Model_CEIter.CEIter_SecParaCtx import CEIter_SecParaCtx
from Model_CEIter.CEIter_SecTitle import CEIter_SecTitle

#######################################################################################
# --------------------------------- Write html files  ------------------------------- #
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

#######################################################################################
# ----------------------- Functions for output ranked sentences --------------------- #
#######################################################################################
def OutputTopKSent(model, topksent=default_topk, maxwords=default_maxw, useabstr=default_useabstr, strictmax=default_strict_maxw):
    ranked_sentences = model.ranked_sentences
    # Get the number of words in abstract and conclusion
    abswords = 0
    concwords = 0
    if len(model.text.abstract) > 0:
        abswords = len(DelEmptyString(model.text.abstract.replace('**.\n', ' ').strip().split(' ')))
    if len(model.text.conclusion) > 0:
        concwords = len(DelEmptyString(model.text.conclusion.replace('**.\n', ' ').strip().split(' ')))
    # Get configures to control the length of generated summaries
    usetopk = False
    if useabstr == 0 and maxwords == -1:
        usetopk = True
    if useabstr == 1 and abswords > 0:
        maxwords = abswords
    if useabstr == 2 and concwords > 0:
        maxwords = concwords
    if useabstr == 3 and abswords > 0 and concwords > 0:
        maxwords = (abswords + concwords)/2
    if useabstr == 4 and abswords > 0 and concwords > 0:
        maxwords = (abswords + concwords)*2 / 3
    if (useabstr == 3 or useabstr == 4) and abswords > 0 and concwords == 0:
        maxwords = abswords
    if (useabstr == 3 or useabstr == 4) and abswords == 0 and concwords > 0:
        maxwords = concwords
    # print "abswords: ", abswords
    # print "concwords: ", concwords
    # print "useabstr: ", useabstr
    # print "maxwords: ", maxwords
    # Get the text of top ranked sentences
    sent_txt_set = []
    added_snum = 0
    added_wnum = 0
    for sentence in ranked_sentences:
        # Skip the sentence which less than 2 str.
        if len(sentence.sentence_text) <= 1:
            continue
        # Get top sentence text set
        cur_words = DelEmptyString(sentence.sentence_text.split(' '))
        cur_wnum = len(cur_words)
        if usetopk:
            if added_snum >= topksent:
                break
        else:
            if added_wnum >= maxwords:
                break
            elif added_wnum + cur_wnum > maxwords:
                if strictmax == 0:
                    break
                else:
                    seglen = maxwords - added_wnum
                    segsent = ' '.join(cur_words[0:seglen])
                    sent_txt_set.append(segsent)
                    break
        sent_txt_set.append(' '.join(cur_words))
        added_snum = added_snum + 1
        added_wnum = added_wnum + cur_wnum
    return sent_txt_set


def OutputAllRankSent(model):
    sent_txt_set = []
    for sentence in model.ranked_sentences:
        sent_txt_set.append(sentence.sentence_text)
    return sent_txt_set


def OutputTopKSentWeight(model, topksent=default_topk, maxwords=default_maxw, useabstr=default_useabstr, strictmax=default_strict_maxw):
    ranked_weight = [model.s[model.idx_s[(i, 0)]] for i in range(len(model.s))]
    # Get the number of words in abstract and conclusion
    abswords = 0
    concwords = 0
    if len(model.text.abstract) > 0:
        abswords = len(model.text.abstract.replace('**.\n', ' ').strip().split(' '))
    if len(model.text.conclusion) > 0:
        concwords = len(model.text.conclusion.replace('**.\n', ' ').strip().split(' '))
    # Get configures to control the length of generated summaries
    usetopk = False
    if useabstr == 0 and maxwords == -1:
        usetopk = True
    if useabstr == 1 and abswords > 0:
        maxwords = abswords
    if useabstr == 2 and concwords > 0:
        maxwords = concwords
    if useabstr == 3 and abswords > 0 and concwords > 0:
        maxwords = (abswords + concwords) / 2
    if useabstr == 4 and abswords > 0 and concwords > 0:
        maxwords = (abswords + concwords) * 2 / 3
    if (useabstr == 3 or useabstr == 4) and abswords > 0 and concwords == 0:
        maxwords = abswords
    if (useabstr == 3 or useabstr == 4) and abswords == 0 and concwords > 0:
        maxwords = concwords
    # print maxwords
    # Get the text of top ranked sentences
    sent_weight_idx_set = []
    added_snum = 0
    added_wnum = 0
    for i, sentence in enumerate(model.ranked_sentences):
        # Skip the sentence which less than 2 str.
        if len(sentence.sentence_text) <= 1:
            continue
        # Get top sentence text set
        cur_words = sentence.sentence_text.split(' ')
        cur_wnum = len(cur_words)
        sent_weight_idx = [sentence.sentence_text, ranked_weight[i], model.idx_s[(i, 0)]]
        if usetopk and added_snum >= topksent:
            break
        elif added_wnum + cur_wnum > maxwords:
            if strictmax == 0:
                break
            else:
                sent_weight_idx_set.append(sent_weight_idx)
                break
        added_snum = added_snum + 1
        added_wnum = added_wnum + cur_wnum
        sent_weight_idx_set.append(sent_weight_idx)
    return sent_weight_idx_set


def OutputTopKWord(model, topkword=default_topkword):
    ranked_word = [model.words[model.idx_w[(i, 0)]] for i in range(len(model.words))]
    topword_set = []
    for i, eachword in enumerate(ranked_word):
        if i >= topkword:
            break
        topword_set.append(eachword)
    return topword_set

#######################################################################################
# ---- Prepare the file mapping for sentence ranking and automatic summarization ---- #
#######################################################################################
# ------- Generate a dict mapping sxpText pickle file names to file name prefixes for system summaries -------
# We account files in model_html directory and find corresponding files in pickle directory,
# We collect the name of these pickle files and map these names into prefix of the file name of system summaries
def PreparePickleByModelFileSet(model_path, mod_fnamept_id, pickle_path, pk_fnamept_id, sys_fnamept_id):
    # ---- get file id list from model summaries file names ----
    model_set_id = []
    modfnamelist, modsubdirlist = sxpGetDirFileList(model_path)
    model_filenames_pattern_id = re.compile(mod_fnamept_id)
    for modfname in modfnamelist:
        match = model_filenames_pattern_id.match(modfname)
        if match:
            model_set_id.append(match.groups(1)[0])
    # ---- Generate a dict mapping a sxpText file names to file name prefixes of system summaries  ----
    pk_sys_fname_dict = {}
    pkfnamelist, pksubdirlist = sxpGetDirFileList(pickle_path)
    for eachid in model_set_id:
        pkfname = pk_fnamept_id.replace('#ID#', eachid)
        sysfname = sys_fnamept_id.replace('#ID#', eachid)
        if pkfname in pkfnamelist:
            pk_sys_fname_dict[pkfname] = sysfname
    return pk_sys_fname_dict


def GetSystemModelFilePair(conf_dict):
    # ------- Get configures ---------
    system_id_list = GetConfSysMidLst(conf_dict)
    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    pickle_path, celstpk_path, pk_fnamept_id = GetConfAboutPickleFiles(conf_dict)
    sys_fnamept_id, mod_fnamept_id = GetConfAboutAuxSumFnamePt(conf_dict)
    # ------- Get dict maps pickle file names to generated summaries name prefix --------
    pk_sys_fname_dict = PreparePickleByModelFileSet(model_path, mod_fnamept_id, pickle_path, pk_fnamept_id, sys_fnamept_id)
    for pk_sys_fname in pk_sys_fname_dict.items():
        print pk_sys_fname
    # ------- Get Keyword Benchmark file path ------------
    if conf_dict.has_key(u'keyword_bench_path'):
        keyword_bench_path = conf_dict[u'keyword_bench_path']
    else:
        keyword_bench_path = ''
    # -------
    all_model = []
    for sysmid in system_id_list:
        print ('working on', sysmid, IDName[sysmid])
        model_files = []
        for file_name, system_name in pk_sys_fname_dict.items():
            pickle_file = os.path.join(pickle_path, file_name)
            topksent_path = os.path.join(system_path, system_name + '.' + sysmid)
            file_dict = {}
            if len(keyword_bench_path) > 0:
                keybench = os.path.join(keyword_bench_path, file_name+'.key')
            else:
                keybench = ''
            file_dict['modelpatter'] = mod_fnamept_id
            file_dict['systemname'] = IDName(sysmid)
            file_dict['systemid'] = sysmid
            file_dict['filepk'] = pickle_file
            file_dict['sys'] = topksent_path
            file_dict['allsentpk'] = topksent_path + 'allsent.pk'
            file_dict['topsentpk'] = topksent_path + 'topsent.pk'
            file_dict['keyword'] = keybench
            print('allsent:', file_dict['allsentpk'])
            model_files.append(file_dict)
        all_model.append(model_files)
    return all_model


# ----- GetComparingText: Preparing standard summaries according Abstract and Conclusion in papers ----
# 1. dataroot: get the root directory for current corpus
# 2. model_html: the directory for standard summaries
# 3. pk_path: the sxpText object pickle directory
# 4. cmptype: the type of standard summaries to be create
#             =1 means use Abstract as standard summaries, summary file name is labeled by suffix ".A.html"
#             =2 means use Conclusion as standard summaries, summary file name is labeled by suffix ".B.html"
#             =other_value means both Abstract and Conclusion as standard summaries,
#                          summary file name is labeled by suffix ".C.html"
def GetComparingText(dataroot, model_html, pk_dir, file_dir, cmptype=0):
    print "Preparing standard summaries according Abstract and Conclusion in papers"
    # -- create the directory which store the comparing text serve as manual summary for each paper --
    if not os.path.exists(model_html):
        os.makedirs(model_html)

    # -- get the original filename list in the path variable --
    file_list = sxpGetDirFileList(file_dir)[0]

    # --  get sxpText objects --
    for i, file_name in enumerate(file_list):
        fset = file_name.split('.')
        if fset[-1] not in ['txt', 'xhtml']:  # if current file is not a txt file, it is not one of the original papers
            continue
        print "getting ", i, "th paper's comparing text named as", file_name, "type = ", cmptype
        # -- get single pickle file directory --
        # -- pk_path is the directory which store sxpText object pickle file --
        pickle_fpath = os.path.join(pk_dir, file_name + '_2.pickle')
        sxptxt = LoadSxptext(pickle_fpath)
        # -- save text abstact text and conclusion text --
        cmptype = cmptype if cmptype <= 3 else 3
        comptxt_dir = os.path.join(model_html, file_name+'.'+["C","A","B","C"][cmptype]+'.html')
        if cmptype == 1:
            comptxt = sxptxt.abstract
        elif cmptype == 2:
            comptxt = sxptxt.conclusion
        else:
            comptxt = sxptxt.abstract + ' ' + sxptxt.conclusion
        # split the comparing text into sentences by "**." and delete empty sentences
        comptxtlst = DelEmptyString((comptxt.strip()+'\n').split('**.\n'))
        if len(comptxtlst) == 0:
            continue
        # create file content and write file
        ct = ProduceSystem(comptxtlst, file_name, 1)
        WriteStrFile(comptxt_dir, ct, 'utf-8')
    print "Preparing complete!"


#######################################################################################
# ----- Rank sentences and extract higher rank sentences to generate summaries ------ #
#######################################################################################
# -------- RunOneRankModel: rank sentences with a specific ranking model according to configs in conf_dict --------
# Inputs:
# 1. pickle_path: the directory of sxpText pickle files
# 2. pk_sys_set: the dict maps the pickle file name to the prefix of system summaries file name
# 3. system_path: the directory of system summaries
# 4. system_id: the ranking model's ID
# 5. conf_dict: the dict stores all the configs
def RunOneRankModel(pickle_path, pk_sys_set, system_path, system_id, conf_dict):
    useabstr, maxw, topk, strictmax, remove_stopword = GetConfAboutSumLength(conf_dict)
    modeltype = IDName[system_id]
    # Get option configs of cause-effect links
    ceopt = "mance"
    if modeltype[0:3] == 'SCE':
        ceopt = "sysce"
    print ("---- Ranking sentences by model %s under config %s ----" %(modeltype, GetConfName(conf_dict)))
    pk_fname_lst = sorted(pk_sys_set.keys())
    for pk_fname in pk_fname_lst:
        print (" -- Ranking file %s ..." %pk_fname)
        pkfp = os.path.join(pickle_path, pk_fname)
        # --- 获取ranking model object pickle path ----
        sys_sum_fname = pk_sys_set[pk_fname]
        model_pk_path = os.path.join(system_path, sys_sum_fname+'.'+system_id+'model.pk')
        # --- 若ranking model object 存在，直接Load ----
        if os.path.exists(model_pk_path):
            model = LoadSxptext(model_pk_path)
        # --- 若之前未创建过该ranking model object，则新建----
        else:
            # ----------------- For 9 Original Models ----------------
            if modeltype == 'Para':
                model = Para(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'TFIDF':
                model = TfIdf(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'SimGraph':
                model = SimGraph(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'WordGraph':
                model = WordGraph(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'ParaCtx':
                model = ParaCtx(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'SecPara':
                model = SecPara(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'SecParaCtx':
                model = SecParaCtx(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'Hybird':
                model = ParaSimHybird(pkfp, remove_stopwords=remove_stopword)
            if modeltype == 'SecTitle':
                model = SecTitle(pkfp, remove_stopwords=remove_stopword)
            # ----------------- For CEPure Models ----------------
            if modeltype[1:] == "CESimGraph":
                model = CESimGraph(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == "CELocPosSeq":
                model = CELocPosSeq(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == "CELocNegSeq":
                model = CELocNegSeq(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == "CESecLocPosSeq":
                model = CESecLocPosSeq(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == "CESecLocNegSeq":
                model = CESecLocNegSeq(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == "CETFIDF":
                model = CETfIdf(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            # ----------------- For CE Filter Models ----------------
            if modeltype[1:] == 'CEFilter_Para':
                model = CEFilter_Para(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_TFIDF':
                model = CEFilter_TfIdf(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_SimGraph':
                model = CEFilter_SimGraph(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_WordGraph':
                model = CEFilter_WordGraph(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_ParaCtx':
                model = CEFilter_ParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_SecPara':
                model = CEFilter_SecPara(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_SecParaCtx':
                model = CEFilter_SecParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_Hybird':
                model = CEFilter_ParaSimHybird(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEFilter_SecTitle':
                model = CEFilter_SecTitle(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            # ----------------- For CE Bias Models ----------------
            if modeltype[1:] == 'CEBias_Para':
                model = CEBias_Para(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_TFIDF':
                model = CEBias_TfIdf(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_SimGraph':
                model = CEBias_SimGraph(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_WordGraph':
                model = CEBias_WordGraph(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_ParaCtx':
                model = CEBias_ParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_SecPara':
                model = CEBias_SecPara(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_SecParaCtx':
                model = CEBias_SecParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_Hybird':
                model = CEBias_ParaSimHybird(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEBias_SecTitle':
                model = CEBias_SecTitle(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
                # ----------------- For CE Filter Models ----------------
            if modeltype[1:] == 'CEIter_Para':
                model = CEIter_Para(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEIter_ParaCtx':
                model = CEIter_ParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEIter_SecPara':
                model = CEIter_SecPara(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEIter_SecParaCtx':
                model = CEIter_SecParaCtx(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEIter_Hybird':
                model = CEIter_ParaSimHybird(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            if modeltype[1:] == 'CEIter_SecTitle':
                model = CEIter_SecTitle(pkfp, ceopt=ceopt, remove_stopwords=remove_stopword)
            # ----- 存储新建的model对象 -----
            StoreSxptext(model, model_pk_path)
        # ----- Get system summary with top k sentences ------
        tops_text = OutputTopKSent(model, topk, maxw, useabstr, strictmax=strictmax)
        # print tops_text
        if len(tops_text) == 0:
            continue
        # ----- Get system summary file path for top k sentences ------
        topksent_path = os.path.join(system_path, sys_sum_fname + '.'+system_id)
        # ----- store system summary into system summary file path  ------
        st = ProduceSystem(tops_text, pk_fname, 1)
        WriteStrFile(topksent_path, st, 'utf-8')
        # ------ Store top k sentences into pickle file -------------
        topsent_pk_file = topksent_path + 'topsent.pk'
        StoreSxptext(tops_text, topsent_pk_file)
        # ------- Get all sentences and store them into pickle --------
        allsent = OutputAllRankSent(model)
        pkfname = topksent_path + 'allsent.pk'
        StoreSxptext(allsent, pkfname)
    print "result is ok"


def RankSentForSysSum(conf_dict):
    # ------- Get configures ---------
    system_id_list = GetConfSysMidLst(conf_dict)
    system_path, model_path, output_path = GetConfAboutFileDirs(conf_dict)
    pickle_path, celstpk_path, pk_fnamept_id = GetConfAboutPickleFiles(conf_dict)
    sys_fnamept_id, mod_fnamept_id = GetConfAboutAuxSumFnamePt(conf_dict)
    # ------- Get dict maps pickle file names to generated summaries name prefix --------
    pk_sys_set = PreparePickleByModelFileSet(model_path, mod_fnamept_id, pickle_path, pk_fnamept_id, sys_fnamept_id)
    for sysmid in system_id_list:
        RunOneRankModel(pickle_path, pk_sys_set, system_path, sysmid, conf_dict)



#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
def main():
    conf_name = r'kgmance_inc_withstop_maxword'
    sysmid_list = ['08']
    useabstr = 4
    conf_dict = GetRougeConfDict(conf_name, sys_mid_lst=sysmid_list, useabstr=useabstr)
    if CheckConfDict(conf_dict):
        RankSentForSysSum(conf_dict)
    else:
        print "config_dict is error!"



if __name__ == '__main__':
    # main()
    model_html = os.path.join(acl_dir, "model_html")
    pkdir = os.path.join(acl_dir, "pickle")
    filedir = os.path.join(acl_dir, r'files')
    GetComparingText(acl_dir, model_html, pkdir, filedir, cmptype=0)
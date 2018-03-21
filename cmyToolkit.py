# -*- coding: UTF-8 -*- 

#######################################################################################
# --------------------------------- Function Introduce ------------------------------ #
#######################################################################################
# This functions set includes some public functions for the whole project:
# 1. changing a PDF file to a txt file;
# 2. load and dump some data from or to a pk_type file.
# 3. Read and Process Files
# 4. Make file path;

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import nltk
import pickle
import re
import codecs
import urllib
import copy
import numpy as np
import xlrd
import xlsxwriter
import xlwt
from tkMessageBox import *

# --------- set some folder path ------------------
project_root_dir = os.path.dirname(os.path.abspath("cmyToolkit.py"))

corpdir = os.path.join(project_root_dir, "Corpus")
pkdir = os.path.join(project_root_dir, "PK")
DICpkdir = os.path.join(pkdir, "DIC")

kg_dir = os.path.join(project_root_dir, "kg")
acl_dir = os.path.join(project_root_dir, "acl")
duc_dir = os.path.join(project_root_dir, "duc")


#######################################################################################
# -------------------------------- File path related -------------------------------- #
#######################################################################################
# -------- Get file path --------
# This function combines the current work dir (cwd), a list of directories, and a filename into a file path.
# Explanation:
# 1. 'dirs' is a list of <str>, means the directories under the current work dir.
# 2. 'fname' is a str.
# 3. Output fp is a file path which is combined by cwd, dirs and fname.
def Getfp(dirs, fname):
    fp = os.getcwd()
    for d in dirs:
        fp = os.path.join(fp, d)
    fp = os.path.join(fp, fname)
    return fp

# ----- Create folders for some new files -----
# This function check whether the directory for a file exist, if not, creating them
# Explanation:
#    'newfp' is a <str> object, it records the absolute directory of a new file  
def CreatNewDir(newfp):
    newdir, fname = os.path.split(newfp)
    if not os.path.isdir(newdir):
        os.makedirs(newdir)
    return

# ----- Check whether there exits a directory, if it doesn't, create one -----
def CheckMkDir(dirname):
    if os.path.exists(dirname):
        return 1
    else:
        os.path.os.mkdir(dirname)
    return 1

# ---- Get the file name and the path of this file ----
def GetFilePathName(filepath):
    fname = os.path.basename(filepath)
    fdir = os.path.dirname(filepath)
    if len(fdir) == 0:
        return fname
    else:
        return (fdir, fname)

# ----- Get files name list and sub-directory name list inside the 'filedir' folder -----
def sxpGetDirFileList(filedir):
    filelist = []
    dirlist = []

    if not os.path.isdir(filedir):
        showerror('Error!', 'no dir to be read')
        return filelist, dirlist

    files = os.listdir(filedir)
    # now we first read each file in the txtPath
    for f in files:
        if os.path.isdir(os.path.join(filedir, f)):
            dirlist.append(f)
        else:
            filelist.append(f)

    return filelist, dirlist


# ---- Get the file paths inside 'fd' folder, and create accordingly new file paths in 'fd_new' folder ----
def Get_Build_fpathes(fd, fd_new):
    if not os.path.exists(fd):
        print "The path of corpus does not exist!"
        return

    if not os.path.exists(fd_new):
        os.mkdir(fd_new)

    file_pn = []
    file_pn_new = []

    files = os.listdir(fd)

    for f in files:
        df = os.path.join(fd, f)
        df_new = os.path.join(fd_new, f)
        if os.path.isdir(df):
            if not os.path.exists(fd_new):
                os.mkdir(fd_new)
            [subfile_pn, subfile_pn_new] = Get_Build_fpathes(df, df_new)
            file_pn.extend(subfile_pn)
            file_pn_new.extend(subfile_pn_new)
        else:
            file_pn.append(df)
            file_pn_new.append(df_new)

    return file_pn, file_pn_new


# ---- Get all files' path inside 'fd' folder (include files in sub-directory) ----
def Get_file_pathes(fd):
    if not os.path.exists(fd):
        print "The path of corpus does not exist!"
        return

    file_pn = []

    files = os.listdir(fd)

    for f in files:
        df = os.path.join(fd, f)
        if os.path.isdir(df):
            [subfile_pn] = Get_file_pathes(df)
            file_pn.extend(subfile_pn)
        else:
            file_pn.append(df)

    return file_pn


#######################################################################################
# --------------------------- PDF to txt/xml/html/tagged_PDF ------------------------ #
#######################################################################################
# This function rewrite a PDF file in txt/xml/html/tagged_PDF style.
# Explanation:
# 1. fp: the path of source file
# 2. newfp: the path of target file
# 3. tp: the type of target file -- belong to ("text","xml","html","tag") 
def Pdfparser(fp, newfp, tp):
    if not os.path.isfile(fp):
        raise IOError('Warning!', 'illegal input in Pdf2txt! There is no file as ' + fp)
    elif tp not in ("text", "xml", "html", "tag"):
        raise ValueError('Warning!',
                         "illegal input in Pdf2txt! The type of target file must in ('text','xml','html','tag')")
    CreatNewDir(newfp)
    os.system('pdf2txt.py -o ' + newfp + ' -t ' + tp + ' ' + fp)
    return


#######################################################################################
# ------------------------------- Dump & Load Pickle files -------------------------- #
#######################################################################################
# -------------------- Dump data into a file using pickle------------------------------
def Dumppickle(fpath, result):
    CreatNewDir(fpath)
    fp = codecs.open(fpath, 'wb', 'utf8')
    pickle.dump(result, fp)
    fp.close()
    return

# ----------------------- Load data from a file using pickle------------------------------
def Loadpickle(fpath):
    if not os.path.isfile(fpath):
        showerror('Warning!', 'illegal input in Loadpickle! There is no file as ' + fpath)
        return
    fp = open(fpath, 'rb')
    result = pickle.load(fp)
    fp.close()
    return result

# --------------------- Dump sxpText object in a pickle file --------------------------
def StoreSxptext(sxptxt, fname):
    f = open(fname, 'wb')
    pickle.dump(sxptxt, f)
    f.close()

# ---------------------- Load sxpText object from a pickle file --------------------------
def LoadSxptext(fname):
    f = open(fname, 'rb')
    sxptxt = pickle.load(f)
    f.close()
    return sxptxt

#######################################################################################
# ---------------------------- Encode and decode related ---------------------------- #
#######################################################################################
def ExtractEnglishWord(textstr):
    p = r'([A-Za-z0-9]+)([,\'\"\(\)\[\]\{\}\.\-\+\:\?\\]*)\s*'
    if isinstance(textstr, unicode):
        ustr = textstr.encode('utf-8')
    else:
        ustr = textstr.decode('utf-8')
    g = re.findall(p, textstr)
    return g


def strdecode(string, charset=None):
    if isinstance(string, unicode):
        return string
    if charset:
        try:
            return string.decode(charset)
        except UnicodeDecodeError:
            return _strdecode(string)
    else:
        return _strdecode(string)


def _strdecode(string):
    try:
        return string.decode('utf8')
    except UnicodeDecodeError:
        try:
            return string.decode('gb2312')
        except UnicodeDecodeError:
            try:
                return string.decode('gbk')
            except UnicodeDecodeError:
                return string.decode('gb18030')


def strencode(string, charset=None):
    if isinstance(string, str):
        return string
    if charset:
        try:
            return string.encode(charset)
        except UnicodeEncodeError:
            return _strencode(string)
    else:
        return _strencode(string)


def _strencode(string):
    try:
        return string.encode('utf8')
    except UnicodeEncodeError:
        try:
            return string.encode('gb2312')
        except UnicodeEncodeError:
            try:
                return string.encode('gbk')
            except UnicodeEncodeError:
                return string.encode('gb18030')


def GetTestTypeCode(s, ignore=False):
    typeset = []
    if isinstance(s, unicode):
        d = ('utf-8', 1, s)
        typeset.append(d)
        return typeset
    else:
        codetype = ['utf-8', 'gbk', 'gb2311']
        for ctype in codetype:
            try:
                if not ignore:
                    us = unicode(s, ctype)
                else:
                    us = unicode(s, ctype, 'ignore')
                d = (ctype, 1, us)
                typeset.append(d)

            except Exception as e:
                d = (ctype, 0, s)
                typeset.append(d)
    return typeset


def GetUnicode(s):
    if isinstance(s, unicode):
        return s
    typeset = GetTestTypeCode(s)
    restr = None
    for t in typeset:
        if t[1] == 1 and t[0] == 'utf-8':
            restr = t[2]
            break
        elif t[1] == 1:
            restr = t[2]
    return restr


def GetGBKStr(s):
    us = GetUnicode(s);
    if us[0] == 'utf-8':
        gs = us[1].encode('gbk');
    else:
        return s
    return gs


def GetUnicodePair(s):
    if isinstance(s, unicode):
        restr = ['utf-8', s]
        return restr
    typeset = GetTestTypeCode(s)
    restr = ['', s]
    for t in typeset:
        if t[1] == 1 and t[0] == 'utf-8':
            restr = ['utf-8', t[2]]
            break
        elif t[1] == 1:
            restr = [t[0], t[2]]
    return restr


def GetPrintUTFStr(s):
    if isinstance(s,unicode):
        restr = ['utf-8', s]
        return restr
    typeset = GetTestTypeCode(s)
    restr = ['utf-8', s]
    for i in range(len(typeset)):
            t = typeset[i]
            if t[1] == 1 and t[0] == 'utf-8':
                u = t[2]
                if isinstance(u, unicode)==False:
                    restr = ['utf-8', unicode(u, t[0])]
                else:
                    restr =['utf-8', u]
                break
            elif t[1] == 1:
                u = t[2]
                if isinstance(u,unicode)==False:
                    restr = (t[0], unicode(u, t[0]))
                else:
                    restr = ['utf-8', u]
    return restr

#######################################################################################
# ------------------------------- File Content related ------------------------------ #
#######################################################################################
# -------------------------- Read and Process Files -----------------------------
def WriteStrFile(filename, txtstr, encodetype='gbk'):
    ut = GetUnicode(txtstr)
    f = codecs.open(filename, 'w+', encodetype)
    f.write(ut)
    f.close()

def ReadFile(fpath):
    # cfn --> shot for current_file_name
    # fp --> the file type pointer
    # fstring --> the string stream of the current_file
    fp = open(fpath, 'r')
    fstring = fp.read()
    fp.close()

    return fstring


def ReadTextUTF(fname):
    try:
        f = codecs.open(fname, 'r', 'utf-8')
        txt = f.read()
        f.close()
        return txt
    except IOError:
        print 'Error in opening file', fname
        return []

# -----------------------------------get stop words-------------------------------------
def getStopWord():
    puncs = [u',', u'.', u':', u';', u'?',  u'!', u'&', u'*', u'@', u'#', u'$', u'%', u'-', u'+', u'=', u'\'', u'\"',
             u'|', u'~', u'^', u'’', u'”', u'`', u'``', u'--', u'\r', u'\n', u'\t', u'\\', u'/', u'(', u')', u'[', u']',
             u'{', u'}', u'<', u'>', u'\u222a', u'\u2190', u'\u2192', u'，', u'。', u'：', u'；', u'（', u'）',
             u'“', u'”', u'【', u'】', u'——', u'？', u'！', u'‘', u'《', u'》', u'…', u'、']
    fp = codecs.open(os.path.join(corpdir, 'stopwords.txt'), 'r', 'utf8')
    stopW = nltk.word_tokenize(fp.read())
    fp.close()

    Dumppickle(os.path.join(pkdir, 'StopW.pk'), stopW)
    Dumppickle(os.path.join(pkdir, 'Puncs.pk'), puncs)


def ReplaceNonEnglishCharacter(ssstr):
    if isinstance(ssstr, unicode):
        unc = ssstr
    else:
        unc = strdecode(ssstr, 'utf-8')
    p = re.compile(ur"([^\x00-\xff])")

    def func(m):  # add ' ' before and after the not matching content.
        st = repr(m.group(1).title())
        st = ' ' + st + ' '
        return st

    g = p.sub(func, unc)  # replace the str in unc that not satisfied p with string by func()
    return g

# ---- RemoveUStrSpace: remove some character that not in ascii scope, and redundant empty character ----- #
def RemoveUStrSpace(strtxt):
    if isinstance(strtxt, unicode):
        unc = strtxt
    else:
        unc = strdecode(strtxt, 'utf-8')
    pattern = re.compile(ur"[^\x20-\x7E]")
    nstr = pattern.sub(' ', unc)
    pattern = re.compile(ur"\s+")
    nstr = pattern.sub(' ', nstr).strip()
    return nstr

# ---- RemoveUStrSpace2: remove some character that not in ascii scope, string like u'\ua78e' and redundant empty character ----- #
def RemoveUStrSpace2(strtxt):
    if isinstance(strtxt, unicode):
        unc = strtxt
    else:
        unc = strdecode(strtxt, 'utf-8')
    pattern = re.compile(ur"[^\x20-\x7E]")
    nstr = pattern.sub(' ', unc)
    pattern = re.compile(r"u\'\\u[a-z0-9]{4}\'")
    nstr = pattern.sub(' ', nstr)
    pattern = re.compile(ur"\s+")
    nstr = pattern.sub(' ', nstr).strip()
    return nstr

#######################################################################################
# ------------------------ Some sentences similarity functions ---------------------- #
#######################################################################################
# ----- Calculate the similarity between two sentences -----
# If two sentences are all tf-idf vectors, calculate the cosine similarity
# If two sentences are all strings, calculate the jaccard similarity
# If the representation of two sentences are different,
def Similarity(sentence, s, stopw=0, punc=1):
    if re.match('.+', sentence):
        if re.match('.+', s):
            return jaccard_similarity(sentence, s, stopw, punc)
        else:
            print("The representation of these two sentences is different! Please uniform the sentence representation")
            return 0
    else:
        return cosine_similarity(sentence, s)

# ----- Calculate the Jaccard similarity between two sentences -----
# Calculate the similarity of word usage between sent1 and sent2.
# "stopword = 1" means we take out stopwords from two sentences; "stopword = 0" means remain stopwords in sentences.
# "punc = 1" means we take out punctuations from two sentences; "punc = 0" means remain punctuations in sentences.
# Jaccard(sent1, sent2) = |set(sent1_words) \intersection set(sent2_words)| / |set(sent1_words) \union set(sent2_words)|
def jaccard_similarity(sent1, sent2, stopword=0, punc=1):
    RemoveWords = []
    if stopword == 1:
        RemoveWords = Loadpickle(os.path.join(pkdir, 'StopW.pk'))
    if punc == 1:
        RemoveWords.extend(
            [u',', u'.', u':', u';', u'?',  u'!', u'&', u'*', u'@', u'#', u'$', u'%', u'-', u'+', u'=', u'\'', u'\"',
             u'|', u'~', u'^', u'’', u'”', u'`', u'``', u'--', u'\r', u'\n', u'\t', u'\\', u'/', u'(', u')', u'[', u']',
             u'{', u'}', u'<', u'>', u'\u222a', u'\u2190', u'\u2192', u'，', u'。', u'：', u'；', u'（', u'）',
             u'“', u'”', u'【', u'】', u'——', u'？', u'！', u'‘', u'《', u'》', u'…', u'、'])
    word_list1 = []
    word_list2 = []
    for word in nltk.word_tokenize(sent1.encode('utf-8')):
        if word.lower() not in RemoveWords:
            word_list1.append(word.lower())
    for word in nltk.word_tokenize(sent2.encode('utf-8')):
        if word.lower() not in RemoveWords:
            word_list2.append(word.lower())
    s1 = set(word_list2).intersection(set(word_list1))
    s2 = set(word_list2).union(set(word_list1))
    if len(s2) == 0:
        return 0
    return float(len(s1)) / float(len(s2))


# ----- Calculate the Jaccard similarity between two sentences -----
def cosine_similarity(sentence, s):
    x = np.array(sentence)
    y = np.array(s)
    Lx = np.sqrt(x.dot(x))
    Ly = np.sqrt(y.dot(y))
    cos_angle = x.dot(y)/(Lx * Ly)
    return cos_angle

#######################################################################################
# ---------------------------- Operations on list object ---------------------------- #
#######################################################################################
### ---- ListFlatten flat a high-dimensional list into a 1-dimensional list ----
def ListFlatten(lst):
    ans = []
    if type(lst) == list:
        for templst in lst:
            ans.extend(ListFlatten(templst))
    else:
        ans.append(lst)
    return ans


# ---- delete empty string in a string list ----
def DelEmptyString(strlist):
    i = 0
    while i < len(strlist):
        if strlist[i] == None or len(strlist[i].strip()) == 0:
            del strlist[i]
        else:
            i += 1
    return strlist


# ---- Delete some elements from a list and return the removed list ----
def DelLstElems(Lst, elems):
    # If elems is a list, remove these elements from Lst
    if type(elems) == list:
        for e in elems:
            if e in Lst:
                Lst.remove(e)
    # If elems is just an element, remove it from Lst
    else:
        if elems in Lst:
            Lst.remove(elems)
    return Lst

# ---- Delete some keys from a dict and return the removed dict ----
def DelDictKeys(a_dict, somekeys):
    b_dict = copy.deepcopy(a_dict)
    dict_keys = b_dict.keys()
    # If somekeys is a key list, remove these keys from a_dict
    if type(somekeys) == list:
        somekeys = list(set(somekeys))
        for k in somekeys:
            if k in dict_keys:
                del b_dict[k]
    # If somekeys is just a key, remove it from a_dict
    elif type(somekeys) == str:
        if somekeys in dict_keys:
            del b_dict[somekeys]
    else:
        pass
    return b_dict

#######################################################################################
# ---------------------------- Write and Read XLSX files ---------------------------- #
#######################################################################################
# ------------ WriteExcel write strings in a excel file ---------------
# 1. 'fp' is the excel file path you want to write
# 2. 'rwstrset' is the raw string set, it is a 3-Dimensional list.
#    Such as [[[hello, world],[nice]], [[to meet],[you]]]
# 3. Each element at the most surface layer will be built as a table.
#    3.1 The rwstrset shown above will be built as two tables.
#    3.2 The first table contains [[hello, world],[nice]]
#    3.3 The second table contains [[to meet],[you]]
# 4. Each raw string set for a table is a 2-dimension list, such as [[hello, world],[nice]].
#    Each element in this 2-dimension list is a row in this table.
def WriteExcel(fp, rwstrset):
    (fdir,fname) = GetFilePathName(fp)
    CheckMkDir(fdir)
    try:
        # open the excel file as workbook
        workbook = xlsxwriter.Workbook(fp)
        print 'Write excel file', fp
        for (tb, eachtable) in enumerate(rwstrset):
            # for each raw string set, create a new table to write it.
            print '\n', tb, 'table write'
            worksheet = workbook.add_worksheet()
            for (row, eachrw) in enumerate(eachtable):
                print '\n\n', row, "row write"
                for (col, eachcol) in enumerate(eachrw):
                    value = str(eachcol)
                    worksheet.write(row, col, value)
        workbook.close()
    except Exception as e:
        print 'Error in writing excel file!!', e


# ------------ LoadExcel read and return a table from a excel file ---------------
# 1. fp: the excel file path which you want to read.
# 2. tableindex: the table index which you want to read. Default value is the first table.
def LoadExcel(fp, tableindex=0):
    if not os.path.exists(fp):
        print 'File does not exists', fp
        return
    data = xlrd.open_workbook(fp)
    if tableindex <= len(data.sheets()):
        print 'Load', tableindex, 'st table at excel file', fp
        table = data.sheets()[tableindex]
        nrows = table.nrows
        ncols = table.ncols
        # return (nrows, ncols)
        return table
    else:
        print "Table Index Error! File", fp, "does not have the", tableindex, "st table."
        return

#######################################################################################
# ---------------------------------- Main function ---------------------------------- #
#######################################################################################
if __name__ == "__main__":
    # Pdfparser(r"C:\Users\Merry\Desktop\PDF\f0014.pdf", r"C:\Users\Merry\Desktop\TXT\f0014.txt", 'text')
    # ssss = r"Example ( 1 ), where \u27e8 \u27e9 marks the cue and { } the in-scope elements, illustrates the annotations, including how negation inside a noun phrase can scope over discontinuous parts of the sentence"
    # print ReplaceNonEnglishCharacter(ssss)
    # print RemoveUStrSpace2(ssss)
    getStopWord()
    # puncs = Loadpickle(os.path.join(pkdir, 'Puncs.pk'))
    # for p in puncs:
    #     print p
    # print type(p)
    # print(os.getcwd())

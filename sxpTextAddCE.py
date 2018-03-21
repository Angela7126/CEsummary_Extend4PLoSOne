# -*- coding: UTF-8 -*-

#######################################################################################
# --------------------------------- Function Introduce ------------------------------ #
#######################################################################################
# This functions set intends to:
# 1. Add pattern matched Cause-effect cases id to each sxpSent object: sysCEidlst, default as []
# 2. Add sysCEid to each CElink1
# 3. Add pattern CE links set -- sys_CE_list to each sxpText object
# 4. Add the dict object storing the mapping between sentence id and pattern matched CE id -- sysce_sent_id_dict
#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
from cmyPackage import *
from cmyToolkit import *

#######################################################################################
# --------------------------- Covert old object to new ------------------------------ #
#######################################################################################
# ---- convert the whole old pattern matched CElist into CELink1 object list ----
def GetSysCE(oldsysCElist):
    sysCElist = []
    sysce_sent_id_dict = {}
    for ceid, oldce in enumerate(oldsysCElist):
        ce = CELink1(ceid, oldce.pt)
        for temps in oldce.sInfo:
            ce.Staglst.append(temps.id)
            if sysce_sent_id_dict.has_key(temps.id):
                sysce_sent_id_dict[temps.id].append(ceid)
            else:
                sysce_sent_id_dict[temps.id] = [ceid]
        ce.cw_span = oldce.cause.span
        ce.ew_span = oldce.effect.span
        sysCElist.append(ce)
    return sysCElist, sysce_sent_id_dict


def GetSentIdDict(sxpSent1, sxpSent2):
    sentid_dict_1to2 = {}
    sentid_dict_2to1 = {}
    s1_len = len(sxpSent1)
    s2_len = len(sxpSent2)
    si = 0
    sj = 0
    while si < s1_len:
        while sj < s2_len and sxpSent1[si].sentence_text != sxpSent2[sj].sentence_text:
            sj += 1
        if sj < s2_len:
            sentid_dict_1to2[sxpSent1[si].id] = sxpSent2[sj].id
            sentid_dict_2to1[sxpSent2[sj].id] = sxpSent1[si].id
        si += 1
    return sentid_dict_1to2, sentid_dict_2to1

def GetSysCESentIdLst(sxptxt):
    StrSysceSentIdDict = ""
    for itm in sxptxt.sysce_sent_id_dict.items():
        StrSysceSentIdDict += str(itm) + '\n'
    return StrSysceSentIdDict
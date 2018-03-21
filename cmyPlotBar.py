# -*- coding: UTF-8 -*-

# -------------------------------------------------------------------------------
# Name:        cmyPlotBar.py  (rewrite from sxpPlotBar.py)
# Purpose:
# 1. PlotBarFromCoordSet: draws a bar graph according to a coordination data table
# 2. PlotScoreTables2BarFig: prints the score tables as figures
# -------------------------------------------------------------------------------

#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from cmyToolkit import *
from cmyRougeConfig import *

# -------------- Color Name to Value Dictionary ------------------
ClrNameValueDic = {'aliceblue':            '#F0F8FF',
                   'antiquewhite':         '#FAEBD7',
                   'aqua':                 '#00FFFF',
                   'aquamarine':           '#7FFFD4',
                   'azure':                '#F0FFFF',
                   'beige':                '#F5F5DC',
                   'bisque':               '#FFE4C4',
                   'black':                '#000000',
                   'blanchedalmond':       '#FFEBCD',
                   'blue':                 '#0000FF',
                   'blueviolet':           '#8A2BE2',
                   'brown':                '#A52A2A',
                   'burlywood':            '#DEB887',
                   'cadetblue':            '#5F9EA0',
                   'chartreuse':           '#7FFF00',
                   'chocolate':            '#D2691E',
                   'coral':                '#FF7F50',
                   'cornflowerblue':       '#6495ED',
                   'cornsilk':             '#FFF8DC',
                   'crimson':              '#DC143C',
                   'cyan':                 '#00FFFF',
                   'darkblue':             '#00008B',
                   'darkcyan':             '#008B8B',
                   'darkgoldenrod':        '#B8860B',
                   'darkgray':             '#A9A9A9',
                   'darkgreen':            '#006400',
                   'darkkhaki':            '#BDB76B',
                   'darkmagenta':          '#8B008B',
                   'darkolivegreen':       '#556B2F',
                   'darkorange':           '#FF8C00',
                   'darkorchid':           '#9932CC',
                   'darkred':              '#8B0000',
                   'darksalmon':           '#E9967A',
                   'darkseagreen':         '#8FBC8F',
                   'darkslateblue':        '#483D8B',
                   'darkslategray':        '#2F4F4F',
                   'darkturquoise':        '#00CED1',
                   'darkviolet':           '#9400D3',
                   'deeppink':             '#FF1493',
                   'deepskyblue':          '#00BFFF',
                   'dimgray':              '#696969',
                   'dodgerblue':           '#1E90FF',
                   'firebrick':            '#B22222',
                   'floralwhite':          '#FFFAF0',
                   'forestgreen':          '#228B22',
                   'fuchsia':              '#FF00FF',
                   'gainsboro':            '#DCDCDC',
                   'ghostwhite':           '#F8F8FF',
                   'gold':                 '#FFD700',
                   'goldenrod':            '#DAA520',
                   'gray':                 '#808080',
                   'green':                '#008000',
                   'greenyellow':          '#ADFF2F',
                   'honeydew':             '#F0FFF0',
                   'hotpink':              '#FF69B4',
                   'indianred':            '#CD5C5C',
                   'indigo':               '#4B0082',
                   'ivory':                '#FFFFF0',
                   'khaki':                '#F0E68C',
                   'lavender':             '#E6E6FA',
                   'lavenderblush':        '#FFF0F5',
                   'lawngreen':            '#7CFC00',
                   'lemonchiffon':         '#FFFACD',
                   'lightblue':            '#ADD8E6',
                   'lightcoral':           '#F08080',
                   'lightcyan':            '#E0FFFF',
                   'lightgoldenrodyellow': '#FAFAD2',
                   'lightgreen':           '#90EE90',
                   'lightgray':            '#D3D3D3',
                   'lightpink':            '#FFB6C1',
                   'lightsalmon':          '#FFA07A',
                   'lightseagreen':        '#20B2AA',
                   'lightskyblue':         '#87CEFA',
                   'lightslategray':       '#778899',
                   'lightsteelblue':       '#B0C4DE',
                   'lightyellow':          '#FFFFE0',
                   'lime':                 '#00FF00',
                   'limegreen':            '#32CD32',
                   'linen':                '#FAF0E6',
                   'magenta':              '#FF00FF',
                   'maroon':               '#800000',
                   'mediumaquamarine':     '#66CDAA',
                   'mediumblue':           '#0000CD',
                   'mediumorchid':         '#BA55D3',
                   'mediumpurple':         '#9370DB',
                   'mediumseagreen':       '#3CB371',
                   'mediumslateblue':      '#7B68EE',
                   'mediumspringgreen':    '#00FA9A',
                   'mediumturquoise':      '#48D1CC',
                   'mediumvioletred':      '#C71585',
                   'midnightblue':         '#191970',
                   'mintcream':            '#F5FFFA',
                   'mistyrose':            '#FFE4E1',
                   'moccasin':             '#FFE4B5',
                   'navajowhite':          '#FFDEAD',
                   'navy':                 '#000080',
                   'oldlace':              '#FDF5E6',
                   'olive':                '#808000',
                   'olivedrab':            '#6B8E23',
                   'orange':               '#FFA500',
                   'orangered':            '#FF4500',
                   'orchid':               '#DA70D6',
                   'palegoldenrod':        '#EEE8AA',
                   'palegreen':            '#98FB98',
                   'paleturquoise':        '#AFEEEE',
                   'palevioletred':        '#DB7093',
                   'papayawhip':           '#FFEFD5',
                   'peachpuff':            '#FFDAB9',
                   'peru':                 '#CD853F',
                   'pink':                 '#FFC0CB',
                   'plum':                 '#DDA0DD',
                   'powderblue':           '#B0E0E6',
                   'purple':               '#800080',
                   'red':                  '#FF0000',
                   'rosybrown':            '#BC8F8F',
                   'royalblue':            '#4169E1',
                   'saddlebrown':          '#8B4513',
                   'salmon':               '#FA8072',
                   'sandybrown':           '#FAA460',
                   'seagreen':             '#2E8B57',
                   'seashell':             '#FFF5EE',
                   'sienna':               '#A0522D',
                   'silver':               '#C0C0C0',
                   'skyblue':              '#87CEEB',
                   'slateblue':            '#6A5ACD',
                   'slategray':            '#708090',
                   'snow':                 '#FFFAFA',
                   'springgreen':          '#00FF7F',
                   'steelblue':            '#4682B4',
                   'tan':                  '#D2B48C',
                   'teal':                 '#008080',
                   'thistle':              '#D8BFD8',
                   'tomato':               '#FF6347',
                   'turquoise':            '#40E0D0',
                   'violet':               '#EE82EE',
                   'wheat':                '#F5DEB3',
                   'white':                '#FFFFFF',
                   'whitesmoke':           '#F5F5F5',
                   'yellow':               '#FFFF00',
                   'yellowgreen':          '#9ACD32'
                   }

# -------------- Get Color Name List ------------------
def GetDefaultColorList():
    clrnamelst = []
    for clrname, clrvalue in ClrNameValueDic.items():
        clrnamelst.append(clrname)
    return clrnamelst

# -------------- Color Name List ------------------
DefaultColorList = GetDefaultColorList()


#######################################################################################
# ------------------- Draw Bar Graphs according to data table ----------------------- #
#######################################################################################
# -------- PlotBarFromCoordSet function draws a bar graph according to a coordination data table  ------
# 1. titlename: is the title name of this figure, which will show at the top of the figure
# 2. coordname: the name list of the metric groups at X axis, such as [Precision, Recall, F-measure]
# 3. coordset: the coordination data table, which is a 2D list object.
#              Each element is an evaluated item and it's value on each X axis' coordinate points,
#              such as ['MyModel', 0.5, 0.5, 0.5].
# An example: coordset = [[legend1, [10,20,10]], [legend2, [11,20,120]],[legend3, [11,20,120]]], it contains 3
#             evaluation items: 'legend1','legend2','legend3', and each item has values on 3 metric groups.
# 4. highratio: the ratio that we want the displayed y value higher than the max y value in coordset.
# 5. symax: the max displaying value on Y axis set by users.

def PlotBarFromCoordSet(titlename, coordset, coordname, colorset=DefaultColorList, fname='output.jpg', highratio=0.1,
                        symax=1.0, widthratio=1.0, xshift=1.0, xfontdict={}, xtickrotation=0, xmax_ratio=1.5):
    N = len(coordname)  # How may evaluation metric groups have been considered, in this project N usually equals 3
    itemsnum = len(coordset)  # In this project, itemsnum is the number of models we want to evaluate
    # If the colorset is empty, we need to generate colors, coloridx stores the index of generated colors.
    coloridx = (np.arange(itemsnum)+1.0)/itemsnum  # if itemsnum=10, coloridx = array[0.1, 0.2, 0.3, ..., 1.0]


    ymajorLocator   = MultipleLocator(0.05)  # 将y轴主刻度标签设置为0.05的倍数
    ymajorFormatter = FormatStrFormatter('%1.2f')  # 设置y轴标签为文本格式,每个标签含一个个位数和两位小数
    yminorLocator   = MultipleLocator(0.01)  # 将y轴次刻度标签设置为0.01的倍数

    ind = np.arange(N)  # the begin locations for each metric group on X axis

    len_group = 1.0  # The width of each metric group on X axis.
    occupy_one_bar = len_group / itemsnum / 1.1  # occupy_one_bar is the width of a bar for an item on one metric group.
    width = occupy_one_bar*0.5   # the width of each bar, if itemsnum=10, width ~=0.045

    fig, ax = plt.subplots()
    legendname = []  # The item name list, in this project it is the model name list.
    rect_set = []  # The color objects list for bars in legend caption set, it is corresponding to legendname

    cmhot = plt.get_cmap("Spectral")
    nm = matplotlib.colors.Normalize(vmin=0.0, vmax=1.0, clip=False)
    m = matplotlib.cm.ScalarMappable(norm=nm, cmap=cmhot)
    my = 0  # Store the max value on Y axis
    xmaxpos = []  #
    xtickpos = []  # Get the position of tick marks for each metric group on X axis
    for i in range(N):
        xtickpos.append(ind[i] + 0.2)
    # generate bars for each evaluation items
    for i, eachd in enumerate(coordset):
        legendname.append(eachd[0])  # append the item's name into the item names list
        ydata = eachd[1]  # In this project, ydata is the ROUGE score data list for current model on each metric.
        my = max(my, max(ydata))  # if values in ydata is larger than max y value, update max y value.
        # set color for the current bar.
        if len(colorset) > 0:
            cl = colorset[i]
        else:
            rgb_value = m.to_rgba(coloridx[i])  # Get a color RGB value tuple, such as m.to_rgba(0.1)=(0.83, 0.24, 0.31, 1.0)
            cl = matplotlib.colors.rgb2hex(rgb_value)  # Get generated color by the RGB value tuple
        # draw bar for current item at each metric group with color cl
        rects2 = ax.bar(ind + width * i * xshift, ydata, width, color=cl)
        xmaxpos.append(max(ind + width * i * xshift))
        rect_set.append(rects2[0])

    # If symax has not be set, or it is not suitably set (i.e., symax < the max data in the coordset),
    # then automatically set the max y value according to the value in dataset.
    ymax = my + my*highratio
    if symax is not None and symax > ymax:
        ymax = symax

    # Set the title of figure.
    ax.set_title(titlename)
    # Set the labels and the max displaying value on Y axis.
    ax.set_ylabel('Scores')
    ax.set_ylim(0, ymax)
    # Set the tick marks, labels, and max displaying value on X axis.
    ax.set_xticks(xtickpos)
    tn = tuple(coordname)  # Get metrics' labels on X axis, (Precision, Recall, F-measure)
    ax.set_xticklabels(tn, xfontdict, rotation=xtickrotation)
    xmax = max(xmaxpos)
    ax.set_xlim(0, xmax*xmax_ratio)
    # Set legend captions
    recn = tuple(rect_set)
    ln = tuple(legendname)  # Get items' labels on legend caption
    ax.legend(recn, ln)
    # set the major and minor scales on Y axis.
    ax.yaxis.set_major_formatter(ymajorFormatter)
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_minor_locator(yminorLocator)
    # ax.yaxis.grid(True, linestyle=':', which='major')  # y坐标轴的网格使用主刻度
    ax.yaxis.grid(True, linestyle=':', which='minor')  # y坐标轴的网格使用次刻度

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                    '%d' % int(height),
                    ha='center', va='bottom')


# --------- PlotScoreTables2BarFig prints the score tables as figures -----------
# score_table_dict_fp: the path of pickle file which stores the score_table_dict
# score_table_dict: (we dump it as pickle file)
#       The ROUGE score value tables organized by score types.
#       Each key is a score type both contained in ROUGEScrMtx and in the ROUGE score dict at result_pk_fp
#       Each item's value is a list, which contains two parts:
#       1. The first is the header of the score table,
#       2. the second is the score dataset organized by model_name
# For building score_table_dict, see the outputs of function ProcessRougeScoreDic2Excel() in cmyParseRougeScore.py
def PlotScoreTables2BarFig(score_table_dict_fp, symax=1.0, highratio=0.2, ifshow=0):
    score_table_dict = LoadSxptext(score_table_dict_fp)
    if len(score_table_dict) == 0:
        return
    score_type_lst = score_table_dict.keys()
    # Get figures' directory and figure file names' prefix.
    resultdir, fname = GetFilePathName(score_table_dict_fp)
    figfphead = fname.split('.')[0]
    # Get configure information about this ROUGE score test as the figure titles' prefix.
    conf_lst = figfphead.split('_')
    fighead = conf_lst[0]
    for conf in conf_lst[1:]:
        if re.match(r'(\d\d)', conf):
            break
        fighead = fighead + '_' + conf
    # Draw a figure for each kind of score_type, such as 'ROUGE-1', 'ROUGE-2', ...
    for score_type in score_type_lst:
        fig_title = fighead + '--' + score_type
        fig_fp = os.path.join(resultdir, figfphead + '.' + score_type + '.png')
        metricslst = score_table_dict[score_type][0][1:]
        table = score_table_dict[score_type][1]
        PlotBarFromCoordSet(fig_title, table, metricslst, symax=symax, highratio=highratio)
        plt.savefig(fig_fp)
        # if user wants to show figures in the drawing processing, show it.
        if ifshow:
            plt.show()
    return


#######################################################################################
# ------------------------------- Some Test Functions ------------------------------- #
#######################################################################################
def TestBar():
    colorset = ['r', 'b', 'g']
    coorname = ['precision', 'recall', 'f-score']
    dataset = [['v1', [0.8, 0.9, 0.85]],
               ['v2', [0.4, 0.5, 0.65]],
               ['v3', [0.4, 0.5, 0.55]]]
    PlotBarFromCoordSet('test', dataset, coorname, colorset)
    plt.show()


def TestPlot():
    coorname = ['precision', 'recall', 'f-score']
    model_score = [['v1', [0.8, 0.9, 0.85]],
                   ['v2', [0.4, 0.5, 0.65]],
                   ['v3', [0.4, 0.5, 0.55]]]
    myfontdict = {'family': 'serif',
                  'color': 'darkred',
                  'weight': 'normal',
                  'size': 14}
    myxrotate = 0.0
    title = 'hello'
    PlotBarFromCoordSet(title,model_score,coorname,highratio=1.0,symax=1.0,widthratio=0.9,xshift=1.2,xfontdict=myfontdict,xtickrotation=myxrotate)
    # plt.savefig('bar.jpg')
    plt.show()


def Test():
    score_table_dict_fp = r"E:\Programs\Eclipse\CE_relation\CEsummary_PureCE\kg\PyrougeResults\kg_exc_withstop_maxword\kg_exc_withstop_maxword_01_02_03_04_05_06_07_08_09.ROUGE_score_table_dict.pk"
    PlotScoreTables2BarFig(score_table_dict_fp, ifshow=0)

#######################################################################################
# ------------------------------------ Main Functions ------------------------------- #
#######################################################################################
def main():
    # TestBar()
    # TestPlot()
    Test()


if __name__ == '__main__':
    main()

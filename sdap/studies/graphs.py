import os
import json
from datetime import datetime
from collections import OrderedDict
from operator import itemgetter   

import numpy as np
import pandas as pd
import math
import uuid
import shutil
import time

import pickle

def random_color(NbColors):
    pi = 3.14159265359
    pid2 = pi/2
    angle = 0
    step = pi/(NbColors)
    ListOfColors = []
    for i in range(0,NbColors):
        R = round((math.cos(angle)+1)/2 * 200)
        G = round((math.cos(angle-pid2)+1)/2 * 200)
        B = round((math.cos(angle-pi)+1)/2 * 200)
        A = 0.4
        angle = angle + step
        ListOfColors.append('rgba('+str(R)+','+str(G)+','+str(B)+','+str(A)+')')
    return ListOfColors

# Get requested values from file
def getValues(data, selectedvalues):
    dIndex = pickle.load(open(data.file.path + ".pickle", 'rb'))
    fList = data.file.file.open("rb")
    result = {}
    for val in selectedvalues :
        if str(val) in dIndex:
            iPosition = dIndex[str(val)]
            fList.seek(iPosition)
            result[str(val)] = fList.readline().decode().rstrip().split('\t')[1:]
        else:
            result[str(val)] = []
    return result

def getValuesExpression(data, Class, selection):
    dIndex = pickle.load(open(data.file.path + ".pickle", 'rb'))
    fList = data.file.file.open("rb")
    result = {}
    iPosition = dIndex[str(Class)]
    fList.seek(iPosition)
    all_class_groups = fList.readline().decode().rstrip().split('\t')[1:]
    pos = np.where(np.array(all_class_groups) == selection)[0]
    removed = ["X","Y","Sample"]
    d={}


    for index in dIndex :
        if "Class" not in index and index not in removed and index != '':
            iPosition = dIndex[str(index)]
            fList.seek(iPosition)
            all_exp_value = fList.readline().decode().rstrip().split('\t')[1:]
            x = np.array(all_exp_value)[pos]

            d[index] = np.mean(x.astype(np.float))
    
    # Iterate over the sorted sequence
    d = dict(OrderedDict(sorted(d.items(), key = itemgetter(1), reverse = True)))
    final = []
    for gene in d :
        final.append([gene,d[gene]])
    return final

# Get classes from pickle file
def getClasses(data):
    dIndex = pickle.load(open(data.file.path + ".pickle", 'rb'))
    result = []
    for index in dIndex :
        if "Class" in index :
            result.append(index)
    return result


def bw_nrd0(x):
    x = [float(i) for i in x]
    if len(x) < 2:
        raise(Exception("need at least 2 data points"))
    hi = np.std(x, ddof=1)
    q75, q25 = np.percentile(x, [75 ,25])
    iqr = q75 - q25
    lo = min(hi, iqr/1.34)
    if not ((lo == hi) or (lo == abs(x[0])) or (lo == 1)):
        lo = 1
    return 0.9 * lo *len(x)**-0.2

def arrayMax(arr) :
    len_ = len(arr) - 1
    max = -math.inf
    while(len_ !=0):
        if (arr[len_] > max):
            max = arr[len_]
        len_ = len_ - 1
    return max

def arrayMin(arr) :
    len_ = len(arr) - 1
    min = math.inf
    while(len_ !=0):
        if (arr[len_] < min):
            min = arr[len_]
        len_ = len_ - 1
    return min

def get_graph_data_full(file, selected_class=None):

    result = {'charts':[],'warning':[],'time':''}
    start_time = time.time()
    chart = {}
    # Should not happen. We select the class before
    chart['classes'] = getClasses(file)
    if not selected_class:
        selected_class = chart['classes'][0]
    groups = getValues(file, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    # Maybe we should have done this at the previous step
    samples = getValues(file,['Sample'])
    samples = np.array(samples['Sample'])

    x = np.array(getValues(file, ['X'])['X'])
    y = np.array(getValues(file, ['Y'])['Y'])
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['data']=[]
    chart['description'] = ""
    chart['name'] = "Classification by: %s" % (selected_class)
    chart['distribution_values'] = []
    chart['distribution_labels'] = []
    chart['colors'] = random_color(len(uniq_groups))

    chart['layout'] = { #'autosize': True,
                        'width':"",
                        'height':"",
                        'yaxis':{'autorange': True,'showgrid': True,'showticklabels': True,'zeroline': False,'showline': True, 'autotick': True},
                        'xaxis':{'showticklabels': True,'autorange': True,'showgrid': True,'zeroline': False,'showline': True,'autotick': True},
                        'autoexpand': True,
                        'showlegend': True,
                        'title':'Scatter plot visualization',
                        'hovermode':'closest'
                      }
    chart['msg'] = []
    color = 0
    for cond in uniq_groups :
        cond_color = chart['colors'][color]
        color = color + 1
        chart['distribution_labels'].append(cond)
        val_x= x[np.where(groups == str(cond))[0]]
        val_y= y[np.where(groups == cond)[0]]
        text = samples[np.where(groups == cond)[0]]
        chart['distribution_values'].append(len(val_x))
        data_chart = {}
        data_chart['x'] = []
        data_chart['x'].extend(val_x)
        data_chart['y'] = []
        data_chart['y'].extend(val_y)
        if len(data_chart['x']) == 0 and len(data_chart['y']) == 0 :
            chart['layout']['title'] = "No available data for %s" % (selected_class)
        data_chart['name'] = cond
        data_chart['text'] = []
        data_chart['text'].extend(text)
        data_chart['hoverinfo'] = "all"
        data_chart['type'] = 'scattergl'
        data_chart['mode']= 'markers'
        data_chart['marker'] = { 'color': cond_color }
        chart['data'].append(data_chart)



    result['chart'] = chart
    interval = time.time() - start_time
    result['time'] = interval
    return result




def get_graph_data_genes(file, genes, selected_class=None):

    for gene_t in genes :
        ensemblgene = gene_t.ensemble_id
        gene = gene_t

    result = {'warning':[],'time':''}
    start_time = time.time()
    # We should do this in the view, and select the class before
    classes =  getClasses(file)
    if not selected_class:
        selected_class = classes[0]
    groups = getValues(file, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    # Maybe we should have done this at the previous step
    samples = getValues(file,['Sample'])
    samples = np.array(samples['Sample'])
    x = np.array(getValues(file, ['X'])['X'])
    y = np.array(getValues(file, ['Y'])['Y'])

    genes = getValues(file, [gene.gene_id])
    ensembl_genes = getValues(file, [ensemblgene])

    chart = {}
    gene_name = gene.symbol
    chart['config'] = {'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['data'] = []
    chart['description'] = ""
    chart['name'] = "Expression of: %s " % (gene_name)
    chart['title'] = ""
    chart['layout'] = { #'autosize': True,
                        'width':"",
                        'height':"",
                        'yaxis':{'autorange': True,'showgrid': True,'showticklabels': True,'zeroline': False,'showline': True, 'autotick': True},
                        'xaxis':{'showticklabels': True,'autorange': True,'showgrid': True,'zeroline': False,'showline': True,'autotick': True},
                        'autoexpand': True,
                        'showlegend': True,
                        'title':'Expression of '+gene.symbol,
                        'hovermode':'closest'
                      }
    chart['gene'] = gene_name
    chart['msg'] = ""
    chart['distribution_values'] = []
    chart['distribution_labels'] = []
    chart['colors'] = random_color(len(uniq_groups))

    max_val = 0
    min_val = 0

    #EntrezGenes
    val_gene = np.array(genes[gene.gene_id])
    val_gene = val_gene.astype(np.float)
    if len(val_gene) != 0 :
        max_val =  np.max(val_gene.astype(np.float))
        min_val =  np.min(val_gene.astype(np.float))

    #Ensembl IDs
    val_gene_ensembl = np.array(ensembl_genes[ensemblgene])
    val_gene_ensembl = val_gene_ensembl.astype(np.float)
    if len(val_gene_ensembl) != 0 :
        max_val =  np.max(val_gene_ensembl.astype(np.float))
        min_val =  np.min(val_gene_ensembl.astype(np.float))

    chart['maxval'] = int(round(max_val))
    chart['minval'] = int(round(min_val))

    #Add condition information according selected the class
    for cond in uniq_groups :
        chart['distribution_labels'].append(cond)
        if len(val_gene) != 0 :
            val = val_gene[np.where(groups == cond)[0]]
            chart['distribution_values'].append(np.mean(val))
            val_x= x[np.where(groups == cond)[0]]
            val_y= y[np.where(groups == cond)[0]]
            text = samples[np.where(groups == cond)[0]]
            data_chart = {}
            data_chart['type'] = 'scattergl'
            data_chart['mode']= 'markers'
            data_chart['text'] = []
            data_chart['text'].extend(text)
            data_chart['x'] = []
            data_chart['x'].extend(val_x)
            data_chart['y'] = []
            data_chart['y'].extend(val_y)
            data_chart['name'] = cond
            data_chart['hoverinfo'] = "all"
            data_chart['marker']={'color':[],'cmax':max_val,'cmin':min_val}
            data_chart['marker']['color'].extend(val)
            chart['data'].append(data_chart)
        elif len(val_gene_ensembl) != 0 :
            val = val_gene_ensembl[np.where(groups == cond)[0]]
            chart['distribution_values'].append(np.mean(val))
            val_x= x[np.where(groups == cond)[0]]
            val_y= y[np.where(groups == cond)[0]]
            text = samples[np.where(groups == cond)[0]]
            data_chart = {}
            data_chart['type'] = 'scattergl'
            data_chart['mode']= 'markers'
            data_chart['text'] = []
            data_chart['text'].extend(text)
            data_chart['x'] = []
            data_chart['x'].extend(val_x)
            data_chart['y'] = []
            data_chart['y'].extend(val_y)
            data_chart['name'] = cond
            data_chart['hoverinfo'] = "all"
            data_chart['marker']={'color':[],'cmax':max_val,'cmin':min_val}
            data_chart['marker']['color'].extend(val)
            chart['data'].append(data_chart)
        else :
            chart['msg'] = "No data available for %s gene" % (gene_name)

    result['chart'] = chart
    interval = time.time() - start_time
    result['time'] = interval
    return result


def get_density_graph_data_full(file, selected_class=None):

    result = {'charts':[],'warning':[],'time':''}
    start_time = time.time()
    chart = {}
    # Should not happen. We select the class before
    chart['classes'] = getClasses(file)
    if not selected_class:
        selected_class = chart['classes'][0]
    groups = getValues(file, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    # Maybe we should have done this at the previous step
    samples = getValues(file,['Sample'])
    samples = np.array(samples['Sample'])

    x = np.array(getValues(file, ['X'])['X'])
    y = np.array(getValues(file, ['Y'])['Y'])
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['data']=[]
    chart['description'] = ""
    chart['name'] = "Classification by: %s" % (selected_class)
    chart['distribution_values'] = []
    chart['distribution_labels'] = []
    chart['colors'] = random_color(len(uniq_groups))

    chart['layout'] = { #'autosize': True,
                        'width':"",
                        'height':"",
                        'yaxis':{'autorange': True,'showgrid': True,'showticklabels': True,'zeroline': False,'showline': True, 'autotick': True},
                        'xaxis':{'showticklabels': True,'autorange': True,'showgrid': True,'zeroline': False,'showline': True,'autotick': True},
                        'autoexpand': True,
                        'showlegend': True,
                        'title':'Cell density',
                        'hovermode':'closest'
                      }
    chart['msg'] = []
    


    color = 0
    for cond in uniq_groups :
        cond_color = chart['colors'][color]
        color = color + 1
        chart['distribution_labels'].append(cond)
        val_x= x[np.where(groups == str(cond))[0]]
        val_y= y[np.where(groups == cond)[0]]
        text = samples[np.where(groups == cond)[0]]
        chart['distribution_values'].append(len(val_x))
        data_chart = {}
        data_chart['type'] = 'histogram2dcontour'
        data_chart['ncontours'] = 20
        data_chart['name'] = cond
        data_chart['x'] = []
        data_chart['x'].extend(val_x)
        data_chart['y'] = []
        data_chart['y'].extend(val_y)

        data_chart['legendgroup'] = cond
        data_chart['hoverinfo'] = 'none'
        

        data_chart['line'] = {'color':cond_color}
        data_chart['contours'] = {'coloring':'none'}
        data_chart['reversescale'] = False
        chart['data'].append(data_chart)



    result['chart'] = chart
    interval = time.time() - start_time
    result['time'] = interval
    return result

def get_density_graph_gene_data_full(file, genes, selected_class=None):


    result = {'charts':[],'warning':[],'time':''}
    start_time = time.time()
    chart = {}
    # Should not happen. We select the class before
    chart['classes'] = getClasses(file)
    if not selected_class:
        selected_class = chart['classes'][0]
    groups = getValues(file, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    # Maybe we should have done this at the previous step
    samples = getValues(file,['Sample'])
    samples = np.array(samples['Sample'])

    x = np.array(getValues(file, ['X'])['X'])
    y = np.array(getValues(file, ['Y'])['Y'])
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['data']=[]
    chart['description'] = ""
    chart['name'] = "Classification by: %s" % (selected_class)
    chart['distribution_values'] = []
    chart['distribution_labels'] = []
    chart['colors'] = random_color(len(uniq_groups))

   

    chart['layout'] = { #'autosize': True,
                        'width':"",
                        'height':"",
                        'yaxis':{'autorange': True,'showgrid': True,'showticklabels': True,'zeroline': False,'showline': True, 'autotick': True},
                        'xaxis':{'showticklabels': True,'autorange': True,'showgrid': True,'zeroline': False,'showline': True,'autotick': True},
                        'autoexpand': True,
                        'showlegend': True,
                        'title':'Expression of ',
                        'hovermode':'closest'
                      }
    chart['msg'] = []

    color = 0
    for cond in uniq_groups :
        cond_color = chart['colors'][color]
        color = color + 1
        val_x= x[np.where(groups == str(cond))[0]]
        val_y= y[np.where(groups == cond)[0]]
        text = samples[np.where(groups == cond)[0]]
        data_chart = {}
        data_chart['type'] = 'histogram2dcontour'
        data_chart['ncontours'] = 20
        data_chart['name'] = cond
        data_chart['x'] = []
        data_chart['x'].extend(val_x)
        data_chart['y'] = []
        data_chart['y'].extend(val_y)

        data_chart['legendgroup'] = cond
        data_chart['hoverinfo'] = 'none'
        

        data_chart['line'] = {'color':cond_color}
        data_chart['contours'] = {'coloring':'none'}
        data_chart['reversescale'] = False
        chart['data'].append(data_chart)



    result['chart'] = chart
    pos = 0
    ListOfColorsGenes = ['rgba(239,4,4,1)','rgba(239, 122, 4,1)','rgba(239, 239, 4,1)','rgba(122, 239, 4,1)','rgba(4, 239, 239,1)','rgba(4, 122, 239,1)','rgba(122, 4, 239,1)','rgba(239, 4, 239,1)','rgba(239, 4, 122,1)','rgba(4, 239, 4,1)']

    for gene in genes :
        chart['layout']["title"] = chart['layout']["title"]+ gene.symbol+", " 
        ensemblgene = gene.ensemble_id
        genes = getValues(file, [gene.gene_id])
        ensembl_genes = getValues(file, [ensemblgene])

        max_val = 0
        min_val = 0
        #EntrezGenes
        val_gene = np.array(genes[gene.gene_id])
        val_gene = val_gene.astype(np.float)
        if len(val_gene) != 0 :
            max_val =  np.max(val_gene.astype(np.float))
            min_val =  np.min(val_gene.astype(np.float))

        #Ensembl IDs
        val_gene_ensembl = np.array(ensembl_genes[ensemblgene])
        val_gene_ensembl = val_gene_ensembl.astype(np.float)
        if len(val_gene_ensembl) != 0 :
            max_val =  np.max(val_gene_ensembl.astype(np.float))
            min_val =  np.min(val_gene_ensembl.astype(np.float))
        # Gene value
        gene_color = ListOfColorsGenes[pos]
        pos = pos +1
        data_chart1 = {}
        data_chart1['type'] = 'histogram2dcontour'
        data_chart1['ncontours'] = 20
        data_chart1['x'] = []
        data_chart1['y'] = []
        data_chart1['z'] = []
        data_chart1['showscale'] = False
        data_chart1['histfunc'] = 'sum'
        data_chart1['colorscale'] = [[0,'rgba(255,255,255,0)'],[1,gene_color]]
        data_chart1['contours'] = {'showlines':False}
        data_chart1['histnorm'] = 'density'
        data_chart1['reversescale'] = False
        data_chart1['hoverinfo'] = 'none'

        for cond in uniq_groups :
            chart['distribution_labels'].append(cond)
            val =""
            if len(val_gene) != 0 :
                val = val_gene[np.where(groups == cond)[0]]
            elif len(val_gene_ensembl) != 0 :
                val = val_gene_ensembl[np.where(groups == cond)[0]]

            chart['distribution_values'].append(np.mean(val))
            val = val_gene[np.where(groups == cond)[0]]
            val_x= x[np.where(groups == cond)[0]]
            val_y= y[np.where(groups == cond)[0]]

            data_chart1['x'].extend(val_x)
            data_chart1['y'].extend(val_y)
            data_chart1['z'].extend(val)
        
        chart['data'].insert(0,data_chart1)

    
    interval = time.time() - start_time
    result['time'] = interval
    return result



def get_violin_graph_gene_data_full(file, genes, selected_class=None):


    result = {'charts':[],'warning':[],'time':''}
    start_time = time.time()
    chart={}
    # Should not happen. We select the class before
    chart['classes'] = getClasses(file)
    if not selected_class:
        selected_class = chart['classes'][0]
    groups = getValues(file, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    # Maybe we should have done this at the previous step
    samples = getValues(file,['Sample'])
    samples = np.array(samples['Sample'])

    x = np.array(getValues(file, ['X'])['X'])
    y = np.array(getValues(file, ['Y'])['Y'])
    chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
    chart['data']=[]
    chart['description'] = ""
    chart['name'] = "Classification by: %s" % (selected_class)
    chart['distribution_values'] = []
    chart['distribution_labels'] = []
    chart['colors'] = random_color(len(uniq_groups))

   

    chart['layout'] = { #'autosize': True,
                        'width':"",
                        'height':"",
                        'yaxis':{'autorange': True,'showgrid': True,'showticklabels': True,'zeroline': False,'showline': True, 'autotick': True},
                        'xaxis':{'showticklabels': True,'autorange': True,'showgrid': True,'zeroline': False,'showline': True,'autotick': True},
                        'autoexpand': True,
                        'showlegend': True,
                        'title':'Dynamic expression of',
                        'hovermode':'closest'
                      }
    chart['msg'] = []


    for gene in genes :
        chart = {}
        gene_name = gene.symbol
        ensemblgene = gene.ensemble_id
        genes = getValues(file, [gene.gene_id])
        ensembl_genes = getValues(file, [ensemblgene])

        max_val = 0
        min_val = 0
        #EntrezGenes
        val_gene = np.array(genes[gene.gene_id])
        val_gene = val_gene.astype(np.float)
        if len(val_gene) != 0 :
            max_val =  np.max(val_gene.astype(np.float))
            min_val =  np.min(val_gene.astype(np.float))

        #Ensembl IDs
        val_gene_ensembl = np.array(ensembl_genes[ensemblgene])
        val_gene_ensembl = val_gene_ensembl.astype(np.float)
        if len(val_gene_ensembl) != 0 :
            max_val =  np.max(val_gene_ensembl.astype(np.float))
            min_val =  np.min(val_gene_ensembl.astype(np.float))
        #ADD VIOLIN PLOT FOR GENE
        violin_chart = {}
        violin_chart['config']={'displaylogo':False,'modeBarButtonsToRemove':['toImage','zoom2d','pan2d','lasso2d','resetScale2d']}
        violin_chart['data']=[]
        violin_chart['description'] = ""
        violin_chart['name'] = "Violin plot of: %s " % (gene_name)
        violin_chart['title'] = "violin"
        violin_chart['selected'] = selected_class
        if len(uniq_groups) > 25 :
            violin_chart['layout'] = {
                'height': "",
                'showlegend': False,
                "title":'Dynamic expression of '+gene.symbol,
                'margin':{'l':300,},
                'yaxis':{'tickfont':10},
                'hovermode': 'closest'
            }
        else :
            violin_chart['layout'] = {
                'height': "",
                'showlegend': False,
                "title":'Dynamic expression of '+gene.symbol,
                'margin':{'l':300,},
                'yaxis':{'tickfont':10},
                'hovermode': 'closest'
            }
        violin_chart['gene'] = gene_name
        violin_chart['violmsg'] = ""

        for cond in uniq_groups :
            val =""
            if len(val_gene) != 0 :
                val = val_gene[np.where(groups == cond)[0]]
            elif len(val_gene_ensembl) != 0 :
                val = val_gene_ensembl[np.where(groups == cond)[0]]

            data_chart = {}
            data_chart['x'] = []

            q3 = np.percentile(val.astype(np.float), 75) #Q3

            data_chart['x'].extend(val)
            data_chart['name'] = cond
            data_chart['hoverinfo'] = "all"
            max_x = max(data_chart['x'])
            min_x = min(data_chart['x'])

            if len( data_chart['x']) > 5 :
                if arrayMax(data_chart['x']) != arrayMin(data_chart['x']):
                    bw = bw_nrd0(data_chart['x'])
                    data_chart['type'] = 'violin'
                    data_chart['opacity'] = 0.4
                    data_chart['points'] = True
                    data_chart['pointpos'] = 0
                    data_chart['jitter'] = .85
                    data_chart['bandwidth'] = bw
                    data_chart['scalemode'] = "width"
                    data_chart['spanmode'] = "hard"
                    data_chart['orientation'] = 'h'
                    data_chart['box'] = {'visible': True,'width': .1}
                    data_chart['boxpoints'] = True
                    data_chart['marker'] = {'size':2,'opacity': 0.8}
                else :
                    data_chart['type'] = 'box'
                    data_chart['orientation'] = "h"
                    data_chart['boxpoints'] = False
                    data_chart['y'] = [cond] * len(data_chart['x'])
                    data_chart['boxmean'] = True
            else :
                data_chart['type'] = 'box'
                data_chart['orientation'] = "h"
                data_chart['boxpoints'] = False
                data_chart['y'] = [cond] * len(data_chart['x'])
                data_chart['boxmean'] = True
                violin_chart['violmsg'] = ""
            violin_chart['data'].append(data_chart)

        result['charts'].append(violin_chart)
    return result

def getGenesValues(data, selected_class, gene_dict):

    #Return dictionnary gene:groups:mean(value)
    result = []
    all_group = []

    groups = getValues(data, [selected_class])
    groups = np.array(groups[selected_class])
    _, idx = np.unique(groups, return_index=True)
    uniq_groups = groups[np.sort(idx)[::-1]]
    all_group = uniq_groups.tolist()

    samples = getValues(data, ['Sample'])
    samples = np.array(samples['Sample'])

    for gene_name, gene_id in gene_dict.items():
        temp_list = [gene_name]
        #result[gene_name]={'geneID':gene_id,'conditions':{}}
        # Get all classes in the file and loop
        #result[gene_name]['conditions'][selected_class]={}

        genes = getValues(data,[gene_id])
        val_gene = np.array(genes[str(gene_id)])
        for cond in all_group:
            #result[gene_name]['conditions'][selected_class][cond] = ""
            if len(val_gene) != 0 :
                val = val_gene[np.where(groups == cond)[0]]
                group_mean_value = np.around(np.mean(val.astype(np.float)),3)
            else :
                group_mean_value = "NA"
            temp_list.append(group_mean_value)
            #result[gene_name]['conditions'][selected_class][cond] = group_mean_value
        result.append(temp_list)
    groups = []
    groups.append({'title': 'Gene'})
    for group in all_group:
        groups.append({'title': group})

    return {'results': result, 'groups': groups}

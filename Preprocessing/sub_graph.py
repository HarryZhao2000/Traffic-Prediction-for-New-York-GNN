import pandas as pd
import networkx as nx
import multiprocessing
from multiprocessing import Manager
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
import time

rawData = "movement-speeds-hourly-new-york-2020-1.csv"
edgeWeightName = "edge_weight.csv"
subedgeName = "subgraph_edge.csv"
rawDataClear = "movement-speeds-hourly-new-york-2020-1_clear.csv"

process_num = 4

def read_data(fileName):
    """
    Read files and return pandas as df
    :return: dataframe
    """
    df = pd.read_csv(fileName,sep=",",encoding="gb18030")
    # print(df.head())
    return df

def progress_print(present,total,stage):
    if present + 1 == total:
        percent = 100.00
        print("\r current %s process: %s [%d/%d]" %(str(stage),str(percent)+"%",present+1,total),end="\n")
    else:
        percent = round(1.0 * present / total * 100,3)
        print("\r current %s process: %s [%d/%d]" %(str(stage),str(percent) + "%", present+1,total),end='')

def setcallback(x):
    """
    function to process return value of function clear_all_data
    :param x: return value of process
    :return: movement-speeds-hourly-new-york-2020-1.csv_clear.csv file
    """
    lock=x[1]
    lock.acquire()
    x[0].to_csv("clean_data_all.csv",index=False, sep=',')
    lock.release()

def abstract_node_lst(edgeWeight,num):
    node_lst = []
    edgeWeight.sort_values("weight", inplace=True)
    count = -1
    total = edgeWeight.loc[edgeWeight["weight"]>=num].shape[0]-1
    # edgeWeight.loc[edgeWeight["weight"]>=num]
    # edgeWeight[:num]
    for i, row in edgeWeight.loc[edgeWeight["weight"]>=num].iterrows():
        progress_print(count, total, "node_abstract")
        count += 1
        for j in [row[1],row[2]]:
            if j not in node_lst:
                node_lst.append(j)
    return node_lst

def abstract_subgraph(edgeWeight,node_lst,subedgeName,write=False):
    G=nx.from_pandas_edgelist(edgeWeight, "start_node_id", 'end_node_id', ['weight', 'road_id'])
    H=G.subgraph(node_lst)
    node_lst = max(nx.connected_components(H))
    H=G.subgraph(node_lst)
    df = nx.to_pandas_edgelist(H)
    if write == True:
        df.to_csv(subedgeName,index=False, sep=',')
    return df

def main_create_subgraph():
    """
    input:  edge_weight.csv
    output: subgraph_edge.csv
    """
    edge_weight_thres= 707

    edgeWeight = read_data(edgeWeightName)
    node_lst = abstract_node_lst(edgeWeight,edge_weight_thres)
    abstract_subgraph(edgeWeight,node_lst,subedgeName,True)

def clean_data(ns_edge_data,ns_raw_data,range_tuple,name,lock):
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()

    edge_data = ns_edge_data.df
    raw_data = ns_raw_data.df
    edge_data_part = edge_data[range_tuple[0]:range_tuple[1]]

    df_res_part = pd.DataFrame(columns=("day","hour","road_id","speed_mph_mean","spped_mph_stddev"))
    for i,row in edge_data_part[["road_id"]].iterrows():
        df_tmp = pd.DataFrame(columns=("day","hour","road_id","speed_mph_mean","spped_mph_stddev"))
        # for j, rows in raw_data.loc[raw_data["road_id"] == row.values[0]].iterrows():
        for day_ in range(1,32):
            for hour_ in range(1,25):
                tmp = raw_data.loc[(raw_data["road_id"] == row.values[0]) & (raw_data["day"] == day_) & (raw_data["hour"] == hour_)]
                # tmp = raw_data.loc[(raw_data["road_id"] == 5003) & (raw_data["day"] == day_) & (raw_data["hour"] == hour_)]
                if len(tmp) == 1:
                    df_tmp = pd.concat([df_tmp,tmp],axis=0)
                elif len(tmp) == 0:
                    tmp = pd.DataFrame({"day":day_,"hour":hour_,"road_id":row.values[0],"speed_mph_mean":40,"spped_mph_stddev":0},index = [0])
                    df_tmp = pd.concat([df_tmp,tmp],axis=0)
                elif len(tmp) == 2:
                    tmp = pd.DataFrame({"day":day_,"hour":hour_,"road_id":row.values[0],"speed_mph_mean":(tmp.iloc[0,3]+tmp.iloc[1,3])/2,"spped_mph_stddev":((tmp.iloc[0,4]**2 + tmp.iloc[1,4]**2)/2)**0.5},index=[0])
                    df_tmp = pd.concat([df_tmp, tmp], axis=0)
                # print(df_tmp)
        df_res_part = pd.concat([df_res_part,df_tmp],axis=0)

    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    return df_res_part,lock

def main_clean_data():
    """
    input: subgraph_edge.csv and movement-speeds-hourly-new-york-2020-1_clear.csv
    output: clean_data_all.csv
    """

    mgr = Manager()
    lock = mgr.Lock()
    ns_edge_data = mgr.Namespace()
    ns_raw_data = mgr.Namespace()

    edge_data = read_data(subedgeName)
    raw_data = read_data(rawDataClear)

    ns_edge_data.df = edge_data
    ns_raw_data.df = raw_data

    index_lst = np.linspace(0, edge_data.shape[0], process_num + 1, endpoint=True).astype(int)

    p = multiprocessing.Pool(process_num)
    for i in range(1,process_num + 1):
        p.apply_async(clean_data, args=(ns_edge_data, ns_raw_data, (index_lst[i - 1], index_lst[i]), i,lock,),callback=setcallback)

    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')


if __name__ == "__main__":
    main_clean_data()

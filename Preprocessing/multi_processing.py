import multiprocessing
from multiprocessing import Manager
from multiprocessing import freeze_support
import os, time, random
import numpy as np
import pandas as pd
from collections import Counter
import csv

process_num = 4

## clear_all_data
fileName_all ="movement-speeds-hourly-new-york-2020-1.csv"
nodeName = "nodes.csv"
fileName_clear = "movement-speeds-hourly-new-york-2020-1_clear.csv"
edgeWeightName = "edge_weight.csv"


def read_data(fileName):
    """
    Read files and return pandas as df
    :return: dataframe
    """
    df = pd.read_csv(fileName,sep=",",encoding="gb18030")
    # print(df.head())
    return df


def setcallback(x):
    """
    function to process return value of function clear_all_data
    :param x: return value of process
    :return: movement-speeds-hourly-new-york-2020-1.csv_clear.csv file
    """
    lock=x[1]
    lock.acquire()
    with open("movement-speeds-hourly-new-york-2020-1_clear.csv",'a+',newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(x[0])
    lock.release()

#Multiprocess function
def clear_all_data(ns_nodes,ns_dataframe,range_tuple,name,lock):
    """
    #replace ns_nodes with node_id and go through all id to replace
    :param ns_nodes: shared space of nodes
    :param ns_dataframe: shared space of raw data
    :param range_tuple: numbers which represent pieces of dataframe we slice
    :param name:  process name
    :return: processed result of each row in dataframe
    """
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()

    # tmp_lst = mvh.speed(dataframe[range_tuple[0]:range_tuple[1]],node)
    res_lst = []
    dataframe = ns_dataframe.df
    node = ns_nodes.df
    dataframe_part = dataframe[range_tuple[0]:range_tuple[1]]
    for i, row in dataframe_part.iterrows():
        tmp = node.loc[(node["start_node_id"] == row[2]) & (node["end_node_id"] == row[3])]
        if tmp.values.size == 0:
            print("Wrong!!!!!!!!!!!!!")
        id = tmp["road_id"].values[0]
        res_lst.append([row[0],row[1],id,row[4],row[5]])
    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    return res_lst,lock

#Multiprocess function
def statistic_edge_weight(ns_dataframe, ns_lst, range_tuple, name,lock):
    """
    calculate weight of edge, which is the number of each edge has
    :param ns_dataframe: shared space of raw data
    :param ns_lst:  shared space of process result
    :param range_tuple: numbers which represent pieces of dataframe we slice
    :param name:  process name
    :return:  dictionary of statistical result of each process
    """
    print('Run task %s (%s)...' % (name, os.getpid()))
    start = time.time()
    tmp_dict = {}
    dataframe = ns_dataframe.df
    dataframe_part = dataframe[range_tuple[0]:range_tuple[1]]

    for i, row in dataframe_part.iterrows():
        if row[2] in list(tmp_dict.keys()):
            tmp_dict[row[2]] += 1
        else:
            tmp_dict.update({row[2]:1})

    lock.acquire()
    ns_lst.append(tmp_dict)
    lock.release()

    end = time.time()
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))
    return tmp_dict

def statistic_from_dict(ns_lst,weight_dict={}):
    """
    The results returned by all process functions refer to the statistics
    :param ns_lst: shared space of process result
    :param weight_dict: dictionary of multiprocess's result
    :return:  weight dictionary
    """
    weight_dict = Counter(weight_dict)
    for i in ns_lst:
        i = Counter(i)
        weight_dict = weight_dict + i
    return dict(weight_dict)


def main_clear_all_data():
    """
    Replace start_id and end_id with road_id
    input:  movement-speeds-hourly-new-york-2020-1.csv and nodes.csv
    :return: movement-speeds-hourly-new-york-2020-1_clear.csv
    """

    mgr = Manager()
    lock = mgr.Lock()
    ns_dataframe = mgr.Namespace()
    ns_nodes = mgr.Namespace()

    node = read_data(nodeName)
    ns_nodes.df = node
    dataframe = read_data(fileName_all)
    dataframe = dataframe[["day", "hour", "osm_start_node_id", "osm_end_node_id", "speed_mph_mean", "speed_mph_stddev"]]
    ns_dataframe.df = dataframe
    index_lst = np.linspace(0, dataframe.shape[0], process_num + 1, endpoint=True).astype(int)

    with open(fileName_clear, "w",newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["day","hour","road_id","speed_mph_mean","spped_mph_stddev"])


    p = multiprocessing.Pool(process_num)
    for i in range(1,process_num + 1):
        p.apply_async(clear_all_data, args=(ns_nodes, ns_dataframe, (index_lst[i - 1], index_lst[i]), i,lock,), callback=setcallback)

    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')

def main_statistic_edge_weight():
    """
     Main function to calculate the amount of data for each edge
     input:  movement-speeds-hourly-new-york-2020-1.csv_clear.csv file from last function
    :return:  edge_weight.csv
    """
    all_start_time = time.time()

    mgr = Manager()
    lock = mgr.Lock()
    ns_dataframe = mgr.Namespace()
    ns_lst = mgr.list()

    dataframe = read_data(fileName_clear)
    ns_dataframe.df = dataframe
    index_lst = np.linspace(0, dataframe.shape[0], process_num + 1, endpoint=True).astype(int)

    p = multiprocessing.Pool(process_num)
    for i in range(1,process_num + 1):
        p.apply_async(statistic_edge_weight, args=(ns_dataframe, ns_lst, (index_lst[i - 1], index_lst[i]), i,lock,), )
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    # print(ns_lst)

    print('All subprocesses done.')
    weight_dict = statistic_from_dict(ns_lst)
    key_lst = sorted(weight_dict)
    # print(weight_dict)

    nodes = pd.read_csv(nodeName)
    add_lst = []
    for i in key_lst:
        add_lst.append(weight_dict[i])

    nodes["weight"] = add_lst
    nodes.to_csv(edgeWeightName, index=False, sep=',')

    all_end_time = time.time()
    print("time cost: ", (all_end_time - all_start_time) / 60, "min")


def main():
    main_clear_all_data()

if __name__=='__main__':
    main()


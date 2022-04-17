import pandas as pd
import numpy as np
import csv
import time


# fileName = "2020_1_1.csv"
path_slice_raw = r"data\day_slice_raw"
path_slice = r"data\day_slice"
fileName = "movement-speeds-hourly-new-york-2020-1.csv"
nodeName = r"data\nodes.csv"
col = "osm_end_node_id"



def read_data(fileName):
    # file read as dataframe
    df = pd.read_csv(fileName,sep=",",encoding="gb18030")
    # print(df.head())
    return df

def basic_info(fileName,col):
    # data display, showing what is our data look like, from aspects of rows and columns
    dataframe = read_data(fileName)
    print(list(dataframe))
    # print dimension of data frame with function shape
    print(dataframe.shape)
    col_unique = dataframe[col].unique()
    # remove duplicated data
    print(len(col_unique))

def progress_print(present,total,stage):

    # function to print current progress
    if present + 1 == total:
        percent = 100.00
        print("\r current %s process: %s [%d/%d]" %(str(stage),str(percent)+"%",present+1,total),end="\n")
    else:
        percent = round(1.0 * present / total * 100,3)
        print("\r current %s process: %s [%d/%d]" %(str(stage),str(percent) + "%", present+1,total),end='')


def write_slice(dataframe,path_slice,day):
    # Slice data depending on days. Data of each day will be recorded as a new csv file.
    dataframe2 = dataframe[dataframe["day"] == day]
    fileName2 = path_slice+r"\2020_1_"+str(day)+".csv"
    # print(fileName2)
    dataframe2.to_csv(fileName2)

def nodes(dataframe):
    # Extract all nodes information as a new csv file. We do this step because when we conduct graph neural network, our
    # input is going to be a graph with many nodes. Here our nodes is many roads, each road equals to a road.
    lst = [["road_id","start_node_id","end_node_id"]]
    dataframe = dataframe[['osm_start_node_id','osm_end_node_id']]
    for i,row in dataframe.iterrows():
        tmp = [row[0],row[1]]
        if tmp != lst[-1]:
            lst.append(tmp)
    res = [list(i) for i in set(tuple(_) for _ in lst)]
    res.sort(key=lst.index)
    # print(res[0])
    # Add a unique number to each road
    for i in list(range(1,len(res))):
        res[i].insert(0,i)
    # print(res[1])

    return res

def speed(dataframe,node):
    # with csv file we have extracted before, here we generate new csv file. We still label file with day. For each file,
    # it will include the mean speed of road and mean standard value of road at that day.
    dataframe = dataframe[["day","hour","osm_start_node_id","osm_end_node_id","speed_mph_mean","speed_mph_stddev"]]
    speed_lst = [["day","hour","road_id","speed_mph_mean","spped_mph_stddev"]]
    for i, row in dataframe.iterrows():
        progress_print(i,dataframe.shape[0],"id replace")
        tmp = node.loc[(node["start_node_id"] == row[2]) & (node["end_node_id"] == row[3])]
        id = tmp["road_id"].values[0]
        speed_lst.append([row[0],row[1],id,row[4],row[5]])
    return speed_lst



def write_csv(lst,fileName2):
    # open and write files
    with open(fileName2, "w",newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(lst)

def create_node():
    """
    input: movement-speeds-hourly-new-york-2020-1.csv
    output: nodes.csv
    """
    dataframe = read_data(fileName)
    lst = nodes(dataframe)
    write_csv(lst, r"data/nodes.csv")

def write_csv_day_slice_raw():
    # Combining the preceding functions together to create raw day information
    dataframe = read_data(fileName)
    for day in range(1,32):
        write_slice(dataframe,path_slice_raw,day)
        print("Day "+str(day) + " is finished.")


def write_csv_day_slice():
    """
    input: clean_data_all.csv
    output: 2020_1_1.csv, 2020_1_2.csv, 2020_1_3.csv ...
    """
    node = read_data(nodeName)
    for day in range(1,32):
        print(" is processing day "+str(day)+"data")
        fileName_tmp_r = path_slice_raw + r"\2020_1_" + str(day) + ".csv"
        fileName_tmp_w = path_slice + r"\2020_1_" + str(day) + ".csv"
        dataframe = read_data(fileName_tmp_r)
        speed_lst = speed(dataframe,node)
        write_csv(speed_lst, fileName_tmp_w)
        print("day "+str(day)+"data processing completed。")


if __name__ == "__main__":
    time_start = time.time()

    write_csv_day_slice()

    time_end = time.time()
    print("time cost: ", (time_end - time_start) / 60, "min")
    # dataframe = read_data(fileName)
    # node = read_data(nodeName)
    # speed_lst = speed(dataframe,node)
    # write_csv(speed_lst,"speed.csv")

    # search = dataframe.loc[(dataframe["hour"] == 8) & (dataframe["osm_start_node_id"] == 2300353500) & (dataframe["osm_end_node_id"] == 5212739096)]
    # print(search)




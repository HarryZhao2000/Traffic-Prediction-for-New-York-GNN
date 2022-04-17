import numpy as np
import pandas as pd

days = 31
hours = 24

nodeFile = "subgraph_edge.csv"
rawFilePath = r".\data\day_slice_raw"

def read_csv(fileName):
    df = pd.read_csv(fileName)
    return df

def create_dataframe(day,nodes):
    columns = [str(day)+"-"+str(_) for _ in range(hours)]
    df_empty  = pd.DataFrame(columns=columns,index=nodes)
    return df_empty

def fill_na(day,df_empty,rawFilePath):
    fileName = rawFilePath+"\\"+"2020_1_"+str(day)+".csv"
    raw_data = read_csv(fileName)
    for i in range(hours):
        tmp = raw_data[raw_data["hour"] == i].copy()
        tmp.sort_values("road_id",inplace=True)
        df_empty.iloc[:,i] = tmp.speed_mph_mean.values
    return df_empty



if __name__ == "__main__":
    nodes = sorted(read_csv(nodeFile)["road_id"].tolist())
    df_full = pd.DataFrame()
    for i in range(days):
        df_empty = create_dataframe(i+1,nodes)
        df_full_part = fill_na(i+1,df_empty,rawFilePath)
        df_full = pd.concat([df_full, df_full_part], axis=1)
    # print(df_full.to_csv("model_data.csv"))
    """
    train = df_full.iloc[:,:576]
    test = df_full.iloc[:,577:]
    train.to_csv("train.csv")
    test.to_csv("test.csv")
    """
    original_data = df_full.to_numpy().T.tolist()
    for i in range(len(original_data)):
        for j in range(len(original_data[i])):
            original_data[i][j] = [original_data[i][j],0,0]
    original_data = np.array(original_data)

    np.savez("input_data\data.npz",data=original_data)

#  INFO442-Data Preprocessing-group2

This is how our project run in preprocessing step.

## Problem Description

In this project, we will use uber movement speed data from New York City to try to build a prediction model for the average speed and congestion of road segments using a graph neural network approach.

## What we did

- Extract nodes information
- Construct graph based on original nodes information
- Construct a temporary graph with the number of records as weights
- Select subgraphs according to conditions
- Filling in missing values
- Store the relevant data for each day as well as the node information into npz form and the list of edges of the finalized eligible subgraphs in csv form

## Main functions and ideas

Running sequence in main functions of code with its functionality. 

Firstly running create_node() in preprocessing.py.
**input**: movement-speeds-hourly-new-york-2020-1.csv
**output**: nodes.csv
**purpose**: Read raw data and extract nodes information  

Secondly running main_clear_all_data() in multi_processing.py
**input**: movement-speeds-hourly-new-york-2020-1.csv 和 nodes.csv
**output**: movement-speeds-hourly-new-york-2020-1_clear.csv
**purpose**: Here we replace information in nodes. We replace start_id and end_id with road_id so that it's convenient for us to calculate all data of each road.

Thirdly running main_statistic_edge_weight() of multi_processing.py
**input**: movement-speeds-hourly-new-york-2020-1_clear.csv 和 nodes.csv
**output**: edge_weight.csv
**purpose**: this is to calculate the amount of data for each edge. If there is a record for the road in that hour, we will plus one to that edge. 

Fourthly running main_create_subgraph() in sub_graph.py
**input**: edge_weight.csv
**output**: subgraph_edge.csv
**purpose**: Extract the sub images we need from the main image. We have used a ninety-five percent confidence interval for the edge weights based on statistical experience.
Here the edge weights represent the number of data records per road segment in the month of January. 
Since the recording is done in hours, one day should have 31*24=744 pieces data. 
We consider the real data within the ninety-five percent confidence interval to be significant, and our assumption of fill for the exact value does not affect the distribution of the data itself, so we choose the road segments with less than five percent record fill as our data set.
That is, road segments with a true data count of 706.8(we use 707 in the code) or more will be included in the sub graph we eventually use.

Fifth running main_clean__data() in sub_graph.py
**input**: subgraph_edge.csv and movement-speeds-hourly-new-york-2020-1_clear.csv
**output**: clean_data_all.csv
**purpose**: Here we merge the extracted edge weights csv file with the corresponding velocity csv file for each edge. Also we fill the speed records for all the missing edges. Since the speed limit in the New York State metropolitan area is 25miles which is about 40 km/h. Therefore we populated the time periods of the missing records assuming that their speed records are 40km/h. Accroding to data statistics of New York Taxi and Limousine Commision , we found that in January 2020, the point in time to which our data belong, an average of about 470,404 Uber trips were generated in New York City each day. With such a large uber usage rate, we think it is safe to assume that when an area is not covered by uber records, the area is not busy at that time. In other words, the roadway is likely not congested at that time of day. Also we assume that people drive to follow the speed limit but as fast as possible, so we fill in the missing speed data using the vehicle speed limit for New York City.

Sixth running write_csv_data_slice_raw() in proprocessing.py
**input**: clean_data_all.csv
**output**: 2020_1_1.csv, 2020_1_2.csv ...
**purpose**: Divide the overall data into 31 csv files according to day-based time dates.

Sixth running input_file.py
**input**: 2020_1_1.csv, 2020_1_2.csv ...
**output**: speed.npz
**purpose**: Combine 31 csv files and store speed averages in npz files.

## Data and outcomes

### Original data 

- Features
  - Year: Year(Local city time) Int
  - Month: Month 1-12(local city time) Int 
  - Day: Day 1-31(local city time) Int 
  - Hour: Hour 0-23(local city time) Int 
  - Utc_timestamp: Unix time for start of hour (UTC) Int 
  - Segment_id: [DEPRECATED] Replaced by OSM value "osm_way_id." Movement ID that maps to a specific road segment. Text 
  - start_junction_id: [DEPRECATED] Replaced by OSM value "osm_start_node_id." Movement ID that maps to start intersection of traversal. Text 
  - end_junction_id: [DEPRECATED] Replaced by OSM value "osm_end_node_id." Movement ID that maps to end intersection of traversal. Text Corresponding OpenStreetMap Way ID for this segment. Note that one OpenStreetMap Way may contain multiple Movement segments. Text 
  - Osm_way_id: Corresponding OpenStreetMap Way ID for this segment. Note that one OpenStreetMap Way may contain multiple Movement segments. Bigint 
  - osm_start_node_id: Corresponding OpenStreetMap Node ID for this junction. Bigint 
  - osm_end_node_id: Corresponding OpenStreetMap Node ID for this junction. Bigint 
  - speed_mph_mean: Average speed of Uber vehicles on this road segment in mph Float
  - speed_mph_stdev: Standard deviation of speeds on this road segment in mph. Float
- Granularity
  - Hourly
- Screenshot

​		![Original data](./ori_data.png)

### Outcomes data

- features
  - day: Day 1-31(local city time) Int
  - Hour: Hour 0-23(local city time) Int 
  - road_id: ID for this road Int
  - speed_mph_mean: Average speed of Uber vehicles on this road segment in mph Float
  - speed_mph_stddev: Standard deviation of speeds on this road segment in mph. Float
- Granularity
  - Hourly

- Screenshot

​		![Outcome data](./out_data.png)

## Reference

- TLC Trip Record Data - TLC. (n.d.). TLC Trip Record Data. Retrieved January 31, 2022, from https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page




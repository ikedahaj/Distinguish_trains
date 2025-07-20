# GPXデータをCSVに変換する
import pandas as pd
import glob
import sys
import gpxpy


import MakeRailGraph
from MakeRailGraph import StationInfo
import DistinguishTranins

filepath_Station="./usedata/N02-20_GML/N02-20_Station.geojson"
filepath_RailRoad="./usedata/N02-20_GML/N02-20_RailroadSection.geojson"
RailGraph=MakeRailGraph.MakeRailGraph(filepath_Station,filepath_RailRoad)
args=sys.argv
l_colname=["lat","lon","time","ele","onT"]
# if len(args)<=1:
#     print("GPXファイルパスを引数に入れてください")

file_path="./GPX位置判定/20250607163124.gpx"
# GPXファイルを読み込み
with open(file_path, 'r',encoding='utf-8') as f:
    gpx = gpxpy.parse(f.read())
points=[]
for point in gpx.tracks[0].segments[0].points:
    points.append([point.latitude, point.longitude,point.time,point.elevation])
print("main1")
Stations=[]
for StationName,StationInfo_ith in RailGraph.items():
    StationLine= StationInfo_ith[StationInfo.stationCoords]
    Stations.append([StationLine,StationName])
print("main2")

# dis=DistinguishTranins.DistinguishOnTrains(Stations,RailGraph)
dis2=DistinguishTranins.distinguishOnTrains_onlyRailRoad(filepath_RailRoad,30)
print("main3")
# newps=dis.DistinguishOnTrains(points)
newps=dis2.DistinguishOnTrains(points)
df=pd.DataFrame(newps,columns=l_colname)

df.to_csv("sample.csv")

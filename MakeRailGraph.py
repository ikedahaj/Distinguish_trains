import pandas as pd
import geopandas as gpd
import os
import urllib.request as rq
# import plotly.express as px
import matplotlib.pyplot as plt
import pyproj
import shapely
import math
from enum import StrEnum
import copy
import json

gstr_stationname="StationName"
class StationInfo(StrEnum):
    stationName="Name"
    stationCoords="xy" #df["geometry"][i].geoms[0].coors.xyを入れる
    RailRoadsToStation="RailRoad" #df["geometry"][i].geomsを入れる
    NextStationInfos="Next"

def IsSame_tuplefloat(a:tuple[float,float],b:tuple[float,float],err=1e-6)->bool:
    return (abs(a[0]-b[0])<err) and (abs(a[1]-b[1])<err)

def _binarySearch(StationList,point,access=lambda i,x:x[i][0])->int:
    left=0
    right=len(StationList)-1
    while left<right:
        mid=(left+right)//2
        if point[0]<access(mid,StationList)[0][0]:
            right=mid-1
        elif point[0]>access(mid,StationList)[0][0]:
            left=mid+1
        else:
            break
    ind=int((left+right)//2)
    while ind>0 and abs(access(ind,StationList)[0][0]-access(ind-1,StationList)[0][0])<(1e-4):
        ind-=1
    return ind

def _convert_StationGPDtoList(df):
    convertedList=[]
    geomdata:shapely.geometry.multilinestring.MultiLineString
    for name,geomdata in zip(df[gstr_stationname],df["geometry"]):
        xy=copy.deepcopy(geomdata.geoms[0].coords.xy)
        xy=_transverse_2dlist(xy)
        convertedList.append([xy,name])
        convertedList.append([xy[::-1],name])
    return sorted(convertedList)

def _convert_RailRoadGPDtoList(df):
    convertedList=[]
    for geomdata in df["geometry"]:
        xy=copy.deepcopy(geomdata.geoms[0].coords.xy)
        xy=_transverse_2dlist(xy)
        convertedList.append(xy)
        convertedList.append(xy[::-1])
    return sorted(convertedList)

def _transverse_2dlist(list2d):
    return list(zip(*list2d))

def _reverse_2dList_col(list2d):
    return [row[::-1] for row in list2d]

def _searchStationNameFromPoint(StationList,point:tuple[float,float]):
    fstIndex=_binarySearch(StationList,point)
    for i_Station in range(fstIndex,len(StationList)):
        if(IsSame_tuplefloat(point,StationList[i_Station][0][0])):
            return StationList[i_Station][1]

def _searchRailroadFromEndPoint(RailRoadList,StationList,point:tuple[float,float]):
    """指定された点が線路の両端にある線路を返す

    Args:
        df_railroad (List[tuple[float,float]]): geojsonのデータをgeopandasで読み込んだものの座標データを_transverse_2dlistに入れたもの
        point (tuple[float,float]): 指定する点

    Returns:
        List: _description_
    """
    L_matchRailRoad=[]
    #点から線路を探す;
    fstIndex=_binarySearch(RailRoadList,point,lambda i,x:x[i])
    #次はここから
    #fstindexから線路を探す
    for i_RailRoad in range(fstIndex,len(RailRoadList)):
        if IsSame_tuplefloat(point,RailRoadList[i_RailRoad][0]):
            l={}
            l[StationInfo.stationName]=_searchStationNameFromPoint(StationList,RailRoadList[i_RailRoad][-1])
            l[StationInfo.RailRoadsToStation]=RailRoadList[i_RailRoad][-1]
            L_matchRailRoad.append(l)
    return L_matchRailRoad

def _makeListDictRailGraph(RailRoadList,StationList):
    StationGraph={}
    per=0
    for i,stationData in enumerate(StationList):
        p=i/len(StationList)
        if p*100>per:
            print(p*100)
            per+=1
        xy=stationData[0]
        if stationData[1] in StationGraph.keys():
            StationGraph[stationData[1]][StationInfo.NextStationInfos].extend(_searchRailroadFromEndPoint(RailRoadList,StationList,xy[0]))
        else:
            StationGraph[stationData[1]]={StationInfo.stationCoords:xy,StationInfo.NextStationInfos:_searchRailroadFromEndPoint(RailRoadList,StationList,xy[0])}  
    return StationGraph


def MakeRailGraph(Filepath_Station:str,Filepath_Railroad:str,foldername="./usedata/",forceUpdate=False):
    filename_station=Filepath_Station.split('/')[-1].replace(".geojson","")
    filename_railroad=Filepath_Railroad.split('/')[-1].replace(".geojson","")
    filepath_graph=foldername+filename_station+filename_railroad+".json"
    if not os.path.isfile(filepath_graph) or forceUpdate:
        df_station=gpd.read_file(Filepath_Station)
        df_railroad=gpd.read_file(Filepath_Railroad)
        df_station[gstr_stationname]=df_station["N02_001"]+df_station["N02_002"]+df_station["N02_003"]+df_station["N02_004"]+df_station["N02_005"]
        StationList=_convert_StationGPDtoList(df_station)
        RailRoadList=_convert_RailRoadGPDtoList(df_railroad)
        RailGraph=_makeListDictRailGraph(RailRoadList,StationList)
        os.makedirs(foldername,exist_ok=True)
        with open(filepath_graph,"w") as f:
            json.dump(RailGraph,f)
    if not __name__=="__main__":
        with open(filepath_graph) as f:
            return json.load(f)
    


if __name__=="__main__":
    MakeRailGraph("./usedata/N02-20_GML/N02-20_Station.geojson","./usedata/N02-20_GML/N02-20_RailroadSection.geojson")

    

    

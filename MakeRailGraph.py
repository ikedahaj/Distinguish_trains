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

def _reverse_2dList_col(list2d):
    return [row[::-1] for row in list2d]

def _searchStationNameFromPoint(df_station,point:tuple[float,float]):
    for name,geomdata in zip(df_station[gstr_stationname],df_station["geometry"]):
        for line in geomdata.geoms:
            xy=line.coords.xy
            for x,y in zip(xy[0],xy[1]):
                if(IsSame_tuplefloat((x,y),point)):
                    return name

def _searchRailroadFromEndPoint(df_railroad,df_station,point:tuple[float,float]):
    """指定された点が線路の両端にある線路を返す

    Args:
        df_railroad (geojson): geojsonのデータをgeopandasで読み込んだもの
        point (tuple[float,float]): 指定する点
        stationName (str): 指定する元の駅名

    Returns:
        List: _description_
    """
    geomdata:shapely.geometry.multilinestring.MultiLineString
    L_matchRailRoad=[]
    for i_geoms, geomdata in enumerate(df_railroad["geometry"]):
        for line in geomdata.geoms:
            xy=line.coords.xy
            if IsSame_tuplefloat(point,(xy[0][0],xy[1][0])):
                l={}
                l[StationInfo.stationName]=_searchStationNameFromPoint(df_station,(xy[0][0],xy[1][0]))
                tmp=copy.deepcopy(xy)
                tmp=list(zip(*tmp))
                tmp=[list(x) for x in tmp]
                l[StationInfo.RailRoadsToStation]=tmp
                L_matchRailRoad.append(l)
                
            if IsSame_tuplefloat(point,(xy[0][-1],xy[1][-1])):
                l={}
                l[StationInfo.stationName]=_searchStationNameFromPoint(df_station,(xy[0][0],xy[1][0]))
                tmp=_reverse_2dList_col(xy)
                tmp=list(zip(*tmp))
                tmp=[list(x) for x in tmp]
                l[StationInfo.RailRoadsToStation]=tmp
                L_matchRailRoad.append(l)
                
    return L_matchRailRoad

def _makeListDictRailGraph(df_railroad,df_station):
    StationName_added=[]
    StationGraph={}
    geomdata:shapely.geometry.multilinestring.MultiLineString
    name:str
    for name,geomdata in zip(df_station[gstr_stationname],df_station["geometry"]):
        for line in geomdata.geoms:
            xy=copy.deepcopy(line.coords.xy)
            xy=list(zip(*xy))
            StationGraph[name]={StationInfo.stationCoords:xy,StationInfo.NextStationInfos:_searchRailroadFromEndPoint(df_railroad,df_station,(xy[0][0],xy[0][1]))}
            StationGraph[name][StationInfo.NextStationInfos].extend(_searchRailroadFromEndPoint(df_railroad,df_station,(xy[-1][0],xy[-1][0])))
        
    return StationGraph

def MakeRailGraph(Filepath_Station:str,Filepath_Railroad:str,foldername="./usedata",forceUpdate=False):
    filename_station=Filepath_Station.split('/')[-1].replace(".geojson","")
    filename_railroad=Filepath_Railroad.split('/')[-1].replace(".geojson","")
    filepath_graph=foldername+filename_station+filename_railroad+".json"
    if os.path.isfile(filepath_graph) and not forceUpdate:
        return
    df_station=gpd.read_file(Filepath_Station)
    df_railroad=gpd.read_file(Filepath_Railroad)
    print("canread")
    df_station[gstr_stationname]=df_station["N02_001"]+df_station["N02_002"]+df_station["N02_003"]+df_station["N02_004"]+df_station["N02_005"]
    # df_railroad[gstr_stationname]=df_railroad["N02_001"]+df_railroad["N02_002"]+df_railroad["N02_003"]+df_railroad["N02_004"]
    RailGraph=_makeListDictRailGraph(df_railroad,df_station)
    os.makedirs(foldername,exist_ok=True)
    with open(filepath_graph,"w") as f:
        json.dump(RailGraph,f)


if __name__=="__main__":
    MakeRailGraph("./usedata/N02-20_GML/N02-20_Station.geojson","./usedata/N02-20_GML/N02-20_RailroadSection.geojson")

    

    

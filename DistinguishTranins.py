import geopandas
import CalcDistOnEarth as calcDOE
import MakeRailGraph as MRG

class DistinguishOnTrains:
    def __init__(self,StationList,RailGraph,StationWidth=100,RailRoadWidth=20) -> None:
        self.CalcDistFromLines=calcDOE.CalcDistFromLines()
        self.calcDistFromPoint=calcDOE.CalcDistToPoint_ConvertPlane()
        self.StationList=sorted(StationList)
        self.RailGraph=RailGraph
        self.prevUpdatePoint=[0,0]
        self.NeighborList=[]
        self.StationWidth=StationWidth
        self.RailRoadWidth=RailRoadWidth
        self.CircleRadios=100 if StationWidth<=10 else StationWidth*10
        self.updateRadios=self.CircleRadios-StationWidth*2

    def _updateNeighborList(self,point):
        """中心からCircleRadios内にある駅のリストを作る

        Args:
            point (list[float]): 現在地
        """
        if self.calcDistFromPoint.p2p(point[1],point[0],self.prevUpdatePoint[1],self.prevUpdatePoint[0])<self.updateRadios:
            return
        self.prevUpdatePoint=point
        self.NeighborList=[]
        fInd=MRG.binarySearch(self.StationList,[point[0]-self.CircleRadios*calcDOE.const_lonPer1m,point[1]-self.CircleRadios*calcDOE.const_latPer1m],lambda i,x:min([x[i][0][0][0],x[i][0][-1][0]]))
        lInd=MRG.binarySearch(self.StationList,[point[0]+self.CircleRadios*calcDOE.const_lonPer1m,point[1]+self.CircleRadios*calcDOE.const_latPer1m],lambda i,x:min([x[i][0][0][0],x[i][0][-1][0]]))
        for ind in range(fInd,lInd+1) :
            # movedDist=self.CalcDistFromLines.calcDist_PointToLine(MRG.StationInfo[0],point)
            movedDist=self.calcDistFromPoint.p2p(self.StationList[ind][0][0][1],self.StationList[ind][0][0][0],point[1],point[0])
            if movedDist<self.CircleRadios:
                self.NeighborList.append(ind)
    def _SearchNearStation(self,point):
        self._updateNeighborList(point=point)
        if not self.NeighborList:
            return
        lind_nearStation=[]
        for ind in self.NeighborList:
            tmp=self.CalcDistFromLines.calcDist_PointToLine(self.StationList[ind][0],point)
            if tmp<=self.StationWidth:
                lind_nearStation.append(self.StationList[ind][1])
        if not lind_nearStation:
            return
        else:
            return lind_nearStation
    


    def DistinguishOnTrains(self,movedList):
        """_summary_

        Args:
            movedList (list): [lat,lon]の順の要素が入った配列
        """
        #行程の中から駅にいたところを探す
        # [movedListのインデックス,その地点の駅名のリスト]を要素とした配列.
        lstr_inStation=[]
        for i_movedList,coorInfo in enumerate(movedList):
            # 電車判定のデフォルト。乗っていない判定.
            coorInfo.append(False)
            nearStationNames=self._SearchNearStation([coorInfo[1],coorInfo[0]])
            if nearStationNames is not None:
                lstr_inStation.append([i_movedList,nearStationNames])
        # 駅の近くに1回までしか行ってないなら終了
        if len(lstr_inStation)<=1:
            return movedList
        # 全ての隣接する要素に対して、隣り合う駅かを判定
        # このネスト…深い!!!!!要改善.
        #[inStationのインデックス,見ている駅の名前,隣の駅を示すRailGraphのインデックス　]
        ind_neighborStations=[]
        for i_inStation in range(len(lstr_inStation)-1):
            for fstStationName in lstr_inStation[i_inStation][1]:
                for sndStationName in lstr_inStation[i_inStation+1][1]:
                    for i_NST,fst_NextStationInfo in enumerate(self.RailGraph[fstStationName][MRG.StationInfo.NextStationInfos]):
                        if sndStationName==fst_NextStationInfo[MRG.StationInfo.stationName]:
                            ind_neighborStations.append([i_inStation,fstStationName,i_NST])
        # 合致した駅間の行程を探索し、すべて線路上なら電車判定をする.    
        for ind_F_inStation,fStationName,ind_Nxt_RG in ind_neighborStations:
            cntOnTrain=0
            cntStep=0
            RailCoor=self.RailGraph[fStationName][MRG.StationInfo.NextStationInfos][ind_Nxt_RG][MRG.StationInfo.RailRoadsToStation]
            for i_movedList in range(lstr_inStation[ind_F_inStation][0],lstr_inStation[ind_F_inStation+1][0]+1):
                cntStep+=1
                railDist=self.CalcDistFromLines.calcDist_PointToLine(RailCoor,[movedList[i_movedList][1],movedList[i_movedList][0]])
                if railDist<self.RailRoadWidth:
                    cntOnTrain+=1
            if cntOnTrain/cntStep>0.8:
                for i_movedList in range(lstr_inStation[ind_F_inStation][0],lstr_inStation[ind_F_inStation+1][0]+1):
                    movedList[i_movedList][-1]=True


            # for i_roadToStation in range(lstr_inStation[ind_neighborMRG.StationInfo[0]][0],lstr_inStation[ind_neighborMRG.StationInfo[0]+1][0]+1):
            #     railDist=self.CalcDistFromLines.calcDist_PointToLine(self.RailGraph[ind_neighborMRG.StationInfo[1]][MRG.StationInfo.NextMRG.StationInfos][ind_neighborMRG.StationInfo[2]][MRG.StationInfo.RailRoadsToStation],movedList[i_roadToStation])
            #     if railDist>self.RailRoadWidth:
            #         onTrain=False
            # if onTrain:
            #     for i_roadToStation in range(lstr_inStation[ind_neighborMRG.StationInfo[0]][0],lstr_inStation[ind_neighborMRG.StationInfo[0]+1][0]+1):   
            #         movedList[i_roadToStation][-1]=True
        
        return movedList

class distinguishOnTrains_onlyRailRoad:
    def __init__(self,Filepath_RailRoad,RailRoadWidth) -> None:
        df_railroad=geopandas.read_file(Filepath_RailRoad)
        self.RailCoors=MRG.convert_RailRoadGPDtoList(df_railroad)
        self.CalcDistFromLines=calcDOE.CalcDistFromLines()
        self.calcDistFromPoint=calcDOE.CalcDistToPoint_ConvertPlane()
        self.prevUpdatePoint=[0,0]
        self.NeighborList=[]
        self.RailRoadWidth=RailRoadWidth
        self.CircleRadios=100 #if RailRoadWidth<=10 else RailRoadWidth*10
        self.updateRadios=self.CircleRadios-RailRoadWidth*2

    def DistinguishOnTrains(self,movedList):
        """_summary_

        Args:
            movedList (list): [lat,lon]の順の要素が入った配列
        """
        #行程の中から駅にいたところを探す
        # [movedListのインデックス,その地点の駅名のリスト]を要素とした配列.
        mannum=len(movedList)
        nowcnt=0
        persent=0
        for i_movedList,coorInfo in enumerate(movedList):
            # 電車判定のデフォルト。乗っていない判定.
            nowcnt+=1
            # if nowcnt/mannum>persent:
            print(nowcnt/mannum*100)
                # persent+=1
            self._updateNeighborList(coorInfo)
            if not self.NeighborList:
                movedList[i_movedList].append(False)
                continue
            minDist=self.calcMinDist_RL(coorInfo)
            if minDist<self.RailRoadWidth:
                movedList[i_movedList].append(True)
            else:
                movedList[i_movedList].append(False)

        return movedList
    def _updateNeighborList(self,point):
        """中心からCircleRadios内にある駅のリストを作る

        Args:
            point (list[float]): 現在地
        """
        if self.calcDistFromPoint.p2p(point[1],point[0],self.prevUpdatePoint[1],self.prevUpdatePoint[0])<self.updateRadios:
            return
        self.prevUpdatePoint=point
        self.NeighborList=[]
        fInd=MRG.binarySearch(self.RailCoors,[point[1]-self.CircleRadios*calcDOE.const_lonPer1m,point[0]-self.CircleRadios*calcDOE.const_latPer1m],lambda i,x:max([x[i][0][0],x[i][-1][0]]))
        lInd=MRG.binarySearch(self.RailCoors,[point[1]+self.CircleRadios*calcDOE.const_lonPer1m,point[0]+self.CircleRadios*calcDOE.const_latPer1m],lambda i,x:min([x[i][0][0],x[i][-1][0]]))
        for ind in range(fInd,lInd+1) :
            # movedDist=self.CalcDistFromLines.calcDist_PointToLine(MRG.StationInfo[0],point)
            movedDist=self.CalcDistFromLines.calcDist_PointToLine(self.RailCoors[ind],[point[1],point[0]])
            if movedDist<self.CircleRadios:
                self.NeighborList.append(ind)

    def calcMinDist_RL(self,point):
        # minDist=min(self.NeighborList,key=lambda x:self.CalcDistFromLines.calcDist_PointToLine(x,[point[1],point[0]]))
        minDist=self.CircleRadios*2
        for ind in self.NeighborList:
            dist=self.CalcDistFromLines.calcDist_PointToLine(self.RailCoors[ind],[point[1],point[0]])
            minDist=min([minDist,dist])
        return minDist
    


# listn=[[100.,5],[200,24],[150,50],[120,60]]

# def cd(li,p):
#     dx=li[0]-p[0]
#     dy=li[1]-p[1]
#     return dx*dx+dy*dy
# mm=min(listn,key=lambda x:cd(x,[150,50]))
# print(mm)

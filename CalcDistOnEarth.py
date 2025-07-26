import pyproj
import numpy as np
from enum import IntEnum
const_lonPer1m=0.000010966382364
const_latPer1m=0.000008983148616

#計算に使用するRPSGの値。
#一覧は https://lemulus.me/column/epsg-list-gis を確認.
class epsg_num(IntEnum):
    alon_120_126=6688
    alon_126_132=6689
    alon_132_138=6690
    alon_138_144=6691
    alon_144_150=6692
    JP_Nagasaki_Kagoshima=2443
    JP_FukuokaSagaKumamotoOitaMiyagi=2444
    JP_YamaguchiSimaneHiroshima=2445
    JP_KagawaEhimeTokushimaKoti=2446
    JP_HyogoTottoriFukuyama=2447
    JP_KyotoOsakaFukuiShigaMieNaraWakayama=2448
    JP_IshikawaToyamaGifuAichi=2449
    JP_NiigataNaganoYamanashiShizuoka=2450
    JP_TokyoFukushimaTochigiIbaragiSaitamaChibaGunnmaKanagawa=2451
    JP_AomoriAkitaYamagataIwateMiyagi=2452
    JP_Hokkaido_Hakodate=2453   #小樽市、函館市、伊達市、北斗市、豊浦町、壮瞥町、
                                # 洞爺湖町、北海道後志総合振興局の所管区域、
                                # 北海道渡島総合振興局の所管地域、
                                # 北海道檜山振興局の所管区域.
    JP_Hokkaido_Other=2454      # 2453、2455に含まれない北海道の地域.
    JP_Hokkaido_Kushiro=2455    #北見市、帯広市、釧路市、網走市、根室市、
                                # 美幌町、津別町、斜里町、清里町、小清水町、
                                # 訓子府町、置戸町、佐呂間町、大空町、
                                # 北海道十勝総合振興局の所管区域、
                                # 北海道釧路総合振興局の所管区域、
                                # 北海道根室振興局の所管区域
    JP_Tokyo_Ogasawara=2456
    JP_Okinawa_Naha=2457        # 	那覇市、石川市、具志川市、宜野湾市、浦添市、
                                # 名護市、糸満市、沖繩市、国頭村、大宜味村、
                                # 東村、今帰仁村、本部町、恩納村、宜野座村、
                                # 金武町、伊江村、与那城町、勝連町、読谷村、
                                # 嘉手納町、北谷町、北中城村、中城村、西原町、
                                # 豊見城村、東風平町、具志頭村、玉城村、知念村、
                                # 佐敷町、与那原町、大里村、南風原町、仲里村、
                                # 具志川村、渡嘉敷村、座間味村、粟国村、渡名喜村、
                                # 伊平屋村、伊是名村
    JP_Okinawa_Ishigaki=2458    # 平良市、石垣市、城辺町、下地町、上野村、
                                # 伊良部町、多良間村、竹富町、与那国町
    JP_Okinawa_OOhigashi=2459   # 南大東村、北大東村.
    JP_Tokyo_Okinotorishima=2460
    JP_Tokyo_Minamitorishima=2461

class CalcDistToLine_ConvertPlane:
    def __init__(self, from_epsg=4326, to_epsg=2448):
        """平面直角座標に変換することで計算する
            出典：https://ikatakos.com/pot/programming_algorithm/geometry/point_to_line#%E5%B9%B3%E9%9D%A2%E7%9B%B4%E8%A7%92%E5%BA%A7%E6%A8%99%E3%81%AB%E5%A4%89%E6%8F%9B

        Args:
            from_epsg (int, optional): _description_. Defaults to 4326.
            to_epsg (int, optional): _description_. Defaults to 2448.
        """
        self.from_epsg = pyproj.Proj('+init=EPSG:{}'.format(from_epsg))
        self.to_epsg = pyproj.Proj('+init=EPSG:{}'.format(to_epsg))
 
    def _latlng2xy(self, lat, lng):
        return pyproj.transform(self.from_epsg, self.to_epsg, lng, lat)
 
    def p2l(self, alat, alng, blat, blng, plat, plng):
        """点Pと線分ABの距離を算出する。

        Args:
            alat (float): 点Aの緯度
            alng (float): 点Aの経度
            blat (float): 点Bの緯度
            blng (float): 点Bの経度
            plat (float): 点Pの緯度
            plng (float): 点Pの経度

        Returns:
            float: 距離。点pから降ろした垂線が線分AB上にあれば垂線の長さが、そうでないなら点A,Bのうち近いほうとの距離が返る。
            単位はm?
        """
        a_ = complex(*self._latlng2xy(alat, alng))
        b_ = complex(*self._latlng2xy(blat, blng))
        p_ = complex(*self._latlng2xy(plat, plng))
 
        ab_, ap_ = b_ - a_, p_ - a_
        abp_prod = ab_.conjugate() * ap_  # 内積 + 外積j
        if abp_prod.real <= 0:
            return abs(ap_)
        ab = abs(ab_)
        ah = abp_prod.real / ab
        if ah >= ab:
            return abs(p_ - b_)
        return abs(abp_prod.imag) / ab
 
 
class CalcDistToLine_Convert3d:
    gi = pyproj.Geod(ellps='WGS84').inv
 
    def __init__(self, from_epsg=4326, to_epsg=5332):
        self.from_epsg = pyproj.Proj('+init=EPSG:{}'.format(from_epsg))
        self.to_epsg = pyproj.Proj('+init=EPSG:{}'.format(to_epsg))

 
    def _latlng2xyz(self, lat, lng):
        return pyproj.transform(self.from_epsg, self.to_epsg, lng, lat)
 
    def p2l(self, alat, alng, blat, blng, plat, plng):
        """点Pと線分ABの距離を算出する。

        Args:
            alat (float): 点Aの
            alng (float): 点Aの
            blat (float): 点Bの
            blng (float): 点Bの
            plat (float): 点Pの
            plng (float): 点Pの

        Returns:
            float: 距離。点pから降ろした垂線が線分AB上にあれば垂線の長さが、そうでないなら点A,Bのうち近いほうとの距離が返る
        """
        a_ = np.array(self._latlng2xyz(alat, alng))
        b_ = np.array(self._latlng2xyz(blat, blng))
        p_ = np.array(self._latlng2xyz(plat, plng))
        ab_, ap_ = b_ - a_, p_ - a_
        dot_prod = np.dot(ab_, ap_)
        if dot_prod <= 0:
            return self.gi(alng, alat, plng, plat)[2]
        ab = np.linalg.norm(ab_)
        ah = dot_prod / ab
        if ah >= ab:
            return self.gi(blng, blat, plng, plat)[2]
         
        # 内分点なら、垂線の足の座標はABの緯度経度を数値的に内分した値とする
        # ここを地球楕円体に沿うように改良するともう少し精度が高まるか？
        rh = ah / ab
        hlat = alat + rh * (blat - alat)
        hlng = alng + rh * (blng - alng)
        return self.gi(plng, plat, hlng, hlat)[2]
    
class CalcDistToPoint_ConvertPlane:
    def __init__(self, from_epsg=4326, to_epsg=2449):
        """平面直角座標に変換することで計算する
            出典：https://ikatakos.com/pot/programming_algorithm/geometry/point_to_line#%E5%B9%B3%E9%9D%A2%E7%9B%B4%E8%A7%92%E5%BA%A7%E6%A8%99%E3%81%AB%E5%A4%89%E6%8F%9B

        Args:
            from_epsg (int, optional): _description_. Defaults to 4326.
            to_epsg (int, optional): _description_. Defaults to 2448.
        """
        self.from_epsg = pyproj.Proj('+init=EPSG:{}'.format(from_epsg))
        self.to_epsg = pyproj.Proj('+init=EPSG:{}'.format(to_epsg))
        # self.transformer=pyproj.Transformer.from_crs(f"EPSG:{from_epsg}",f"EPSG{to_epsg}")

    def _latlng2xy(self, lng,lat):
        # return self.transformer.transform(lng,lat,)
        return pyproj.transform(self.from_epsg, self.to_epsg, lng, lat)

    def p2p(self, alat, alng,  plat, plng):
        """点Pと点Aの距離を算出する。

        Args:
            alat (float): 点Aの緯度
            alng (float): 点Aの経度
            plat (float): 点Pの緯度
            plng (float): 点Pの経度

        Returns:
            float: 距離。単位はm?
        """
        a_ = complex(*self._latlng2xy(alat, alng))
        p_ = complex(*self._latlng2xy(plat, plng))
        return abs(a_-p_)
    

class CalcDistFromLines:
    def __init__(self,to_epsg) -> None:
        self._CalcDist=CalcDistToLine_ConvertPlane2(to_epsg=to_epsg)

    def calcDist_PointToLine(self,Line:list[list[float]],Point:list[float])->float:
        minDist=self._CalcDist.p2l(Line[0][1],Line[0][0],Line[1][1],Line[1][0],Point[1],Point[0])
        for i in range(1,len(Line)-1):
            minDist=min([minDist,self._CalcDist.p2l(Line[i][1],Line[i][0],Line[i+1][1],Line[i+1][0],Point[1],Point[0])])
        return minDist
    

class CalcDistToLine_ConvertPlane2:
    def __init__(self, from_epsg=4326, to_epsg=6690):
        """平面直角座標に変換することで計算する
            出典：https://ikatakos.com/pot/programming_algorithm/geometry/point_to_line#%E5%B9%B3%E9%9D%A2%E7%9B%B4%E8%A7%92%E5%BA%A7%E6%A8%99%E3%81%AB%E5%A4%89%E6%8F%9B

        Args:
            from_epsg (int, optional): _description_. Defaults to 4326.
            to_epsg (int, optional): _description_. Defaults to 2448.
        """
        # self.from_epsg = pyproj.Proj('+init=EPSG:{}'.format(from_epsg))
        # self.to_epsg = pyproj.Proj('+init=EPSG:{}'.format(to_epsg))
        self.transformer=pyproj.Transformer.from_crs(f"EPSG:{from_epsg}",f"EPSG:{to_epsg}")
 
    def _latlng2xy(self, lat, lng):
        return self.transformer.transform(lat,lng)
        return pyproj.transform(self.from_epsg, self.to_epsg, lng, lat)
 
    def p2l(self, alat, alng, blat, blng, plat, plng):
        """点Pと線分ABの距離を算出する。

        Args:
            alat (float): 点Aの緯度
            alng (float): 点Aの経度
            blat (float): 点Bの緯度
            blng (float): 点Bの経度
            plat (float): 点Pの緯度
            plng (float): 点Pの経度

        Returns:
            float: 距離。点pから降ろした垂線が線分AB上にあれば垂線の長さが、そうでないなら点A,Bのうち近いほうとの距離が返る。
            単位はm
        """
        cnv_a = self._latlng2xy(alat, alng)
        cnv_b = self._latlng2xy(blat, blng)
        cnv_p = self._latlng2xy(plat, plng)
        ab_y=cnv_b[0]-cnv_a[0]
        ab_x=cnv_b[1]-cnv_a[1]
        ap_y=cnv_p[0]-cnv_a[0]
        ap_x=cnv_p[1]-cnv_a[1]
        apdotab=ab_y*ap_y+ab_x*ap_x
        if apdotab <= 0:
            return np.sqrt(ap_y*ap_y+ap_x*ap_x)
        ab2 = ab_y*ab_y+ab_x*ab_x
        if apdotab >= ab2:
            return np.sqrt((cnv_b[0]-cnv_p[0])*(cnv_b[0]-cnv_p[0])+(cnv_b[1]-cnv_p[1])*(cnv_b[1]-cnv_p[1]))
        ab=ab2**0.5
        k=abs(-ab_y*ap_x+ab_x*ap_y)
        return k/ab
    
if __name__=="__main__":
    import time,random
    calc1=CalcDistToLine_ConvertPlane()
    calc2=CalcDistToLine_ConvertPlane2()
    def random_ln():
        return 134+random.random()*10
    def rand_lat():
        return 23+random.random()
    # start = time.perf_counter() #計測開始
    # start2 = time.perf_counter() #計測開始
    # dist2=0
    # for i in range(1000):
    #     dist2+=calc2.p2l(rand_lat(),random_ln(),rand_lat(),random_ln(),rand_lat(),random_ln())
    # print(dist2)
    # end2 = time.perf_counter() #計測終了
    # print('{:.2f}'.format((end2-start2)/60)) # 87.97(秒→分に直し、小数点以下の桁数を指定して出力)
    # dist=0
    # for i in range(1000):
    #     dist+=calc1.p2l(rand_lat(),random_ln(),rand_lat(),random_ln(),rand_lat(),random_ln())
    # print(dist)
    # end = time.perf_counter() #計測終了
    # print('{:.2f}'.format((end-start)/60)) # 87.97(秒→分に直し、小数点以下の桁数を指定して出力)
    import math
    a=34.749123
    # a=35.1
    b=136.897292
    c=35.642438
    # c=34.9
    d=136.897292
    e=35.078341
    f=136.890308
    # for i in range(1000):
    dist=calc1.p2l(a,b,c,d,e,f)
    dist2=calc2.p2l(a,b,c,d,e,f)
    #     if not math.isclose(dist,dist2):
    #         print(a,d,b,e,c,f)
    #         print(dist-dist2)
    print(dist)
    print(dist2)


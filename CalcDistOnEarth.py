import pyproj
import numpy as np
 
class CalcDistFromLine_ConvertPlane:
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
 
 
class CalcDistFromLine_Convert3d:
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
    
class CalcDistFromPoint_ConvertPlane:
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
 
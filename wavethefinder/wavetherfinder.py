import ephem
import folium
import requests
import json
import re
from geopy.geocoders import Nominatim


class WTF:
    def __init__(self):
        """
            wave 와 weather 합성어로 wavetherfinder

            service 함수는 geopy 의 Nominatim 을 불러와
            원하는 특정도시의 위도,경도를 알수있고,
            sun_position 함수 는 ephem (천문학 계산을 수행하는 패키지)를 이용 하여
            특정도시의 경도와위도로 원하는 시간(과거포함)의 태양위치를 알수있다.

            또, city_map_check 함수는
            folium를 이용하여 특정도시(경도,위도)의 위치를 확인하여 index.html 으로 저장 하여 비주얼로 확인할수있따.

            weather_api_passing : 과거 전후 50년 이내 날씨를 웹 api로 json 데이터를 가져온다 . 주의 일일 최대 허용 횟수가 정해져있다. 짧다.
            wave_api_passing : 파도 데이터들을 웹 api 로 json 데이터 가져오온다.  range from 2022-07-29 to 2023-02-06


            특정 도시의 정보들을 확인할수 있는 데이터들은 현재 py 있는 파일에
            (index.html weather.json , wave.json) 저장된다.

          """

        self._name = ''
        self.location = None
        self._latitude = None
        self._longitude = None
        self._year = None
        self._month = None
        self._day = None

        # self._date = None
        # self.time = None

        self._hour = None
        self._min = None
        self._sec = None

        self.time = None

    def service(self):
        """
        도시 위치 lat,lon 얻는 거
        """
        geoservice = Nominatim(user_agent="MyGeoCoder")
        self.location = geoservice.geocode(self._name)

    def sun_position(self):
        """
        도시의 위치값 기준으로 태양의 위치 az,alt 데이터 get.
        az — Azimuth 0°–360° east of north
        alt — Altitude ±90° relative to the horizon’s great circle
        (unaffected by the rise/set setting horizon)
        Azimuth: 방위각,  Altitude: 고도

        특정도시 lat lon을 이용하여 그 도시 기준의 태양 위치데이터를 as,alt 반환한다.

        self.date = self.year + "/" + self.month + "/" + self.day
        self.time = self.hour + ":" + self.min + ":" + self.sec

        """

        date = self.year + "/" + self.month + "/" + self.day
        time = self.hour + ":" + self.min + ":" + self.sec

        observer = ephem.Observer()
        observer.pressure = 0
        observer.horizon = '-0:34'
        observer.lat = self.location.latitude
        observer.lon = self.location.longitude
        observer.date = date + ' ' + time

        sun = ephem.Sun()
        sun.compute(observer)

        return sun.az, sun.alt

    def city_map_check(self):
        """
        도시 이름 기준으로 html OSM MAP 파일 현재 py 있는 폴더 안에 저장하고
        Marker 찍고
        싸이클 마커 찍음.

        folium 을 사용하여 특정도시의 위치를 html  save 데이터 : index.html
        마커,반경 커스텀
        특정도시의 위치 확인 html OSM 기반의 지도 로 구체적으로 확인한다.
        """

        m = folium.Map(location=[self.location.latitude, self.location.longitude],
                       zoom_start=14,
                       width=750,
                       height=500)
        folium.Marker(
            location=[self.location.latitude, self.location.longitude],
            popup=self._name,
            icon=folium.Icon(color='red', icon='star')
        ).add_to(m)

        """
        radius 반경의 범위
        color 선의 색
        fill_color 채워지는 원안의 색
        """
        folium.CircleMarker([self.location.latitude, self.location.longitude],
                            radius=300,
                            color='blue',
                            fill_color='skygrean').add_to(m)

        m.save('index.html')

    def weather_api_passing(self):      # def 웹 API > 파이썬 API
        """
        city = name
        특정 도시 lat lon 의 날씨데이터 api json
        특정 날짜에 대한 1시간단위 00 - 24시간 데이타 json
        weather data :
        timezone(check),datetime ,tempmax, tempmin,windspeed, sunrise, sunset, icon,
        solarradiation,description,conditions
         get 날씨 데이터 icon:날씨정보, 기온, 바람방향,sunrise,sunset

        """
        lat = self.location.latitude
        lon = self.location.longitude

        weather_url = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/' \
                      f'{lat}%2C{lon}/{self.year + "-" + self.month + "-" + self.day}' \
                      f'?unitGroup=metric&key=8FDPK3NVXJQGA7FBL8C9C98T6&contentType=json'

        weather_data = requests.get(weather_url).json()
        return weather_data

    def weather_data_save(self):
        """
        wave api data json에 저장 : lat,lon,
        "time": "iso8601", "wave_height": "m", "wave_direction": "\u00b0", "wave_period": "s"
        """
        with open("weather_data.json", "w") as json_file:
            json.dump(self.weather_api_passing(), json_file)

    def wave_api_passing(self):  # def 웹 API > 파이썬 API

        """
        get 파도 데이터 파도 높이,,방향,피이어드
        파도 파싱할수 있는 날짜 범위
        range from 2022-07-29 to 2023-02-06
        wave_data.json 저장 주요 데이터:
        latitude longitude timezone
        ["hourly"] : ["time"],["wave_height"],["wave_direction"],["wave_period"]
        """

        lat = self.location.latitude
        lon = self.location.longitude
        wave_url = f'https://marine-api.open-meteo.com/v1/marine?' \
                   f'latitude={lat}&longitude={lon}&hourly=wave_height,wave_direction,wave_period&' \
                   f'start_date={self.year + "-" +self.month + "-" + self.day}&' \
                   f'end_date={self.year + "-" + self.month + "-" + self.day}'

        wave_data = requests.get(wave_url).json()
        return wave_data

    def wave_data_save(self):
        '''
        wave 파싱한 api josn을 저장

        wave api data json에 저장 데이터들 :
        lat,lon,"time": "iso8601", "wave_height": "m", "wave_direction": "\u00b0", "wave_period": "s"
        '''

        with open("wave_data.json", "w") as json_file:
            json.dump(self.wave_api_passing(), json_file)


    @property
    def name(self):
        """
        특정 도시의 이름 (type:str,ex : "부산 대한민국 " or "korea busan")
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def year(self):
        """
        특정 년도 (type:str,"YYYY" ex : "2023")
        """
        return self._year

    @year.setter
    def year(self, value):
        self._year = value

    @property
    def month(self):
        """
        특정 달 type:str,"MM" ex : "01" or "02" or "10")
        """
        return self._month

    @month.setter
    def month(self, value):
        self._month = value
    #day
    @property
    def day(self):
        """
       특정 일 type:str,"DD" ex : "01" or "08" or "30")
        """
        return self._day

    @day.setter
    def day(self, value):
        self._day = value

    @property
    def hour(self):
        """
       특정 시간 type:str,"HH" ex : "01" or "11" or "23")
        """
        return self._hour

    @hour.setter
    def hour(self, value):
        self._hour = value

    @property
    def min(self):
        """
       특정 분  type:str,"MM" ex : "01" or "23" or "60")
        """
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    # sec
    @property
    def sec(self):
        """
       특정 초 type:str,"" ex : "01" or "32" or "53")
        """
        return self._sec

    @sec.setter
    def sec(self, value):
        self._sec = value

    @property
    def latitude(self):
        return self._latitude
    @property
    def longitude(self):
        return self._longitude
    #
    # @property
    # def date(self):
    #     return self._date

    # @date.setter
    # def date(self, value):
    #     m = re.search(r"(\d{4}/(\d{2})/(\d{2}", value)
    #     if not m:
    #         raise ValueError("aaaa")
    #     self.year = m.gourp(1)
    #     self.month = m.group(2)
    #
    #     self._date = value

    # @property
    # def time(self):
    #     return self._time

#
# def main():
#
#     a = WTF()
#     """
#     name = 도시 이름
#     latitude = 위도, longitude = 경도
#     특정 날짜,시간,도시 의 위도,경도 데이터를 만.
#     """
#
#     # print("날짜와 시간 > ", a.date, a.time)
#     a.name = "태안 대한민국"
#     print(a.name)
#     a.service()
#     print(a.location.latitude, a.location.longitude)
#     print("도시명:", a.name, "도시 위치 > 위도 lat : ", a.location.latitude, " 경도 lon: ", a.location.longitude)
#
#     a.year = "2023"
#     a.month = "01"
#     a.day = "25"
#     a.hour = "18"
#     a.min = "18"
#     a.sec = "00"
#
#     # a.date = a.year + "/" + a.month + "/" + a.day
#     # a.time = a.hour + ":" + a.min + ":" + a.sec
#
#     a.sun_position()
#     print("특정도시의 태양 위치 :", a.sun_position())
#
#     """
#     folium 을 사용하여 특정도시의 위치를 html  save 데이터 : index.html
#     마커,반경 커스텀
#     특정도시의 위치 확인 html OSM 기반의 지도 로 구체적으로 확인한다.
#     """
#     a.city_map_check()
#
#     """
#     특정 도시위치 (lat lon) 의 날씨와 파도 두 데이터 룰 api josn 파일로 저장 weather_data.json, wave_data.json
#     (특정 날짜에 대한 1시간단위 00 - 24시간 데이타)
#     # get 날씨 데이터 icon:날씨정보, 기온, 바람방향, sunrise,sunset
#     # get 파도데이터 파도 높이,파도피이어드(sec)
#     """
#
#     # a.weather_api_passing()
#     # a.weather_data_save()
#
#     """
#     wave_data.json 저장 주요 데이터:
#     latitude longitude timezone
#     ["hourly"] : ["time"],["wave_height"],["wave_direction"],["wave_period"]
#     """
#     a.wave_api_passing()
#     a.wave_data_save()
#
#     # a.user_data = a.wave_passing()["hourly"]["wave_height"]
#     #파도안의 특정 데이터 출력
#     # print("time iso8601 :", a.wave_passing()["hourly"]["time"])
#     # print("wave_height m :", a.wave_passing()["hourly"]["wave_height"])
#     # print("wave_direction ° :", a.data["hourly"]["wave_direction"])
#     # print("wave_period s :", a.data["hourly"]["wave_period"])
#
# if __name__ == "__main__":
#     main()

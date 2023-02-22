# Netflix VFX Academy Pipline TD 1기

## Day_06 ~ Day_08
## 1차 프로젝트

## 개인 api name : WaveTherFinder

* What is WaveTerFinder : wave 와 weather 합성어로 wavetherfinder

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


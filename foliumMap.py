import io  #다양한 유형의 IO를 처리하기 위한 파이썬의 주 장치 제공
import folium  #지도 시각화 라이브러리
import json

from dataClass import *

class FoliumMap:
    def __init__(self):
        self.defaultCenter = [35.1570, 126.8540]
        self.defaultZoomLevel = 12
        self.center = [35.2214,126.8226]
        self.zoomLevel = 16
        self.m = folium.Map(
            location=self.defaultCenter, zoom_start=self.defaultZoomLevel
        )

    def setZoomLevel(self, zoomLevel : int):
        self.zoomLevel = zoomLevel

    def setCenter(self, location : list):
        self.center = location
        self.m.location = location

    def defaultClear(self):
        self.m = folium.Map(
            location=self.defaultCenter, zoom_start=self.defaultZoomLevel
        )

    def clear(self):
        self.m = folium.Map(
            location=self.center, zoom_start=self.zoomLevel
        )

    def addPropertyCenterMarker(self):
        folium.Marker(
            location=self.center,
            icon=folium.Icon(color='black'),
            popup=folium.LatLngPopup()
        ).add_to(self.m)
    
    def addPropertyMarkerList(self, propertyList : list[Property]):
        for property in propertyList:
            folium.Marker(
                location=[property.propertyLatitude, property.propertyLongitude],
                popup=folium.Popup(f'<div>유형</div>', min_width=200, max_width=200),
                icon=folium.Icon('black')
            ).add_to(self.m)

    def addPlaceMarkerList(self, placeList : list[Place]):
        for place in placeList:
            if place.placeCategory == '치킨 전문점':
                color = 'green'
            elif place.placeCategory == '음식':
                color = 'red'
            else:
                color = 'darkblue'

            folium.Marker(
                location=[place.placeLatitude, place.placeLongitude],
                popup=folium.Popup(f'<div>유형 : {place.placeCategory} <br/> 이름 : {place.placeName} <br/> 주소 : {place.placeAddress} </div>', min_width=230, max_width=200),
                icon=folium.Icon(color= color)
            ).add_to(self.m)
            
            # folium.Marker(
            #     icon=folium.Icon('red' if place.placeCategory == "음식점" else 'blue')
            # ).add_to(self.m)
    
    def saveData(self):
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        return data.getvalue().decode()

    
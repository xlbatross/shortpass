from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from dataClass import PlaceData
from db import DB

import time
import os
import zipfile
import shutil
import csv
import requests
import json

class ChromeCrawling:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.initChromeOptions()) # chromedriver 세
        self.actions = ActionChains(self.driver)
        self.db = DB()

    def initChromeOptions(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {"download.default_directory" : os.getcwd()}) # 다운로드 기본 위치를 이 프로그램이 실행되는 곳을 기준으로 한다
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
        chrome_options.add_argument("start-maximized")

        return chrome_options
    
    def get(self, url):
        self.driver.get(url)
    
    def close(self):
        self.driver.close()

    def find_elements(self, type, path):
        return self.driver.find_elements(type, path)

    def find_element(self, type, path):
        return self.driver.find_element(type, path)

    def crawlData(self):
        placeDataList : list[PlaceData] = []
        try:
            url = "https://www.data.go.kr/data/15083033/fileData.do#tab-layer-file"

            self.get(url) # chromedriver를 사용하여 url을 get 방식으로 접근한다.

            downloadButton = self.find_element(By.CSS_SELECTOR, '#tab-layer-file > div.data-detail-wrap > div.d-flex.float-r.just-pc > a')

            # 다운로드 시작
            fileList = [] 
            newFileList = [] 
            tryCount = 5 # 시도 횟수
            while len(fileList) == len(newFileList) and tryCount > 0:
                fileList = os.listdir(os.getcwd())
                self.actions.send_keys_to_element(downloadButton, Keys.ENTER).perform()
                time.sleep(1)
                newFileList = os.listdir(os.getcwd())
                tryCount -= 1

            if tryCount == -1:
                raise

            # 크롬용 파일 다운로드 체크
            fileName = ''
            for file in os.listdir(os.getcwd()):
                if ".crdownload" in file:
                    fileName = file
                    break

            while fileName in os.listdir(os.getcwd()):
                pass

            if fileName == '':
                raise

            fileName = fileName[:-11]

            # 파일 압축 해제
            extractFolder = 'extract'
            for file in os.listdir(os.getcwd()):
                if file == extractFolder:
                    shutil.rmtree(extractFolder)
            os.mkdir(extractFolder)

            with zipfile.ZipFile(fileName) as zip:
                zip.extractall(extractFolder)

            csvFileName = ''
            city = '광주'
            for file in os.listdir(os.getcwd() + "/" + extractFolder):
                if city in file:
                    csvFileName = file

            with open(f'{os.getcwd()}\\{extractFolder}\\{csvFileName}', 'r', encoding='utf-8') as f:
                rdr = csv.reader(f)

                for line in rdr:
                    if line[14] != "광산구" or line[6] == '커피점/카페' or line[6] == "제과제빵떡케익" and line[6] == '유흥주점':
                        continue
                    shopType = ''
                    shopWeight = 0
                    if line[4] == "음식":
                        shopType = line[4] if line[10] != "치킨 전문점" else line[10]
                        shopWeight = 0 if line[10] != "치킨 전문점" else -1
                    elif line[8] == "노래방" or line[8] == "인터넷PC방":
                        shopType = line[8]
                        shopWeight = 1
                    if shopType != '':
                        placeDataList.append(PlaceData(name=line[1], address=line[24], latitude=line[38], longitude=line[37], category=shopType, weight=shopWeight))


            for file in os.listdir(os.getcwd()):
                if file == extractFolder:
                    shutil.rmtree(extractFolder)
                elif file == fileName:
                    os.remove(fileName)

            return placeDataList
        except Exception as e:
            print(e)
            return []
    
    def crawlEMHSchools(self):
        placeDataList : list[PlaceData] = []
        try:
            schoolType = {"초등학교" : 2, "중학교" : 3, "고등학교" : 4}
            schoolWeight = {"초등학교" : 1, "중학교" : 1, "고등학교" : 2}
            schoolBaseUrl = "https://www.gen.go.kr/s_school/index.php?&mode=search1&s_div1=&s_div2="
            pageUrl = "&s_div3=&s_div4=&s_name=&page="

            for key in schoolType:
                typeValue = str(schoolType[key])
                count = 0

                while True:
                    count += 1
                    self.get(schoolBaseUrl + typeValue + pageUrl + str(count))
                    # time.sleep(2)
                    soup = BeautifulSoup(self.driver.page_source, "html.parser")

                    trElements = soup.select("#content > table > tbody > tr")

                    if len(trElements[0].select("td")) == 1:
                        break

                    for tr in trElements:
                        tdElements = tr.select("td")
                        schoolName = tdElements[0].select_one("a").text
                        if "휴교" in schoolName:
                            continue
                        schoolAddr = tdElements[3].text
                        latLng = None
                        try:
                            latLng = self.naverGeocoding(schoolAddr)
                        except:
                            try:
                                latLng = self.kakaoGeocoding(schoolAddr)
                            except:
                                pass
                        if latLng:
                            placeDataList.append(PlaceData(schoolName, schoolAddr, latLng[0], latLng[1], key, schoolWeight[key]))
            return placeDataList
        except Exception as e:
            print(e)
            return []

    def crawlCollege(self):
        placeDataList : list[PlaceData] = []
        try:
            collegePlaceDataList : list[PlaceData] = []
            collegeWeight = 5
            url = "https://www.data.go.kr/data/15055629/fileData.do"

            self.get(url)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            trElements = soup.select("#tab-layer-file > div.sample-data > div.mt40.just-pc > div.common-data-grid-area > div > table > tbody > tr")
            trElements.pop(0)
            for tr in trElements:
                tdElements = tr.select("td")
                collegePlaceDataList.append(PlaceData(name=tdElements[1].text, address=tdElements[2].text, latitude=tdElements[3].text, longitude=tdElements[4].text, category="대학교", weight=collegeWeight))
            
            return placeDataList
        except Exception as e:
            print(e)
            return []

    def crawlPark(self):
        placeDataList : list[PlaceData] = []
        try:
            baseAPIurl = "https://bigdata.gwangju.go.kr/gjAPI/getCityPark/getCityParklist.rd?apiSrvCd=0030&pageNo="
            rowNumUrl = "&numOfRow=10"
            count = 0

            while True:
                count += 1
                response = requests.get(baseAPIurl + str(count) + rowNumUrl, verify=False, timeout=5)
                time.sleep(2)
                parkList = response.json()['response']['body']['items']
                if len(parkList) == 0:
                    break
                for item in parkList:
                    if item['make_type'] != "조성":
                        continue
                    parkName = item['organ_nm'].strip().replace("\n", "") + item['type1'].strip().replace("\n", "") 
                    if not "공원" in parkName:
                        parkName += "공원"
                    parkAddr = item['st_add'].strip().replace("\n", "")
                    latLng = None
                    try:
                        latLng = self.naverGeocoding(parkAddr)
                    except:
                        try:
                            latLng = self.kakaoGeocoding(parkAddr)
                        except:
                            pass
                    if latLng:
                        placeDataList.append(PlaceData(parkName, parkAddr, latLng[0], latLng[1], "공원", 5))
            return placeDataList
        except Exception as e:
            print(e)
            return []

    def kakaoGeocoding(self, addr):
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
        headers = {"Authorization": "KakaoAK 073a393656181c6073880062d3507191"}
        result = requests.get(url, headers=headers).json()
        match_first = result['documents'][0]['address']
        return match_first['y'], match_first['x']

    def naverGeocoding(self, addr):
        url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query=' + addr
        headers = {"X-NCP-APIGW-API-KEY-ID" : "864b0vavw8", "X-NCP-APIGW-API-KEY" : "5oWwklMK0QayxxwimncBYks8x71KAE1ut6tDgYA6"}
        result = requests.get(url, headers=headers).json()
        match_first = result['addresses'][0]
        return match_first['y'], match_first['x']

    
        
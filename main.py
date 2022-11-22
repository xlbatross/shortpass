import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

from foliumMap import FoliumMap
from dataClass import *
from tcpClientClass import TCPClient

main_form = uic.loadUiType("./main.ui")[0]

#시그널 : 이벤트라고 한다 어떠한 행동을 이야기함
class ReceiveThread(QThread):  #큐스레드
    connectFail = pyqtSignal() 
    resProperty = pyqtSignal(ResProperty)
    resAnalysis = pyqtSignal(ResAnalysis)
    resStandard = pyqtSignal(ResStandard)
    resRights = pyqtSignal(ResRights)
    resCount = pyqtSignal(ResCount)
    ###############################################우선 클래스 각각 불러오기...
    resUpdate = pyqtSignal(ResUpdate)
    resUsepay = pyqtSignal(ResUsePay)
    resHistory = pyqtSignal(ResHistory)
    ###############################################
    resProTeamName = pyqtSignal(ResProTeamName)
    resChkPopulation = pyqtSignal(ResChkPopulation)
    resStdSales = pyqtSignal(ResStdSales)
    resStdFood = pyqtSignal(ResStdFood)
    noAnswer = pyqtSignal(ResNoAnswer)
    ###############################################

    def __init__(self, client : TCPClient):
        super().__init__()
        self.client = client
    
    def run(self):
        while True:
            data = self.client.receive()  #받을때
            if not data:
                self.connectFail.emit()  #데이터가 아니면 연결실패를 발생해라?
                break  #그리고 멈춰라
            if type(data) == ResProperty:  #데이터타입이 부동산 매물이면
                self.resProperty.emit(data) #해라
            elif type(data) == ResAnalysis:  #데이터타입이 분석이면 
                self.resAnalysis.emit(data)  #해라
            ############################################################
            elif type(data) == ResStandard:
                self.resStandard.emit(data)
            elif type(data) == ResRights:
                self.resRights.emit(data)
            elif type(data) == ResCount:
                self.resCount.emit(data)
            ############################################################
            elif type(data) == ResUpdate:
                self.resUpdate.emit(data)
            elif type(data) == ResUsePay:
                self.resUsepay.emit(data)
            elif type(data) == ResHistory:
                self.resHistory.emit(data)
            #############################################################
            elif type(data) == ResProTeamName:
                self.resProTeamName.emit(data)
            elif type(data) == ResChkPopulation:
                self.resChkPopulation.emit(data)
            elif type(data) == ResStdSales:
                self.resStdSales.emit(data)
            elif type(data) == ResStdFood:
                self.resStdFood.emit(data)
            elif type(data) == ResNoAnswer:
                self.noAnswer.emit(data)


class MainForm(QWidget, main_form):  #큐티메인화면
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.client = TCPClient()  #self.client는 TCPClient 클래스이다 import되어있음
        if not self.client.connect():  #self.client 연결이 아니면
            self.disconnect() #연결 실패
        else:  #성공했다면
            self.minMoney = 0
            self.maxMoney = 9999999
            self.propertyList = []  #이것은 빈 부동산매물리스트이다  
            self.selectedProperty = None  #부동산고르는건 아직 none값이다
            self.map = FoliumMap()  #맵은 foliumMap클래스?import?이다
            self.receiveThread = ReceiveThread(self.client)  #self.receive ReceiveThread
            self.receiveThread.start() #self.receiveThread시작해라
            self.chatDialog = chatDialog()
            self.renderMap() #renderMap 함수 실행
            self.setupConnect()  #setupConnect 함수 실행

    def setupConnect(self):  #초기함수.... 연결 같은거
        self.pushButton.clicked.connect(self.requestAnalysis)  #입지분석 버튼 클릭시 requestAnalysis 함수 연결
        self.btnReqProperty.clicked.connect(self.requestProperty) #매물검색 클릭시 requestProperty 함수 연결
        self.listWidgetPropertyList.itemClicked.connect(self.viewProperty) #리스트위젯 아이템 클릭시 viewProperty함수 연결
        self.receiveThread.connectFail.connect(self.disconnect)  #recieveThread의 connectFail은 disconnect함수로 연결
        self.receiveThread.resProperty.connect(self.viewPropertyList) #recieveThread의 resProperty는 viewPropertyList 함수로 연결
        self.receiveThread.resAnalysis.connect(self.viewLocationAnalysis) #recieveThread의 resAnalysis는 viewLocationAnalysis 함수로 연결
        self.comboBox.currentIndexChanged.connect(self.selectedComboItem)
        self.btnQnA.clicked.connect(self.chatWindow)

    def chatWindow(self):
        dialog = chatDialog()
        dialog.exec_()

    def renderMap(self):  #renderMap함수 : client연결 성공했다면 실행되는 함수 중 하나
        self.webEngineView.setHtml(self.map.saveData())   #전체 내용을 html 형식 문자열로 변경

    def disconnect(self):  #disconnect 함수
        QMessageBox.information(self, "서버 연결 실패", "서버와 연결하지 못하였습니다.")  #연결 실패하면 나타나는 메세지 박스
        self.deleteLater()  #Qobject 종료한 스레드 객체 안전하게 해제가능?

    def requestProperty(self):  #매물검색 클릭시 발생하는 함수 
        self.client.send(ReqProperty(minMoney=self.minMoney, maxMoney=self.maxMoney))  #self.client가 보낸다 ResPoperty(부동산매물)에 자본금에 맞는 매물 보여달라고

    def selectedComboItem(self, index):
        if index == 0:
            self.minMoney = 0
            self.maxMoney = 9999999
        elif index == 1:
            self.minMoney = 10000000
            self.maxMoney = 19999999
        elif index == 2:
            self.minMoney = 20000000
            self.maxMoney = 29999999
        elif index == 3:
            self.minMoney = 30000000
            self.maxMoney = 39999999
        elif index == 4:
            self.minMoney = 40000000
            self.maxMoney = 49999999
        elif index == 5:
            self.minMoney = 50000000
            self.maxMoney = 59999999
        elif index == 6:
            self.minMoney = 60000000
            self.maxMoney = 69999999
        elif index == 7:
            self.minMoney = 70000000
            self.maxMoney = 79999999
        elif index == 8:
            self.minMoney = 80000000
            self.maxMoney = 89999999
        elif index == 9:
            self.minMoney = 90000000
            self.maxMoney = 99999999
        elif index == 10:
            self.minMoney = 100000000
            self.maxMoney = 99999999999

    def requestAnalysis(self):  #입지분석 클릭시 발생하는 함수
        self.client.send(ReqAnalysis(self.selectedProperty.propertyLatitude, self.selectedProperty.propertyLongitude, self.selectedProperty.propertyNeighborhood))  #클라이언트 연결되면 위도,경도,동 resAnalysis에 보내라

    def viewPropertyList(self, data : ResProperty): #recieveThread의 resProperty 연결 함수  
        self.propertyList = data.propertyList  #빈 부동산 매물 리스트는 부동산데이터이다
        self.selectedProperty = None  #부동산 고르는건 왜 또 none이지?
        self.listWidgetPropertyList.clear()  #매물리스트 보여주는거 클리어
        if len(self.propertyList) == 0:  # 부동산리스트의 길이가 0이면
            self.labelNoProperty.show() #매물이없습니다라벨 보여주기
        else: #0이 아니라면
            self.labelNoProperty.hide()  #매물없다라벨 숨기고
            for property in data.propertyList:  #부동산매물이 무동산매물데이터 안에 있다면
                self.listWidgetPropertyList.addItem(QListWidgetItem(property.__str__())) #매물리스트에 추가 부동산 매물을
        self.pushButton.setEnabled(False)  #입지분석버튼은 클릭 못하게 해라
        self.labelNoPropertyInformation.show()  #매물정보라벨을 보여줘라
        self.labelNoLocationAnalysis.show()  #입지분석결과라벨을 보여줘라
        self.map.defaultClear()  #selfmap은 클리어해라 
        self.map.addPropertyMarkerList(self.propertyList) #selfmap은 마크리스트를 추가해라 부동산매물리스트를 통해
        self.renderMap()  #renderMap 함수로 가라

    def viewProperty(self, item):  #recieveThread의 resProperty때 발생하는 함수
        row = self.listWidgetPropertyList.currentRow()  #매물리스트 현재의 행
        self.selectedProperty = self.propertyList[row] #선택된부동산은 부동산매물의 현재 행
        self.renderPropertyMarker(self.selectedProperty.propertyLatitude, self.selectedProperty.propertyLongitude)  #위도, 경도를 통해 마커 표시 함수 연결 (함수 아래 있음)
        self.setPropertyInformation(self.selectedProperty)  #선택된 부동산의 정보 함수 연결 (아래 함수 있음)
        self.labelNoPropertyInformation.hide()  #매물정보라벨 숨겨
        self.labelNoLocationAnalysis.show() #부동산 입지 분석 라벨 숨겨
        self.pushButton.setEnabled(True)  #입지분석 버튼 보여라

    #내가 바꿔야 하는곳 
    def setPropertyInformation(self, property : Property):  #PropertyDB 연동하여 부동산매물정보 보여주기
        self.labelPropertyAddress.setText(str(property.propertyAddress)) #매물주소라벨이 주소 보여주기
        self.labelPropertyType.setText(str(property.propertyType)) #매물타입(월세,전제)에 타입 보여주기

        #권리금 완료
        entitlement = property.propertyEntitlement
        if 10000000> entitlement >= 10000:
            self.labelPropertyEntitlement.setText(str(entitlement // 10000) + "만원")
        if entitlement >= 100000000:
            self.labelPropertyEntitlement.setText(str(entitlement // 100000000) + "억")
        if entitlement == 0: 
            self.labelPropertyEntitlement.setText("알수없음")
        #보증금 만원 단위완료
        deposit = property.propertyDeposit
        if 100000000 > deposit >= 10000:
            self.labelPropertyDeposit.setText(str(deposit//10000) + "만원")
        elif deposit >= 100000000:  
            self.labelPropertyDeposit.setText(str(deposit//100000000) + "억")
        #월세 완료
        monthly = property.propertyMonthly
        if 100000000 > monthly >= 10000:
            self.labelPropertyMonthly.setText(str(monthly//10000) + "만원") #매물 월세 보여주기
        elif monthly >= 100000000: #월세 억단위 해야하나...
            self.labelPropertyMonthly.setText(str(monthly//100000000), + "억")
        self.labelPropertyArea.setText(str(property.propertyArea) + "평") #매물 평수 보여주기
    
    def renderPropertyMarker(self, latitude, longitude):  #매물 마커 함수
        self.map.clear()  #self.map 클리어
        self.map.setCenter(location=[latitude, longitude])  #self.map 위치(위도, 경도) 센터로하기?
        self.map.addPropertyCenterMarker() #self.map에 매물마크 표시
        self.renderMap() #renderMap함수 연결

    def viewLocationAnalysis(self, data : ResAnalysis):   #recieveThread의 resAnalysis시 발생 함수/ 분석 데이터
        self.labelNoLocationAnalysis.hide() #입지 분석 결과 라벨 숨기기
        self.renderPlaceMarkerList(data.placeList) #renderPlaceMarkerList 함수 연결 장소리스트데이터로
        self.setLocationAnalysis(data.placeCategoryList, data.expectedSales, data.population) #setLocationAnalysis 함수 연결 장소카테고리와 예상매출데이터로 (예상 매출 계산식은 서버클래스에 있다..)

    def setLocationAnalysis(self, placeCategoryList : list[PlaceCategory], expectedSales : int, population : int): #장소카테고리와 기대매출 표시 함수 
        self.listWidgetPositiveElements.clear() #증가요인 클리어
        self.listWidgetNegativeElements.clear() #감소요인 클리어
        for placeCategory in placeCategoryList: #장소카테고리가 장소카테고리 리스트 안에 있다
            if placeCategory.placeCategoryWeight > 0: #장소카테고리 위젯이 0보다 크면? 값이 들어있다면?
                self.listWidgetPositiveElements.addItem(QListWidgetItem(placeCategory.placeCategoryName + ": " + str(placeCategory.placeCategoryCount)))
                #증가요인에 추가해라 장소카테고리의 장소 이름과 장소 개수를? 왜 str?
            else:  #0 이하면
                self.listWidgetNegativeElements.addItem(QListWidgetItem(placeCategory.placeCategoryName + ": " + str(placeCategory.placeCategoryCount)))
                # 감소요인을 추가해라 장소 카테고리의 장소 이름과 장소 개수를? 근데 왜 str?

        if 100000000 > expectedSales >= 1000000:
            self.labelExpectedSales.setText("예상 월 매출 : " + str(expectedSales//10000) + "만원")  #예상 월 매출 계산
        if expectedSales >= 100000000:
            self.labelExpectedSales.setText("예상 월 매출 : " + str(expectedSales//100000000) + "억")  #예상 월 매출 계산

        self.labelPopulationCount.setText(f'({self.selectedProperty.propertyNeighborhood}) 거주인구수 : {population}명')
    def renderPlaceMarkerList(self, placeList : list[Place]):  #마커표시 리스트 함수 (장소 DB를 리스트로)
        self.map.clear() #self.map 클리어
        self.map.addPlaceMarkerList(placeList) #self.map에 마커 추가 장소 리스트를 통해
        self.map.addPropertyCenterMarker()   #self.map에 마커 표시
        self.renderMap() #renderMap 함수 연결 

###############################채팅창 보여주는 거######################################
class chatDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./chatUi.ui", self)

        self.chatClient = TCPClient()

        if not self.chatClient.connect():  #self.client 연결이 아니면
            self.disconnect() #연결 실패
        else:  #성공했다면
            self.dialogReceiveThread = ReceiveThread(self.chatClient)
            self.dialogReceiveThread.start()
            self.setupConnectDialog()

    def setupConnectDialog(self):
            self.dialogReceiveThread.connectFail.connect(self.disconnect)
            self.dialogReceiveThread.resProTeamName.connect(self.recvTeamNameMsg)
            self.dialogReceiveThread.resStandard.connect(self.recvChatStandard)
            self.dialogReceiveThread.resRights.connect(self.recvChatRights)
            self.dialogReceiveThread.resCount.connect(self.recvChatCount)
            self.dialogReceiveThread.resUpdate.connect(self.recvResUpate)
            self.dialogReceiveThread.resUsepay.connect(self.recvResUsePlay)
            self.dialogReceiveThread.resHistory.connect(self.recvResHistory)
            self.dialogReceiveThread.resChkPopulation.connect(self.recvPopulationMsg)
            self.dialogReceiveThread.resStdSales.connect(self.recvSalesMsg)
            self.dialogReceiveThread.resStdFood.connect(self.recvFoodMsg)
            self.dialogReceiveThread.noAnswer.connect(self.recvNoAnswerMsg)
            self.btn_sendMsg.clicked.connect(self.sendMessage)

    def disconnect(self):
        QMessageBox.information(self, "서버 연결 실패", "서버와 연결하지 못하였습니다.")
        self.deleteLater()

    def sendMessage(self):
        number = self.lineEdit.text()
        msg = f'''[사용자] : {number}
        '''
        if number == '1':
            Q = "이 프로그램 개발자의 이름은 무엇인가요?"
            self.chatClient.send(ReqProTeamName(number, Q))
        elif number == '2':
            Q = "상승요인과 하락요인 기준은 무엇인가요?"
            self.chatClient.send(ReqStandard(number, Q))
        elif number == '3' :
            Q = "부동산 권리금은 이 프로그램에서 알 수 없나요?"
            self.chatClient.send(ReqRights(number, Q))
        elif number == '4':
            Q = "주변 음식점 개수가 나오는데 정확한 정보인가요?"
            self.chatClient.send(ReqCount(number, Q))
        elif number == '5':
            Q = "지도나 요인들의 업데이트는 얼마나 자주 되나요?"
            self.chatClient.send(ReqUpdate(number, Q))
        elif number == '6':
            Q = "이용 요금은 없나요?"
            self.chatClient.send(ReqUsePay(number, Q))
        elif number == '7':
            Q = "검색 내역 또는 이용 내역은 뜨지않나요?"
            self.chatClient.send(ReqHistory(number, Q))
        elif number == '8':
            Q = "거주 인구수는 지도에 표시된 부분에 거주하는 사람들의 수인가요?"
            self.chatClient.send(ReqChkPopulation(number, Q))
        elif number == '9':
            Q = "예상 월 매출은 어떤 기준으로 산정된건가요?"
            self.chatClient.send(ReqStdSales(number, Q))
        elif number == '0':
            Q = "여기에 표시되는 음식점은 어떤 기준인가요?"
            self.chatClient.send(ReqStdFood(number, Q))
        else:
            Q = "Etc"
            self.chatClient.send(ReqNoAnswer(Q))
        # else:
        #     QMessageBox.warning(self,"경고",  "답변은 선택지 안에서 골라주세요!")
        self.lineEdit.clear()
        self.textBrowser.append(msg)

    def recvTeamNameMsg(self, data : ResProTeamName):
        self.textBrowser.append(data.teamMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())

    def recvChatStandard(self, data : ResStandard):
        self.textBrowser.append(data.stdMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvChatRights(self, data : ResRights):
        self.textBrowser.append(data.rightMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvChatCount(self, data : ResCount):
        self.textBrowser.append(data.countMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvResUpate(self, data : ResUpdate):
        self.textBrowser.append(data.updateMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvResUsePlay(self, data : ResUsePay):
        self.textBrowser.append(data.payMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvResHistory(self, data : ResHistory):
        self.textBrowser.append(data.historyMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvPopulationMsg(self, data : ResChkPopulation):
        self.textBrowser.append(data.chkpopMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvSalesMsg(self, data : ResStdSales):
        self.textBrowser.append(data.saleMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvFoodMsg(self, data : ResStdFood):
        self.textBrowser.append(data.foodMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())


    def recvNoAnswerMsg(self, data : ResNoAnswer):
        self.textBrowser.append(data.etcMsg)
        QTextBrowser.verticalScrollBar(self.textBrowser).setValue(QTextBrowser.verticalScrollBar(self.textBrowser).maximum())

########################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainForm = MainForm()
    mainForm.show()
    sys.exit(app.exec_())
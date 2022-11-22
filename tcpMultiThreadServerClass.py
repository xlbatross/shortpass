import socket
import pickle
from db import DB
from dataClass import *

class TCPMultiThreadServer:
    def __init__(self, port : int = 2500, listener : int = 1):
        self.db = DB() # DB와의 연동을 처리하는 클래스 객체
        self.connected = False # 서버가 클라이언트와 연결되었는지를 판단하는 변수
        self.client : dict[tuple, list[socket.socket, str]] = {} # 현재 서버에 연결된 클라이언트 정보를 담는 변수
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 서버 소켓 생성
        self.sock.bind(('', port)) # 서버 소켓에 어드레스(IP가 빈칸일 경우 자기 자신(127.0.0.1)로 인식한다. + 포트번호)를 지정한다. 
        self.sock.listen(listener) # 서버 소켓을 연결 요청 대기 상태로 한다.

    # 접속 종료로 인한 클라이언트 정보 정리
    def disconnect(self, cAddr : tuple):
        if cAddr in self.client: # 접속을 끊은 클라이언트의 정보가 client 인스턴스 변수에 존재한다면.
            del self.client[cAddr] # 클라이언트 정보 삭제
        if len(self.client) == 0: # 만약 서버에 연결된 클라이언트가 없다면
            self.connected = False # 서버와 연결된 클라이언트가 없는 상태임을 저장한다.
        print(self.client)
    
    # 클라이언트 연결
    def accept(self):
        cSock, cAddr = self.sock.accept() # 클라이언트와 연결이 된다면 클라이언트와 연결된 소켓과 클라이언트의 어드레스(IP와 포트번호)를 반환한다.
        self.connected = True # 서버가 클라이언트와 연결된 상태임을 저장한다.
        self.client[cAddr] = [cSock, ""] # client 인스턴스 변수에 클라이언트의 어드레스를 키값으로 하여 소켓과 해당 클라이언트에 로그인한 아이디를 저장한다.
        # 지금은 서버로 접속만 했기 때문에 아이디 부분은 빈 부분이다.
        return cSock, cAddr # 클라이언트와 연결된 소켓과 클리이언트의 어드레스 반환

    
    # 모든 클라이언트에 데이터 송신
    def sendAllClient(self, data):
        if self.connected: # 현재 서버가 클라이언트에 연결된 상태라면
            for client in self.client.values(): # 연결된 모든 클라이언트에
                client[0].sendall(pickle.dumps(data)) # 바이트 바이너리로 변환한 데이터를 송신한다
            return True
        else:
            return False
    
    # 단일 클라이언트에 데이터 송신
    def sendClient(self, cSock : socket.socket, data):
        if self.connected: # 현재 서버가 클라이언트에 연결된 상태라면
            cSock.sendall(pickle.dumps(data)) # 해당 클라이언트에 연결된 소켓에 바이트 바이너리로 변환한 데이터를 송신한다
            return True
        else:
            return False

    # 특정 클라이언트들에 데이터 송신
    def sendReceiver(self, data):
        if self.connected: # 현재 서버가 클라이언트에 연결된 상태라면
            for receiver in data.receiver: # 송신할 데이터에 보관된 클라이언트들에게
                self.client[receiver][0].sendall(pickle.dumps(data)) # 바이트 바이너리로 변환한 데이터를 송신한다
            return True
        else:
            return False

    # 데이터 송신
    # 데이터 송신은 이 메소드를 통해서만 전달된다.
    def send(self, cSock : socket.socket, data):
            self.sendClient(cSock=cSock, data=data) # 단일 클라이언트에 데이터 송신
    
    # 데이터 수신
    def receive(self, rSock : socket.socket = None):
        cAddr = rSock.getpeername() # 데이터를 수신할 클라이언트의 어드레스
        try:
            receiveBytes = bytearray() 
            while True:
                packet = rSock.recv(1024) # 서버로부터 데이터를 수신받는다.
                if not packet: # 수신한 데이터가 없으면
                    raise # 오류 발생
                receiveBytes.extend(packet)
                if len(packet) < 1024:
                    break
            data = pickle.loads(receiveBytes) # 수신받은 데이터를 바이트 바이너리에서 클래스 객체로 변환
            return data # 변환된 데이터를 반환
        except:
            rSock.close() # 클라이언트와 연결된 소켓을 닫고
            self.disconnect(cAddr) # 해당 클라이언트의 정보를 해제한다.
            return None
    
    # 요청 데이터 처리
    # 클라이언트에서 수신받은 요청 데이터의 타입을 구분하여 처리하고
    # 처리된 데이터를 반환하는 함수
    def processData(self, cSock : socket.socket, data):
        chatbotID = '챗봇'
        if type(data) == ReqProperty:
            return ResProperty(self.db.getPropertyList(data))
        elif type(data) == ReqAnalysis:
            placeList = self.db.getPlaceList(data.latitude, data.longitude)
            placeCategoryList = self.db.getPlaceCategoryList(data.latitude, data.longitude)
            population = self.db.getPopulation(data.neighborhood)
            plusSum = 0
            minusSum = 0
            for placeCategory in placeCategoryList:
                if placeCategory.placeCategoryWeight > 0:
                    plusSum += placeCategory.placeCategoryWeight
                else:
                    minusSum += placeCategory.placeCategoryWeight
            expectedSales = int(20000 * population * 0.1 * 4 * plusSum * (100 + minusSum) / 100 * 0.01)
            return ResAnalysis(placeList, placeCategoryList, expectedSales, population)
        elif type(data) == ReqStandard:
            data = f'''[{chatbotID}] : 상승요인은 일반 주거직역에서 주문하는 것 이외에 학교나 공원 등 추가적인 매출의 요인이 될 수 있는 부분이 해당합니다.

하락요인은 치킨 대신 한끼 식사로 선택할 수 있는 식당과 경쟁사인 치킨가게가 해당합니다.
            '''   
            return ResStandard(data)
        elif type(data) == ReqRights:
            data = f'''[{chatbotID}] : 부동산 매물 글에 명시된 금액은 표기했으나 직접 문의인 경우가 많아 해당 매물을 가진 부동산으로 연락을 해보시는게 정확합니다.
            '''
            return ResRights(data)
        elif type(data) == ReqCount:
            data = f'''[{chatbotID}] : 공공데이터에 업데이트되는 공식적인 자료입니다.
            '''
            return ResCount(data)
        ####################################################
        elif type(data) == ReqUpdate:
            data = f'''[{chatbotID}] : 입지 분석에 영향을 주는 요인들은 달에 한번씩 업데이트가 됩니다
            '''
            return ResUpdate(data)
        elif type(data) == ReqUsePay:
            data = f'''[{chatbotID}] : 치킨 프렌차이즈 입지 분석 프로그램의 이용요금은 무료입니다
            '''
            return ResUsePay(data)
        elif type(data) == ReqHistory:
            data = f'''[{chatbotID}] : 이용내역은 남아있지 않으므로  한번 프로그램을 종료하시면 모든 내역이 사라집니다
            '''
            return ResHistory(data)
        #####################################################
        elif type(data) == ReqProTeamName:
            leader = '강신용'
            lovely = '오정민'
            fatty = '유진호'
            cutie = '임승연'
            teamMsg = f'''[{chatbotID}] : <숏패스 소개>
팀장으로는 {leader}, 팀원으로는 {lovely}, {fatty}, {cutie}
총 4명으로 구성 되어 있습니다.
            '''
            return ResProTeamName(teamMsg)
        elif type(data) == ReqChkPopulation:
            chkpopMsg = f'''[{chatbotID}] : 거주 인구수는 지도에 표시된 매물의 동에서 현재 거주 하는 인구 수 입니다.
            '''
            return ResChkPopulation(chkpopMsg)
        elif type(data) == ReqStdSales:
            saleMsg = f'''[{chatbotID}] : 예상 매출액 공식은 월별 예상 손님수 × 기본금 입니다.

월별 예상 손님수 =
동별 거주 인구수 × 0.1 x 4 (동별 거주 인구 중 10%가 한달에 4번 소비한다는 가정)
  × (상승요인의 가중치 총 합) × ( (100 - 하락요인 지수) ÷ 100 ) × 0.01

상승 요인의 가중치 총합 = 상승 요인의 종류의 가중치 × 개수의 합

하락 요인의 지수 = 타종 요식업체의 구간 별 가중치 + 동종 요식업체의 개수당 가중치의 합
            
상승 요인 가중치
공원 : 3
노래방 : 1
PC방 : 1
교육기관 (초등학교 : 1, 중학교 : 1, 고등학교 : 2, 대학교 : 5)

하락 요인 가중치
타종 요식업체 (구간별)
0 ~ 10 곳 : 1
11 ~ 20 곳 : 10
21 ~ 30 곳 : 20
31 ~ 40 곳 : 30
41 ~ 50 곳 : 40
50 곳 이상 : 50
            
동종 요식업체
개수 당 1
            '''
            return ResStdSales(saleMsg)
        elif type(data) == ReqStdFood:
            foodMsg = f'''[{chatbotID}] : 공공데이터를 기준으로 카페나 떡집 등 한끼 식사로 보기에 부족한 업태를 제외한 음식점 데이터를 사용합니다.
            '''
            return ResStdFood(foodMsg)
        elif type(data) == ReqNoAnswer:
            etcMsg = f'''[{chatbotID}] :
Q1. 이 프로그램 개발자의 이름은 무엇인가요?

Q2. 입지 요인 분석에서 상승요인과 하락요인을 구분하는 기준은 무엇인가요?

Q3. 권리금은 이 프로그램에서 알 수 없나요?

Q4. 주변 음식점 개수가 나오는데 정확한가요?

Q5. 지도나 요인들의 업데이트는 얼마나 자주 되나요?

Q6. 이용 요금은 없나요?

Q7. 검색 내역 또는 이용 내역은 뜨지않나요?

Q8. 거주 인구수는 지도에 표시된 부분에 거주하는 사람들의 수인가요?

Q9. 예상 월 매출은 어떤 기준으로 산정된건가요?

Q0. 여기에 표시되는 음식점은 어떤 기준인가요?
            '''
            return ResNoAnswer(etcMsg)
class PlaceData:
    def __init__(self, name, address, latitude, longitude, category, weight):
        self.placeName = name
        self.placeAddress = address
        self.placeLatitude = float(latitude)
        self.placeLongitude = float(longitude)
        self.placeCategory = category
        self.placeWeight = weight
    
    def __str__(self):
        return f"상호명 : {self.placeName} / 주소 : {self.placeAddress} / 위도 경도 : [{self.placeLatitude}, {self.placeLongitude}] / 유형 : {self.placeCategory} / 가중치 : {self.placeWeight}"

class Place:
    def __init__(self, row : dict):
        self.placeId = row['id']
        self.placeName = row['place_name']
        self.placeAddress = row['place_address']
        self.placeLatitude = float(row['place_latitude'])
        self.placeLongitude = float(row['place_longitude'])
        self.placeCategory = row['place_category']
        self.placeWeight = row['place_weight']
    
    def __str__(self):
        return f"상호명 : {self.placeName} / 주소 : {self.placeAddress} / 위도 경도 : [{self.placeLatitude}, {self.placeLongitude}] / 유형 : {self.placeCategory} / 가중치 : {self.placeWeight}"

class PlaceCategory:
    def __init__(self, row : dict):
        self.placeCategoryName = row['place_category']
        self.placeCategoryCount = row['count']
        self.placeCategoryWeight = float(row['weight'])

class Property:
    def __init__(self, row : dict):
        self.propertyId = row['id']
        self.propertyDistrict = row['property_district']
        self.propertyNeighborhood = row['property_neighborhood']
        self.propertyAddress = row['property_address']
        self.propertyLatitude = float(row['property_latitude'])
        self.propertyLongitude = float(row['property_longitude'])
        self.propertyType = row['property_type']
        self.propertyEntitlement = row['property_entitlement']
        self.propertyDeposit = row['property_deposit']
        self.propertyMonthly = row['property_monthly']
        self.propertyArea = row['property_area']
    
    def __str__(self):
        propertyFixDeposit = str(self.propertyDeposit)
        result = ''

        if len(propertyFixDeposit) >= 9:
            result += f'{propertyFixDeposit[:-8]}억'
        if len(propertyFixDeposit) >= 5:
            if propertyFixDeposit[-8:-4] == '0000':
                pass
            elif propertyFixDeposit[-8:-5] == '000':
                result += f'{propertyFixDeposit[-5:-4]}만'
            elif propertyFixDeposit[-8:-6] == '00':
                result += f'{propertyFixDeposit[-6:-4]}만'
            elif propertyFixDeposit[-8:-7] == '0':
                result += f'{propertyFixDeposit[-7:-4]}만'
            else:
                result += f'{propertyFixDeposit[-8:-4]}만'
            if len(propertyFixDeposit) > 0:
                if propertyFixDeposit[-4:] == '0000':
                    result += '원'
                elif propertyFixDeposit[-4:-1] == '000':
                    result += f' {propertyFixDeposit[-1:]}원'
                elif propertyFixDeposit[-4:-2] == '00':
                    result += f' {propertyFixDeposit[-2:]}원'
                elif propertyFixDeposit[-4:-3] == '0':
                    result += f' {propertyFixDeposit[-3:]}원'
                else:
                    result += f' {propertyFixDeposit[-4:]}원'
        if len(propertyFixDeposit) <= 4:
            if propertyFixDeposit[-4:-1] == '000':
                result += f'{propertyFixDeposit[-1:]}원'
            elif propertyFixDeposit[-4:-2] == '00':
                result += f'{propertyFixDeposit[-2:]}원'
            elif propertyFixDeposit[-4:-3] == '0':
                result += f'{propertyFixDeposit[-3:]}원'
            else:
                result += f'{propertyFixDeposit[-4:]}원'
        return f"{self.propertyId}. / 동 : {self.propertyNeighborhood} / 보증금 : {result}"

# 클라이언트가 서버에게 요청으로 보낼 클래스 형식
# 매물 요청
####################################################################
class ReqProperty:
    def __init__(self, maxMoney, minMoney):
        self.maxMoney = maxMoney
        self.minMoney = minMoney
#######################################################################

# 분석 요청
class ReqAnalysis: 
    def __init__(self, latitude : float, longitude : float, neighborhood : str):
        # 분석을 요청할 위치의 위도 경도
        self.latitude = latitude
        self.longitude = longitude
        self.neighborhood = neighborhood

# 서버가 클라이언트에 응답으로 보낼 클래스 형식
# 매물 응답
class ResProperty:
    def __init__(self, propertyList : list[Property]):
        self.propertyList = propertyList

# 분석 응답
class ResAnalysis: 
    def __init__(self, placeList : list[Place], placeCategoryList : list[PlaceCategory], expectedSales : int, population : int):
        self.placeList = placeList
        self.placeCategoryList = placeCategoryList
        self.expectedSales = expectedSales
        self.population = population

#######################################################################
# 이 프로그램 개발자의 이름은 무엇인가요?
# 챗봇 요청
class ReqProTeamName:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResProTeamName:
    def __init__(self, teamMsg : str):
        self.teamMsg = teamMsg
#######################################################################
# 입지 요인 분석에서 상승요인과 하락요인을 구분하는 기준은 무엇인가요?
# 챗봇 요청
class ReqStandard:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResStandard:
    def __init__(self, stdMsg : str):
        self.stdMsg = stdMsg
#######################################################################
# 권리금은 이 프로그램에서 알 수 없나요?
# 챗봇 요청
class ReqRights:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResRights:
    def __init__(self, rightMsg : str):
        self.rightMsg = rightMsg
#######################################################################
# 주변 음식점 개수가 나오는데 정확한가요?
# 챗봇 요청
class ReqCount:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResCount:
    def __init__(self, countMsg : str):
        self.countMsg = countMsg
#######################################################################
# 지도나 요인들의 업데이트는 얼마나 자주 되나요?
# 챗봇 요청
class ReqUpdate:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResUpdate:
    def __init__(self, updateMsg : str):
        self.updateMsg = updateMsg
#######################################################################
# 이용 요금은 없나요?
# 챗봇 요청
class ReqUsePay:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResUsePay:
    def __init__(self, payMsg : str):
        self.payMsg = payMsg
#######################################################################
# 검색 내역 또는 이용 내역은 뜨지않나요?
# 챗봇 요청
class ReqHistory:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResHistory:
    def __init__(self, historyMsg : str):
        self.historyMsg = historyMsg
#######################################################################
# 거주 인구수는 지도에 표시된 부분에 거주하는 사람들의 수인가요?
# 챗봇 요청
class ReqChkPopulation:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResChkPopulation:
    def __init__(self, chkpopMsg : str):
        self.chkpopMsg = chkpopMsg
#######################################################################
# 예상 월 매출은 어떤 기준으로 산정된건가요?
# 챗봇 요청
class ReqStdSales:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResStdSales:
    def __init__(self, saleMsg : str):
        self.saleMsg = saleMsg
#######################################################################
# 여기에 표시되는 음식점은 어떤 기준인가요?
# 챗봇 요청
class ReqStdFood:
    def __init__(self, num : int, msg : str):
        self.num = num
        self.msg = msg

# 챗봇 응답
class ResStdFood:
    def __init__(self, foodMsg : str):
        self.foodMsg = foodMsg
#######################################################################
# 기본 값 혹은 잘못 입력 했을 경우
# 챗봇 요청
class ReqNoAnswer:
    def __init__(self, msg : str):
        self.msg = msg

# 챗봇 응답
class ResNoAnswer:
    def __init__(self, etcMsg : str):
        self.etcMsg = etcMsg
#######################################################################
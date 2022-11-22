import pymysql
import pymysql.cursors

from dataClass import *

# // 위도(latitude) 1km = 0.0091
# // 500m = 0.0091 / 2
# // 경도(longitude) 1km = 0.0113
# // 500m = 0.0113 / 2

class DB:
    def __init__(self):
        self.host = 'localhost'
        self.port = 3306
        self.user = "root"
        self.passwd = "iotiotiot"
        self.dbname = "chicken"
        self.charset = "utf8"

    def connect(self):
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.passwd,
            db=self.dbname,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def getPropertyList(self, data : ReqProperty):
        conn = self.connect()
        result : list[Property] = []
        try:
            with conn.cursor() as cursor:
                #####################################################################################################
                sql = f"SELECT * FROM property WHERE property_deposit BETWEEN {data.minMoney} AND {data.maxMoney}"
                #####################################################################################################
                print(sql)
                cursor.execute(sql)
                for row in cursor:
                    result.append(Property(row))
        finally:
            conn.close()
        return result
    
    def getPlaceList(self, latitude, longitude):
        conn = self.connect()
        result : list[Place] = []
        try:
            with conn.cursor() as cursor:
                sql = f"""SELECT A.* FROM place A inner join (SELECT place_category, max(update_date) as update_date FROM place GROUP BY place_category) B on A.place_category = B.place_category and A.update_date = B.update_date
                WHERE A.place_latitude BETWEEN {latitude - (0.0091 / 2)} AND {latitude + (0.0091 / 2)} AND A.place_longitude BETWEEN {longitude - (0.0113 / 2)} and {longitude + (0.0113 / 2)}"""
                print(sql)
                cursor.execute(sql)
                for row in cursor:
                    result.append(Place(row))
        finally:
            conn.close()
        return result

    
    def getPlaceCategoryList(self, latitude, longitude):
        conn = self.connect()
        result : list[PlaceCategory] = []
        try:
            with conn.cursor() as cursor:
                sql = f"""SELECT place_category, count(*) as count, 
                (CASE WHEN place_category = "음식" THEN (CASE WHEN count(*) >= 50 THEN 50 ELSE floor(count(*) / 10) * 10 END) * -1
                ELSE sum(place_weight) END) as weight FROM (SELECT A.* FROM place A inner join (SELECT place_category, max(update_date) as update_date FROM place GROUP BY place_category) B on A.place_category = B.place_category and A.update_date = B.update_date) C 
                WHERE place_latitude BETWEEN {latitude - (0.0091 / 2)} AND {latitude + (0.0091 / 2)} AND place_longitude BETWEEN {longitude - (0.0113 / 2)} AND {longitude + (0.0113 / 2)} 
                GROUP BY place_category"""
                print(sql)
                cursor.execute(sql)
                for row in cursor:
                    result.append(PlaceCategory(row))
        finally:
            conn.close()
        return result

    def getPopulation(self, neighborhood : str):
        conn = self.connect()
        result : int = 0
        try:
            with conn.cursor() as cursor:
                sql = f"SELECT population_count FROM population WHERE population_name = '{neighborhood}'"
                print(sql)
                cursor.execute(sql)
                result = cursor.fetchone()['population_count']
        finally:
            conn.close()
        return result
        
    def insertPlaceList(self, placeDataList : list[PlaceData]):
        conn = self.connect()
        result : bool = True
        try:
            with conn.cursor() as cursor:
                for placeData in placeDataList:
                    sql = f"INSERT INTO place (place_name, place_address, place_latitude, place_longitude, place_category, place_weight, update_date) VALUES ('{placeData.placeName}', '{placeData.placeAddress}', {placeData.placeLatitude}, {placeData.placeLongitude}, '{placeData.placeCategory}', {placeData.placeWeight}, curdate())"
                    cursor.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
            result = False
        finally:
            conn.close()
        return result
    
    # def regist(self, data : ReqRegist) -> ResRegist:
    #     conn = self.connect()
    #     result : ResRegist = ResRegist(True)
    #     try:
    #         with conn.cursor() as cursor:
    #             sql = f"INSERT INTO user (id, password, name, email, phone, isOnline) VALUES ('{data.id}', '{data.password}', '{data.name}', '{data.email}', '{data.phone}', false)"
    #             cursor.execute(sql)
    #         conn.commit()
    #     except Exception:
    #         conn.rollback()
    #         result.isItSuccess = False
    #     finally:
    #         conn.close()
    #     return result

    # def duplicateCheck(self, data : ReqDuplicateCheck) -> ResDuplicateCheck:
    #     conn = self.connect()
    #     result : ResDuplicateCheck = ResDuplicateCheck(True)
    #     try:
    #         with conn.cursor() as cursor:
    #             sql = f"SELECT * FROM user WHERE id = '{data.id}'"
    #             cursor.execute(sql)
    #             row = cursor.fetchone()
    #             if row is None:
    #                 result.doesItExisted = False
    #     finally:
    #         conn.close()
    #     return result


    # def login(self, data: ReqLogin) -> ResLogin:
    #     conn = self.connect()
    #     result : ResLogin = ResLogin(rescode = 3, id = data.id)
    #     try:
    #         with conn.cursor() as cursor:
    #             sql = f"SELECT * FROM user WHERE id = '{data.id}'"
    #             cursor.execute(sql)
    #             row = cursor.fetchone()
    #             if row is None:
    #                 result.rescode = 0

    #         if result.rescode != 3:
    #             return result
            
    #         with conn.cursor() as cursor:
    #             sql = f"SELECT isOnline FROM user WHERE id = '{data.id}' and password = '{data.password}'"
    #             cursor.execute(sql)
    #             row = cursor.fetchone()
    #             if row is None:
    #                 result.rescode = 1
    #             elif row['isOnline'] == 1:
    #                 result.rescode = 2
            
    #         with conn.cursor() as cursor:
    #             sql = f"UPDATE user SET isOnline = true WHERE id = '{data.id}'"
    #             cursor.execute(sql)

    #         conn.commit()
    #     except:
    #         conn.rollback()
    #     finally:
    #         conn.close()
    #     return result

    # def logout(self, id : str):
    #     conn = self.connect()
    #     result : bool = True
    #     try:
    #         with conn.cursor() as cursor:
    #             sql = f"UPDATE user SET isOnline = false WHERE id = '{id}'"
    #             cursor.execute(sql)
    #         conn.commit()
    #     except:
    #         conn.rollback()
    #         result = False
    #     finally:
    #         conn.close()
    #     return result
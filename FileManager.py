# 만들지 말지 생각만 하는중
from collections import defaultdict
import pickle

class FileManager:
    # 저장해야되는 것들 :
    # - 장바구니
    # - 꼭 리스트
    # - 들으면 좋음 리스트
    # - 시간표 리스트

    # 사용법:
    # (1) 저장하기
    #   FileManager를 선언한다.
    #   - ex) FileManager fm
    #   FileManager에 파일을 할당한다.
    #   - ex) fm.Must_group = Must_group
    #   save를 누른다
    #   - ex) fm.save()  -> scheduleManagerSaveFile.pickle이 생성될거임
    # (2) 로드하기
    #   FileManager에서 load 호출
    #   - ex) fm.load()
    #   그럼 멤버변수에 객체가 로드된다.
    #   갖다 쓰면 된다.
    #   - ex) Must_group = fm.Must_group()

    # 대충 만든거라 아직 테스트 안해봄
    def __init__(self):
        self.basket = None
        self.Must_group = None
        self.Prefer_group = None
        self.schedules = None
        self.data_list = [self.basket, self.Must_group, self.Prefer_group, self.schedules]
        self.filename = "scheduleManagerSaveFile.pickle"

    def save(self):
        with open("scheduleManagerSaveFile.pickle", "wb") as writef:
            pickle.dump(writef, self.data_list)
    
    def load(self):
        with open("scheduleManagerSaveFile.pickle", "rb") as readf:
            loaded_data = pickle.load(readf)
        self.basket = loaded_data[0]
        self.Must_group = loaded_data[1]
        self.Prefer_group = loaded_data[2]
        self.schedules = loaded_data[3]
    

            
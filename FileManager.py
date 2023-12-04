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
    #   - ex) fm = FileManager()
    #   FileManager에 파일을 넣는다.
    #   - ex) fm.must_group = Must_group
    #   save 호출
    #   - ex) fm.save()  -> scheduleManagerSaveFile.pickle이 생성될거임
    # (2) 로드하기
    #   load를 호출한다
    #   - ex) fm.load()
    #   그럼 멤버변수에 객체가 로드된다.
    #   갖다 쓰면 된다.
    #   - ex) Must_group = fm.must_group

    # 대충 만든거라 아직 테스트 안해봄
    def __init__(self):
        self.basket = None
        self.must_group = None
        self.prefer_group = None
        self.schedules = None
        self.filename = "scheduleManagerSaveFile.pickle"

    def save(self, basket=None, must_group=None, prefer_group=None, schedules=None):
        data_list = [basket, must_group, prefer_group, schedules]
        with open(self.filename, "wb") as writef:
            pickle.dump(data_list, writef)
    
    def load(self):
        try:
            with open(self.filename, "rb") as readf:
                loaded_data = pickle.load(readf)
            self.basket = loaded_data[0]
            self.must_group = loaded_data[1]
            self.prefer_group = loaded_data[2]
            self.schedules = loaded_data[3]
            return True
        except:
            self.basket = None
            self.must_group = None
            self.prefer_group = None
            self.schedules = None
            return False
    
    def __str__(self):
        return str(self.basket) + str(self.must_group) + str(self.prefer_group) + str(self.schedules)
    
if __name__ == "__main__":
    f = FileManager()
    f.filename = "saveTestFile"
    f.prefer_group = "Prefer Group"
    f.basket = [[1], [1,2], [1,2,3]]
    f.must_group = FileManager()
    f.schedules = {"dict" : "TEST"}
    f.save()
    f.load()
    print(f)

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
        self.must_layout = None
        self.prefer_layout = None
        self.filename = "scheduleManagerSaveFile.pickle"
        self.data_list = {}
        self.save_and_load = True

    # "key":data 쌍으로 data_list에 저장
    def add(self, key, data):
        self.data_list[key] = data

    # "key"로 저장된 데이터 꺼냄
    def get(self, key):
        if key not in self.data_list.keys():
            return None
        return self.data_list[key]
    
    # data_list 로드
    def load(self):
            if not self.save_and_load:
                return
            try:
                with open(self.filename, "rb") as readf:
                    self.data_list = pickle.load(readf)
                return True
            except:
                self.data_list = {}
                return False
    


    # data_list 파일로 저장
    def save(self):
        if not self.save_and_load:
            return
        with open(self.filename, "wb") as writef:
            try:
                pickle.dump(self.data_list, writef)
                return True
            except:
                return False
            
    def __str__(self):
        #return str(self.basket) + str(self.must_group) + str(self.prefer_group) + str(self.schedules)
        s = ''
        for key, val in self.data_list.items():
            s += f"'{key}':'{val}'"
            s += ' $ '
        return s
        
        '''
    def save(self, basket=None, must_group=None, prefer_group=None, must_layout=None, prefer_layout=None, schedules=None):
        data_list = [basket, must_group, prefer_group, schedules]
        with open(self.filename, "wb") as writef:
            pickle.dump(data_list, writef)
            '''
    '''
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
    '''

    
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

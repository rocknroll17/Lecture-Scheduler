import pickle # pickle 모듈로 저장함

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
    #   FileManager에 key:value 쌍으로 파일을 넣는다.
    #   - ex) fm.add("must_group") = Must_group
    #   save 호출
    #   - ex) fm.save()  -> 파일이 생성됨 (기본은 save.data)
    # (2) 로드하기
    #   load를 호출한다
    #   - ex) fm.load()
    #   그럼 멤버변수에 객체가 로드된다.
    #   저장한 키값으로 갖다 쓰면 된다.
    #   - ex) Must_group = fm.get("must_group")

    def __init__(self):
        self.filename = "save.data"
        self.data_list = {} # 딕셔너리에 저장할 내용 담아둔다
        self.save_and_load = True

    # key:data 쌍으로 data_list에 저장
    def add(self, key, data):
        self.data_list[key] = data

    # key로 저장된 데이터 꺼냄
    def get(self, key):
        if key not in self.data_list.keys():
            return None
        return self.data_list[key]
    
    # data_list 로드
    def load(self):
            if not self.save_and_load:
                return False
            try:
                with open(self.filename, "rb") as readf:
                    self.data_list = pickle.load(readf) # 피클로 읽어온다
                return True
            except:
                self.data_list = {}
                return False
    
    # data_list 파일로 저장
    def save(self):
        if not self.save_and_load:
            return False
        with open(self.filename, "wb") as writef:
            try:
                pickle.dump(self.data_list, writef) # 피클로 저장한다
                return True
            except:
                return False
            
    def __str__(self):
        s = ''
        for key, val in self.data_list.items():
            s += f"'{key}':'{val}'"
            s += ' $ '
        return s
    
if __name__ == "__main__":
    # 테스트 코드
    f = FileManager()
    f.filename = "saveTestFile"
    f.save()
    f.load()
    print(f)

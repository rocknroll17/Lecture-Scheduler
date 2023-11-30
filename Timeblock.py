class Timeblock:
    # 시간표 한 블럭에 대한 정보
    # 강의를 두번에 걸쳐서 하는 강의는, Timeblock을 두 개 갖는다
    # ex) 월 34, 수 4 -> [Timeblock('월', 3, "2:00"), Timeblock('수', 4, '1:00')]
    # 교시랑 시간도 같이 넣자
    def __init__(self):
        self.day = ""  # 요일 "월" ~ "일"
        self.period = 0  # N교시
        self.course_time = "00:00" # HH:MM -> H시간 MM분 강의
        self.start_time = "00:00" # 시작시간 HH:MM 형식으로
        self.end_time = "00:00" # 종료시간 HH:MM 형식으로
        
    def __init__(self, day, period, course_time, start_time = "", end_time = ""):
        self.day = day
        self.period = period
        self.course_time = course_time
        self.start_time = start_time # 나중에 만들기
        self.end_time = end_time # 나중에 만들기

    def __str__(self):
        return f"{self.day}/{self.period}/{self.course_time}"
    
    def __repr__(self):
        return self.__str__

    ## 비교연산자 오버로딩 ##
    def __eq__(self, other):
        # ==
        pass
    def __ne__(self, other):
        # !=
        pass
    def __gt__(self, other):
        # <
        pass
    def __ge__(self, other):
        # <=
        pass
    def __le__(self, other):
        # >=
        pass
    def __lt__(self, other):
        # >
        pass
class Timeblock:
    # 시간표 한 블럭에 대한 정보
    # 강의를 두번에 걸쳐서 하는 강의는, Timeblock을 두 개 갖는다
    # ex) 월 34, 수 4 -> [Timeblock('월', 3, "2:00"), Timeblock('수', 4, '1:00')]
    # 교시랑 시간도 같이 넣자
    day_value = {'일':0, '월':1, '화':2, '수':3, '목':4, '금':5, '토':6}
    def __init__(self):
        self.day = ""  # 요일 "월" ~ "일"
        self.period = 0  # N교시
        self.course_time = "00:00" # HH:MM -> H시간 MM분 강의
        self.start_time = "00:00" # 시작시간 HH:MM 형식으로
        self.end_time = "00:00" # 종료시간 HH:MM 형식으로
        self.startmin = 0 # 시작시간 분으로 환산 (크기비교용)
        self.endmin = 0 # 종료시간 분으로 환산 (크기비교용)
        
    def __init__(self, day, period, course_time, start_time, end_time):
        self.day = day
        self.period = period
        self.course_time = course_time
        self.start_time = start_time # 시작시간 HH:MM 
        self.end_time = end_time # 종료시간 HH:MM 
        self.startmin = Timeblock.time_to_int(start_time)
        self.endmin = Timeblock.time_to_int(end_time)

    def intersects_with(self, other):
        # 해당 timeblock과 other timeblock이 겹치는가? -> True False
        if self.day != other.day:
            return False
        if self.startmin < other.startmin and self.endmin > other.startmin:
            return True
        elif other.startmin < self.startmin and other.endmin > self.startmin:
            return True
        return False
    
    @staticmethod
    def time_to_int(time):
    # 분 단위로 바꿔줌
        hour, min = map(int, time.split(":"))
        return min + hour * 60

    ## 내장함수 ##
    def __str__(self):
        return f"{self.day}/{self.period}/{self.course_time}"
    
    def __repr__(self):
        return self.__str__()

    ## 비교연산자 오버로딩 ##
    def __eq__(self, other):
        # ==
        return (self.day == other.day) and (self.period == other.period) and (self.course_time == other.course_time)
    
    def __ne__(self, other):
        # !=
        return not self.__eq__(self, other)

    def __ge__(self, other):
        # >=
        # 더 큰 경우. 겹쳐도 됨 (= 더 늦게 시작한다)
        # 요일 비교
        if self.day != other.day:
            return Timeblock.day_value[self.day] > Timeblock.day_value[other.day]
        return self.startmin > other.startmin
    
    def __gt__(self, other):
        # > 
        # 겹치지 않고 더 큰 경우
        # 요일 비교
        if self.day != other.day:
            return Timeblock.day_value[self.day] > Timeblock.day_value[other.day]
        return self.startmin > other.startmin and self.startmin > other.endmin

    def __le__(self, other):
        # <=
        # 더 작은 경우. 겹쳐도 됨 (= 더 일찍 끝난다)
        if self.day != other.day:
            return Timeblock.day_value[self.day] < Timeblock.day_value[other.day]
        return self.startmin < other.startmin

    def __lt__(self, other):
        # <
        #  겹치지 않고 더 작은 경우
        if self.day != other.day:
            return Timeblock.day_value[self.day] < Timeblock.day_value[other.day]
        return self.startmin < other.startmin and self.endmin < other.startmin



if __name__ == "__main__":

    pass
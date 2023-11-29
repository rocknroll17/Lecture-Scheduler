class Timeblock():
    def __init__(self):
        self.day = ""  # 요일 "월" ~ "일"
        self.period = 0  # N교시
        self.courseTime = "0:00" # H:MM -> H시간 MM분 강의
        
    def __init__(self, day, period, courseTime):
        self.day = day
        self.period = period
        self.courseTime = courseTime
        
    def __str__(self):
        pass
    
    def __repr__(self):
        pass
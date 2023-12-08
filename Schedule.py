# 시간표 객체
# - 완성된 하나의 시간표를 가리킴
# - 사용자가 듣고 싶은 강의 담겨있음

class Schedule:
    schedule_counts = 0 # 클래스변수 - 스케줄 객체 수 관리
    def __init__(self):
        self.__courses = [] # 시간표에 들어갈 강의들.
        self.__id = Schedule.schedule_counts # 스케줄 개수로 id 부여 (자기식별용)
        Schedule.schedule_counts += 1

    # 강의 추가
    def append(self, course):
        # 시간 겹치는 강의 있는지 확인
        if self.check_intersection(course):
            return False
        self.__courses.append(course) # 강의 추가
        return True
    
    # 시간표에 course랑 겹치는 강의 있는지 
    def check_intersection(self, course):
        # 시간표에 있는 각 강의의 Timeblock과 겹치는지 비교
        for _course in self.__courses:
            for _time in _course.time:
                for time in course.time:
                    if time.intersects_with(_time):
                        return True
        return False
    
    def get_id(self):
        return self.__id
    
    # index번째 원소 반환
    def get(self, index):
        try:
            ret = self.__course[index]
            return ret
        except Exception as e:
            print(e)
            return None
    
    # 시간 순 정렬
    def sort(self):
        self.__courses.sort(key=lambda x : x.time.period)   
    
    # 시간표 리스트 반환
    def get_courses(self):
        return self.__courses[:]

    # 내장함수들
    # __getitem__ : 객체 인덱스 접근 시 호출  ex) s가 Schedule 객체일 때 s[i] -> __getitem(self, i)__
    def __getitem__(self, index):
        return self.__course[index]
        
    # __len__ : len()으로 객체 덮었을 때 반환 값
    def __len__(self):
        return len(self.__courses)
    
    # __str__ : 객체 출력시 나오는 문자열
    def __str__(self):
        s = ''
        for course in self.__courses:
            s += f"[{course}] "
        return s
# 시간표 객체
# 완성된 하나의 시간표 객체
# 사용자가 듣고 싶은 강의 담겨있음
# 이게 GUI에 시간표 탭에 뜨게 할 예정

class Schedule:
    def __init__(self):
        self.__courses = [] 
        # 담은 강의 - 시간 순으로 정렬해서 유지 -> 이진트리??
        # private임
    def add_course(self, course):
        self.__courses.append(course)
        self.__courses.sort(key=lambda x : x.time.period)
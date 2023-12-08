from collections import defaultdict # key가 존재하지 않으면 디폴트값 반환
from Course import Course

# 꼭 or 들으면 좋음 목록을 가리키는 클래스
# 꼭 or 들으면 좋음 목록은 '강의 그룹의 그룹'을 저장한다
# - 꼭 목록이던 들으면 좋음 목록이던 강의 그룹 여러가지를 저장함.
#   같은 그룹에 있다 -> 여기있는 강의 중 하나만 들으면 된다
# - 각 그룹은 CourseGroup(아래에 선언) 객체로 저장된다
class Candidate:
    def __init__(self):
        self.__groups = [] # 그룹 단위로 저장함 (Course 리스트의 리스트)
        self.__ids = [] # 강의 존재하는지 확인용. (defaultdict의 리스트)

    def add(self, group): 
        # group을 더함 (group : course의 리스트)
        self.__groups.append(group)
        __id = defaultdict(bool)  # defaultdict(bool) : 존재하지 않는 key로 검색하면 False 반환
        for c in group:
            __id[c.course_id] = True
        self.__ids.append(__id)
    
    def add_course(self, course):
        # 새로운 그룹에 course 추가
        self.__groups.append([course])
    
    def add_course(self, group_index, course):
        # i번째 그룹에 course 추가
        self.__groups[group_index].append(course)

    def delete(self, index):
        del self.__groups[index]

    def remove(self, index):
        if not isinstance(index, int) or not (0 <= index < len(self.__groups)):
            return
        self.__groups.remove(self.__groups[index])

    def exists(self, group_index, course_id):
        # i번째 그룹에 course가 존재하는지
        return self.__ids[group_index][course_id]
    
    def get_groups(self):
        return self.__groups
    
    def set_groups(self, group):
        self.__groups = group

    def get_group(self, index):
        if not isinstance(index, int) or not (0 <= index < len(self.__groups)):
            return None
        return self.__groups[index]
    
    def empty(self):
        return len(self.__groups) == 0
    
    def pop(self):
        return self.__groups.pop()

    def __str__(self):
        return str(self.__groups)


# Basket 클래스 -> CourseGroup 클래스로 개명
# - 바꾼 이유 : 
#   해당 클래스는 장바구니를 나타내기 이전에 '강의를 담은 그룹'을 나타내는 클래스임
#   그래서 Basket이라고 직접 이름짓기보단 CourseGroup처럼  범용적인 이름으로 개명하는 게 낫다고 판단함
#   + 강의를 담는 그룹이므로 기타 Course 객체 리스트도 CourseGroup 객체로 만들 수 있고
#     Candidate에서도 CourseGroup의 리스트를 저장하도록 만들 수 있음

# CourseGroup : 강의를 담는 그룹
# - 리스트처럼 사용할 수 있게 하는 데에 중점을 둠
#   a = CourseGroup일 때
#   인덱싱 가능 : a[0]  ->  0번째 강의 반환
#   append 가능 : a.append(course)  ->  course를 그룹에 추가
# - 리스트처럼 활용하되, Course 객체만 담을 수 있도록 타입체킹 기능 + 중복 강의는 담지 않는 등의 편의기능 추가


#class Basket:
class CourseGroup:
    # 생성자 - course 리스트 객체로 받음
    def __init__(self, courses=None):
        self.__courses = []
        self.__ids = [] # 강의 존재하는지 확인용
        if courses:
            for c in courses:
                self.append(c)

    # 강의 추가
    def append(self, course):
        # course 객체 아니면 기각
        if not isinstance(course, Course):
            print(f"{course} is not course")
            return
        # 이미 그룹에 존재하면 기각
        if course.course_id in self.__ids:
            return
        self.__courses.append(course)
        self.__ids.append(course.course_id)

    # 삭제 : index의 강의 삭제
    def delete(self, index):
        course = self.__courses[index]
        self.__ids.remove(course.course_id)
        del self.__courses[index]
    
    # 삭제 : course에 해당하는 강의 삭제
    def remove(self, course):
        self.__ids.remove(course.course_id)
        self.__courses.remove(course)
    
    # 강의 존재하는지
    def exists(self, lecture):
        return lecture.course_id in self.__ids
    
    # 리스트 날리기
    def clear(self):
        self.__ids = []
        self.__courses = []
        
    # 내장함수들
    # __len__ : len()으로 감쌀 때 반환값
    def __len__(self):
        return len(self.__courses)
    
    # __getitem__ : 객체 인덱스 접근 시 호출  ex) a가 Candidate 객체일 때 a[index] -> __getitem__(self, index) 호출
    def __getitem__(self, index):
        return self.__courses[index]

    # __str__ : 객체 print 시 문자열 반환
    def __str__(self):
        s = ''
        for c in self.__courses:
            s += f"[{c}] "
        return s
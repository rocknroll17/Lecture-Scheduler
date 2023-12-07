from collections import defaultdict

class Candidate:
    # 꼭, 들으면 좋음
    def __init__(self, isPrefer = False):
        self.__groups = [] # 그룹 단위로 저장함 (Course 리스트의 리스트)
        self.__ids = [] # 강의 존재하는지 확인용 -> 근데 여기 add는 어떻게 돌아가는지 몰겟음

    def add(self, group):
        # group : course의 리스트
        self.__groups.append(group)
        __id = defaultdict(bool)
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

    #def remove(self, group):
        #self.__groups.remove(group)
    def remove(self, index):
        if not isinstance(index, int) or not (0 <= index < len(self.__groups)):
            return
        self.__groups.remove(self.__groups[index])

    def exists(self, group_index, course_id):
        # i번째 그룹에 course가 존재하는지
        return self.__ids[group_index][course_id]
    
    def get_groups(self):
        return self.__groups
    
    def get_group(self, index):
        if not isinstance(index, int) or not (0 <= index < len(self.__groups)):
            return None
        return self.__groups[index]
    
    def pop(self):
        return self.__groups.pop()

    def __str__(self):
        return str(self.__groups)


class Basket:
    # 장바구니
    def __init__(self):
        self.data = []
        self.__ids = defaultdict(bool) # 강의 존재하는지 확인용

    def add(self, lecture):
        self.data.append(lecture)
        self.__ids[lecture.course_id] = True

    def delete(self, index):
        del self.data[index]

    def remove(self, lecture):
        self.data.remove(lecture)
        self.__ids.pop(lecture.course_id)
    
    def exists(self, lecture_id):
        return self.__ids[lecture_id]
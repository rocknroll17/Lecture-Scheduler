from collections import defaultdict

class Candidate:
    #꼭 들으면 좋음
    def __init__(self):
        self.data = []
        self.__ids = defaultdict(bool) # 강의 존재하는지 확인용

    def add(self, group):
        self.data.append(group)

    def delete(self, index):
        del self.data[index]

    def remove(self, group):
        self.data.remove(group)

class Basket:
    #장바구니
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
    
    def exists(self, lecture):
        return self.__ids[lecture.course_id]
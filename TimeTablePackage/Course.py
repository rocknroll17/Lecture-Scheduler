class Course():
    def __init__(self, one_course):
        # one_course 문자열 파싱해서 클래스변수 저장
        self.college = "" # 대학
        self.department = "" # 개설학과
        self.isMajor = "" # 이수구분 - 전공인지 -> 필요한가??
        self.grade = 0 # 학년 -> 필요한가??
        self.courseId = 0 # 과목번호
        self.title = "" # 과목명
        self.credit = 0 # 학점
        self.instructor = "" # 강의자
        #self.vector<Timeblock> courseTime # 강의시간. Timeblock 배열에 저장.
        self.courseType = "" # 강의유형 -> 필요한가??
        self.annotations = "" # 비고 -> 필요한가??
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.title
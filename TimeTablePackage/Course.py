class Course():
    def __init__(self, lecture):
        # lecture 문자열 파싱해서 클래스변수 저장
        self.college = lecture[0] # 대학
        self.department = lecture[1] # 개설학과
        self.campus = lecture[2] #캠퍼스
        self.grade = lecture[3] # 학년
        self.course = lecture[4] #과정
        self.category = lecture[5] # 이수구분
        self.courseId = lecture[6] # 과목번호
        self.title = lecture[7] # 과목명
        self.credit = lecture[8] # 학점
        self.instructor = lecture[9] # 강의자
        self.closed = lecture[10] #폐강 여부
        self.time = lecture[11] # 강의시간
        self.annotations = lecture[12] # 비고
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.courseId +" "+self.title
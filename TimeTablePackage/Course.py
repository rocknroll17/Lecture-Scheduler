class Course:
    def __init__(self, lecture):
        self.college = lecture[0]  # 대학
        self.department = lecture[1]  # 개설학과
        self.campus = lecture[2]  # 캠퍼스
        self.grade = lecture[3]  # 학년
        self.course = lecture[4]  # 과정
        self.category = lecture[5]  # 이수구분
        self.courseId = lecture[6]  # 과목번호
        self.title = lecture[7]  # 과목명
        self.credit = lecture[8]  # 학점
        self.instructor = lecture[9]  # 강의자
        self.closed = lecture[10]  # 폐강 여부
        self.time = lecture[11]  # 강의시간
        self.annotations = lecture[12]  # 비고

    def __repr__(self):
        return self.__str__()

    def __str__(self, option=None):
        if option is None:
            return f"{self.courseId} {self.title}"
        elif option == 'college':
            return self.college
        elif option == 'department':
            return self.department
        elif option == 'campus':
            return self.campus
        elif option == 'grade':
            return self.grade
        elif option == 'course':
            return self.course
        elif option == 'category':
            return self.category
        elif option == 'courseId':
            return self.courseId
        elif option == 'title':
            return self.title
        elif option == 'credit':
            return self.credit
        elif option == 'instructor':
            return self.instructor
        elif option == 'closed':
            return self.closed
        elif option == 'time':
            return self.time
        elif option == 'annotations':
            return self.annotations
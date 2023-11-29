fails = []

class Course:
    def __init__(self):
        pass
    def __init__(self, line):
        self.parse_line(line)
        
    
    def parse_line(self, line):
        self.college = line[0]  # 대학
        self.department = line[1]  # 개설학과
        self.campus = line[2]  # 캠퍼스
        self.grade = line[3]  # 학년
        self.course = line[4]  # 과정
        self.category = line[5]  # 이수구분
        self.courseId = line[6]  # 과목번호
        self.title = line[7]  # 과목명
        self.credit = line[8]  # 학점
        self.instructor = line[9]  # 강의자
        self.closed = line[10]  # 폐강 여부
        self.time = self.__parse_time_info(line[11]) # 강의시간 -> Timeblock객체로
        self.annotations = line[12]  # 비고
        
    def __parse_time_info(self, time_string):
        # '수1,2 / 310관(310관) B603호 <대형강의실>' 꼴의 문자열을 Timeblock 객체로 만들어서 반환
        try:
            time_info = time_string.split('/')
            time_info = [t.strip() for t in time_info]
            day_period = time_info[0]
            day_kor = day_period[0]
            periods = day_period[1:].split(',')
            periods = list(map(int, periods))

            #print(self.title, day_kor, periods)
            # 파싱해서 Timeblock 객체로 만들어서 반환해야함
        except:
            # 파싱 실패한 경우 -> 시간 란이 공란임
            fails.append(f"'{self.title}' '{time_string}'")
            pass



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
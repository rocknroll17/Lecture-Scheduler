class Course():
    college = "" # 대학
    department = "" # 개설학과
    isMajor = "" # 이수구분 - 전공인지 -> 필요한가??
    grade = 0 # 학년 -> 필요한가??
    courseId = 0 # 과목번호
    title = "" # 과목명
    credit = 0 # 학점
    instructor = "" # 강의자
    #vector<Timeblock> courseTime # 강의시간. Timeblock 배열에 저장.
    courseType = "" # 강의유형 -> 필요한가??
    annotations = "" # 비고 -> 필요한가??

    def __init__(self, one_course):
        # one_course 문자열 파싱해서 클래스변수 저장

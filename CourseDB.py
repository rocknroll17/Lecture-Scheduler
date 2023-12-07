from Timeblock import *
import Course # 나중에 지워 test

class CourseDB():
    def __init__(self, path=""):
        self.course_list = []
        self.load_path = "Data/lecture.txt"
        if path:
            self.load_path = path
        self.load_courses(self.load_path)

    def add(self, lecture):
        self.course_list.append(lecture)

    def sort(self, option):
        self.course_list.sort(key=lambda x: getattr(x, option))
    
    def search_by_id(self, id):
        for c in self.course_list:
            if c.course_id == id:
                return c
    
    def load_courses(self, path=""):
        if path:
            _path = path
        else:
            _path = self.load_path
        with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
            lecture_data = f.readlines()
            for i in range(len(lecture_data)):
                # for i in range(300):
                course = Course.Course(lecture_data[i].strip().split("$"))
                self.add(course)


    def search(self, condition):
        # 검색 버튼 누르면 호출되는 메서드
        #   condition : gui에서 사용자가 설정한 검색조건
        #   condition[0] : 대학명
        #   condition[1] : 학과명
        #   condition[2] : 이게 강의명인듯
        #   condition[3] : 요일 "일" ~ "월"
        #   condition[4] : 교시
        
        # search 방식
        # 일단 모든 강의를 담아두고,
        # condition[0]부터 condition[4]까지 차례차례 필터링한다

        # result : 리턴할 강의목록. 일단 모든 강의를 담아두고 시작함
        result = self.course_list[:]

        # 필터 함수 : 함수에 적힌 대로 강의 필터링 진행
        def checkCollege(course): # 대학 필터 : 강의와 전체 일치하면 True
            return course.college == condition[0]
        
        def checkDepartment(course): # 학과명 필터 : 강의와 전체 일치하면 True
            return course.department == condition[1]
        
        def checkTitle(course): # 강의명 필터 : 강의명과 일부만 일치하면 True
            return condition[2] in course.title

        def checkDay(course): # 요일 필터 : 해당 요일이 강의 요일과 하나라도 일치하면 True
            for t in course.time:
                if t.day == condition[3]:
                    return True
            return False
        
        def checkPeriod(course): # 교시 필터 : 해당 교시가 course의 강의시간에 껴있으면 True
            period_to_min = (int(condition[4]) + 8) * 60
            for t in course.time:
                if t.startmin <= period_to_min < t.endmin:
                    if (not condition[3]) or (condition[3] and t.day == condition[3]):
                        # 요일도 설정된 경우, 교시+요일 둘 다 겹쳐야 함
                        return True
            return False
        
        # 대학 검색 (ex. 대학(전체), 소프트웨어대학)
        if condition[0]:
            result = list(filter(checkCollege, result))

        # 학과명 검색 (ex. 소프트웨어학부)
        if condition[1]:
            result = list(filter(checkDepartment, result))

        # 요일 (ex. '월', '화')
        if condition[3]:
            result = list(filter(checkDay, result))

        # 교시 (ex. 1, 2)
        if condition[4]:
            result = list(filter(checkPeriod, result))

        # 강의명 (ex. ACT, AC) -> 연산 젤 많을 거 같아서 뒤로 뺐음
        if condition[2]:
            result = list(filter(checkTitle, result))

        return result

if __name__ == "__main__":
    # DB 테스트
    db = CourseDB()
    # DB 로드
    with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
        lecture_data = f.readlines()
        for i in range(len(lecture_data)):
        #for i in range(600, 900):
            course = Course(lecture_data[i].strip().split("$"))
            db.add(course)
    # 검색 수행
    # 대학 학과명 강의명 요일 교시
    condition = ["", "", "AC", "월", "3"]
    results = db.search(condition)
    for r in results:
        print(r)
    print(len(db.course_list), len(results))
    pass
class CourseDB():
    course_list = list()

    def __init__(self, course_all):
        #course_all 문자열을 받아서 \n으로 나누어서 Course 객체를 생성하여 리스트에 저장

class CourseDB():
    def __init__(self):
        self.course_list = []

    def add(self, lecture):
        self.course_list.append(lecture)

    def sort(self):
        self.course_list.sort()
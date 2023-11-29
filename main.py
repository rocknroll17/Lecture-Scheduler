from TimeTablePackage import Course
from TimeTablePackage import CourseDB
from TimeTablePackage import Timeblock
lecture_list = []
with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
    lecture_data = f.readlines()
    for i in range(len(lecture_data)):
        lecture_list.append(Course.Course(lecture_data[i].strip().split("$")))
print(lecture_list)
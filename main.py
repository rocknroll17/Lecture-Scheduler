from TimeTablePackage import Course
from TimeTablePackage import CourseDB
from TimeTablePackage import Timeblock
lecture_list = []
DB = CourseDB.CourseDB()
with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
    lecture_data = f.readlines()
    for i in range(len(lecture_data)):
        DB.add(Course.Course(lecture_data[i].strip().split("$")))
        
DB.sort('courseId')
print(DB.course_list[0].time)
for f in Course.fails:
    print(f)

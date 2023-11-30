import Course
from TimeTablePackage import CourseDB
lecture_list = []
DB = CourseDB.CourseDB()
with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
    lecture_data = f.readlines()
    #for i in range(len(lecture_data)):
    for i in range(300):
        course = Course.Course(lecture_data[i].strip().split("$"))
        DB.add(course)
        print(f"{course.title[:5]}", end=" ")
        for t in course.time:
            print(t, end=" ")
        print(f" '{course.time_info_raw_string}'",end=" ")
        print()
        
DB.sort('courseId')


for f in Course.fails:
    print(f"fails: {f}")

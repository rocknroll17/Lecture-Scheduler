from Course import *
from CourseDB import *

lecture_list = []
DB = CourseDB()
with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
    lecture_data = f.readlines()
    #for i in range(len(lecture_data)):
    for i in range(300, 600):
        course = Course(lecture_data[i].strip().split("$"))
        DB.add(course)
        # Timeblock 파싱 확인용
        print(f"{course.title[:5]}", end=" ")
        for t in course.time:
            print(t, end=" ")
        print(f" '{course.time_info_raw_string}'",end=" ")
        print()
        
DB.sort('courseId')

# 파싱 실패한 거 있으면 출력

for f in Course.fails:
    print(f"fails: {f}")

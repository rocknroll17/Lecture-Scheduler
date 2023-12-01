import Course
from functools import partial
from TimeTablePackage import CourseDB

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import uic

# lecture_list = []
# DB = CourseDB.CourseDB()
# with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
#     lecture_data = f.readlines()
#     for i in range(len(lecture_data)):
#         DB.add(Course.Course(lecture_data[i].strip().split("$")))
lecture_list = []
DB = CourseDB.CourseDB()
with open('Data/lecture.txt', 'r', encoding='utf-8') as f:
    lecture_data = f.readlines()
    for i in range(len(lecture_data)):
    # for i in range(300):
        course = Course.Course(lecture_data[i].strip().split("$"))
        DB.add(course)
        # Timeblock 파싱 확인용
        # print(f"{course.title[:5]}", end=" ")
        # for t in course.time:
        #     print(t, end=" ")
        # print(f" '{course.time_info_raw_string}'",end=" ")
        # print()

# 처음 모든 강의 목록을 볼 수 있는 창
# -> 왼쪽에 버튼 3개 (강의목록 / 시간표 / 마법사)
# -> 오른쪽에 강의 목록 보여주기
# 검색 조건을 선택하면(condition_search), 이 조건에 맞는 강의들을 강의DB 객체에서 뽑아옴(searched_course), 그리고 여기서 장바구니에 넣을 강의들을 선택해서 뽑음(selected_course)

# 시간표를 볼 수 있는 창 (버튼 클릭)
# -> table로 열은 시간, 행은 요일로 구성해야할듯?
# -> 마법사에서 "꼭"에 있는 애들로 알고리즘(애들이 할거임)을 통해 생성한 새로운 course 리스트가 있을건데 그걸 내가 추가만 하면 됨

# 마법사로 들어가는 창 (버튼 클릭)
# -> 왼쪽부터 순서대로 꼭 / 그냥 / 원하는 수강목록
# -> 아마 table로 만들어야 될 것 같음..?
# -> 수강목록에서 drag drop으로 꼭 / 그냥에 강의 넣기
# -> 강의목록 창에서 뽑은 selected_course를 장바구니 table에 다 넣는다
# -> drag & drop으로 "꼭", "들으면 좋음"에 옮긴다. 이 때 "꼭"과 "들으면 좋음"은 각각 그룹이 형성되어 있는데 이 그룹에 대해 course 리스트를 동적으로 생성해야함(그룹 생길 때마다 만들기)

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class1 = uic.loadUiType("test.ui")[0]
form_class2 = uic.loadUiType("magic.ui")[0]
form_class3 = uic.loadUiType("table.ui")[0]

condition = ["","","","",""]    # 검색 조건
searched_course = []            # 검색 조건에 부합하는 강의 리스트
selected_course = []            # 장바구니에 담을 강의 리스트
Must_group = []                 # 꼭 그룹 (한 그룹 = 강의[], 그룹들의 [])
Must_layout = []                # 꼭 그룹에 추가되는 테이블 모음
Prefer_group = []               # 들으면 좋음 그룹 (한 그룹 = 강의[], 그룹들의 [])
Prefer_layout = []              # 들으면 좋음 그룹에 추가되는 테이블 모음

# 강의 검색 창
class courseSearch(QMainWindow, form_class1) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Search.clicked.connect(self.Button_SearchFunction)  # 강의 검색 버튼
        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 시간표 창으로 이동하는 버튼
        self.Button_Magic.clicked.connect(self.Button_MagicFunction)  # 마법사 창으로 이동하는 버튼

        self.comboBoxCollege.addItems([""] + list(set(course.college for course in DB.course_list)))  # 대학 검색
        self.comboBoxCollege.model().sort(0, Qt.AscendingOrder)
        self.comboBoxCollege.currentIndexChanged.connect(self.comboBoxFunction)

        self.comboBoxDepartment.addItems(list(set(course.department for course in DB.course_list))) # 학과 검색
        self.comboBoxDepartment.model().sort(0, Qt.AscendingOrder)
        self.comboBoxDepartment.currentIndexChanged.connect(self.comboBoxFunction)

        self.titleInput.textChanged.connect(self.printFunction) # 과목명 입력

        self.comboBoxDay.addItems(["", "월", "화", "수", "목", "금", "토"])  # 요일 검색
        self.comboBoxDay.currentIndexChanged.connect(self.comboBoxFunction)

        periods = list(set(int(period) for course in DB.course_list for time in course.time for period in [time.period]))
        periods.sort()
        self.comboBoxPeriod.addItems([""] + [str(period) for period in periods]) # 교시 검색
        self.comboBoxPeriod.currentIndexChanged.connect(self.comboBoxFunction)

        self.Table_Course.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # 조건 넣고 검색버튼 누르면 강의 검색 테이블 만들어짐
    def Button_SearchFunction(self):
        self.Table_Course.setRowCount(0)
        searched_course.clear()

        for course in DB.course_list:
            if (not condition[1] or course.department == condition[1]) and \
                (not condition[2] or course.title == condition[2]) and \
                (not condition[3] or (condition[3] in [time.day for time in course.time])) and \
                (not condition[4] or any(time.day == condition[3] and str(time.period) == condition[4] for time in course.time)):
                searched_course.append(course)

        self.createTable()

    # 강의 검색 테이블 생성
    def createTable(self):
        self.Table_Course.setRowCount(len(searched_course))

        for i in range(0, len(searched_course)):
            button = QPushButton("장바구니")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(lambda _, index=i: self.inBasketButton(index))
            self.Table_Course.setCellWidget(i, 0, button)

            for j in range(1, 13):
                item_text = searched_course[i].total[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Table_Course.setItem(i, j, item)

        self.Table_Course.resizeRowsToContents()
        self.Table_Course.resizeColumnsToContents()

    # 장바구니 테이블 최신화
    def setTable(self):
        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            button = QPushButton("삭제")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.outBasketButton)
            self.Course_Basket.setCellWidget(i, 0, button)

            for j in range(1, 14):
                item_text = selected_course[i].total[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Course_Basket.setItem(i, j, item)

        self.Course_Basket.resizeRowsToContents()
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.Course_Basket.setSelectionMode(QAbstractItemView.SingleSelection)

    # 강의 검색 창에서 장바구니 버튼 누르면 장바구니로 이동
    def inBasketButton(self, row):
        if searched_course[row] not in selected_course:
            selected_course.append(searched_course[row])

            self.Course_Basket.setRowCount(len(selected_course))

            for i in range(len(selected_course)):
                button = QPushButton("삭제")
                button.setStyleSheet("QPushButton {margin-left: 10%; margin-right: 10%;}")
                button.setStyleSheet("background-color: rgb(242, 255, 255);")
                button.setSizePolicy(
                    QSizePolicy.Expanding, QSizePolicy.Expanding
                )
                button.clicked.connect(self.outBasketButton)
                self.Course_Basket.setCellWidget(i, 0, button)

                for j in range(1, 14):
                    item_text = selected_course[i].total[j-1]
                    item = QTableWidgetItem(item_text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.Course_Basket.setItem(i, j, item)

            self.Course_Basket.resizeRowsToContents()
            self.Course_Basket.resizeColumnsToContents()
            self.Course_Basket.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.Course_Basket.setSelectionMode(QAbstractItemView.SingleSelection)
        else:
            print("이미 장바구니에 담았습니다")

        print(selected_course)

    # 장바구니에서 삭제 버튼 누르면 장바구니에서 강의 삭제
    def outBasketButton(self):
        button = self.sender()
        if button:
            index = self.Course_Basket.indexAt(button.pos())
            row = index.row()

            if row != -1:
                del selected_course[row]
                self.Course_Basket.removeRow(row)
                print(selected_course)

    # 시간표 버튼 눌렀을 때
    def Button_ScheduleFunction(self):
        myWindow3.show()
        self.close()

    # 마법사 버튼 눌렀을 때
    def Button_MagicFunction(self):
        myWindow2.setTable()
        myWindow2.show()
        self.close()

    def comboBoxFunction(self):
        sender = self.sender()

        if sender == self.comboBoxCollege:
            selected_data = self.comboBoxCollege.currentText()
            condition[0] = selected_data
        elif sender == self.comboBoxDepartment:
            selected_data = self.comboBoxDepartment.currentText()
            condition[1] = selected_data
        elif sender == self.comboBoxDay:
            selected_data = self.comboBoxDay.currentText()
            condition[3] = selected_data
        elif sender == self.comboBoxPeriod:
            selected_data = self.comboBoxPeriod.currentText()
            condition[4] = selected_data

        print(condition)

    def printFunction(self):
        condition[2] = self.titleInput.text()

# 마법사
class Magic(QMainWindow, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)
        self.Button_Courses.clicked.connect(self.Button_CoursesFunction)
        self.group1Button.clicked.connect(self.g1buttonFunction)
        self.group2Button.clicked.connect(self.g2buttonFunction)

        self.groupMust.setLayout(QVBoxLayout(self.groupMust))
        self.groupPrefer.setLayout(QVBoxLayout(self.groupPrefer))

        self.buttonGroup1 = QGroupBox()
        self.group_layout1 = QHBoxLayout(self.buttonGroup1)

        self.buttonGroup2 = QGroupBox()
        self.group_layout2 = QHBoxLayout(self.buttonGroup2)

    #  장바구니 테이블 생성하는 메소드
    def setTable(self):
        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            button1 = QPushButton("꼭")
            button1.setStyleSheet("background-color: rgb(242, 255, 255);")
            button1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button1.clicked.connect(self.inGroupButton1)

            button2 = QPushButton("들으면 좋음")
            button2.setStyleSheet("background-color: rgb(242, 255, 255);")
            button2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button2.clicked.connect(self.inGroupButton2)

            self.Course_Basket.setCellWidget(i, 0, button1)
            self.Course_Basket.setCellWidget(i, 1, button2)

            for j in range(2, 15):
                item_text = selected_course[i].total[j-2]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Course_Basket.setItem(i, j, item)

        self.Course_Basket.resizeRowsToContents()
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.Course_Basket.setSelectionMode(QAbstractItemView.SingleSelection)

    # 꼭 버튼 눌렀을 때
    def inGroupButton1(self):
        c_button = self.sender()

        if c_button:
            index = self.Course_Basket.indexAt(c_button.pos())
            row = index.row()

            if row != -1:
                course = selected_course[row]
                del selected_course[row]
                self.Course_Basket.removeRow(row)
                print(selected_course)

                for i in range(len(Must_layout)):
                    button = QPushButton(str(i+1))
                    button.clicked.connect(partial(self.addCourse1, i, course))
                    self.group_layout1.addWidget(button)

                self.layout().addWidget(self.buttonGroup1)
                self.buttonGroup1.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.buttonGroup1.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                self.buttonGroup1.show()

    # 들으면 좋음 버튼 눌렀을 때
    def inGroupButton2(self):
        c_button = self.sender()

        if c_button:
            index = self.Course_Basket.indexAt(c_button.pos())
            row = index.row()

            if row != -1:
                course = selected_course[row]
                del selected_course[row]
                self.Course_Basket.removeRow(row)
                print(selected_course)

                for i in range(len(Prefer_layout)):
                    button = QPushButton(str(i+1))
                    button.clicked.connect(partial(self.addCourse2, i, course))
                    self.group_layout2.addWidget(button)

                self.layout().addWidget(self.buttonGroup2)
                self.buttonGroup2.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.buttonGroup2.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                self.buttonGroup2.show()

    # 꼭 그룹의 그룹번호 선택하기
    def addCourse1(self, i, course):
        self.layout().removeWidget(self.buttonGroup1)
        while self.group_layout1.count():
            item = self.group_layout1.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.buttonGroup1.hide()
        widget = Must_layout[i]
        Must_group[i].append(course)
        widget.createTable1(i)

    # 들으면 좋음 그룹의 그룹번호 선택하기
    def addCourse2(self, i, course):
        self.layout().removeWidget(self.buttonGroup2)
        while self.group_layout2.count():
            item = self.group_layout2.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.buttonGroup2.hide()
        widget = Prefer_layout[i]
        Prefer_group[i].append(course)
        widget.createTable2(i)

    # 시간표 버튼 클릭
    def Button_ScheduleFunction(self):
        myWindow3.show()
        self.close()

    # 마법사 버튼 클릭
    def Button_CoursesFunction(self):
        myWindow1.setTable()
        myWindow1.show()
        self.close()

    # 꼭에서 그룹추가
    def g1buttonFunction(self):
        new_group = Table()
        course_group = []
        Must_group.append(course_group)
        Must_layout.append(new_group)
        self.groupMust.layout().addWidget(new_group)

    # 들으면 좋음에서 그룹추가
    def g2buttonFunction(self):
        new_group = Table()
        course_group = []
        Prefer_group.append(course_group)
        Prefer_layout.append(new_group)
        self.groupPrefer.layout().addWidget(new_group)

# 시간표
class timeTable(QMainWindow, form_class3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_1.clicked.connect(self.button1Function) # 마법사 창으로 이동하는 버튼
        self.pushButton_2.clicked.connect(self.button2Function) # 강의 검색 창으로 이동하는 버튼

    def button1Function(self):
        myWindow2.setTable()
        myWindow2.show()
        self.close()

    def button2Function(self):
        myWindow1.setTable()
        myWindow1.show()
        self.close()

# 꼭, 들으면 좋음에서 하나의 그룹을 테이블로 표현함
class Table(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["", '과목명', '과목번호', '담당교수', '강의시간'])

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    # 꼭에서 그룹 생성
    def createTable1(self, index):
        self.setRowCount(len(Must_group[index]))

        for i in range(len(Must_group[index])):
            button = QPushButton("X")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.outGroupButton1)
            self.setCellWidget(i, 0, button)

            for j in range(1, 5):
                item_text = ""
                if j == 1:
                    item_text = Must_group[index][i].total[7]
                elif j == 2:
                    item_text = Must_group[index][i].total[6]
                elif j == 3:
                    item_text = Must_group[index][i].total[9]
                elif j == 4:
                    item_text = Must_group[index][i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)

        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 들으면 좋음에서 그룹 생성
    def createTable2(self, index):
        self.setRowCount(len(Prefer_group[index]))

        for i in range(len(Prefer_group[index])):
            button = QPushButton("X")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.outGroupButton2)
            self.setCellWidget(i, 0, button)

            for j in range(1, 5):
                item_text = ""
                if j == 1:
                    item_text = Prefer_group[index][i].total[7]
                elif j == 2:
                    item_text = Prefer_group[index][i].total[6]
                elif j == 3:
                    item_text = Prefer_group[index][i].total[9]
                elif j == 4:
                    item_text = Prefer_group[index][i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)

        self.resizeRowsToContents()  # 칸 크기 맞추기
        self.resizeColumnsToContents()  # 칸 크기 맞추기

    # 꼭 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton1(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Must_layout.index(self)

            if row != -1:
                selected_course.append(Must_group[idx][row])
                del Must_group[idx][row]
                self.removeRow(row)

        myWindow2.setTable()

    # 들으면 좋음 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton2(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Prefer_layout.index(self)

            if row != -1:
                selected_course.append(Prefer_group[idx][row])
                del Prefer_group[idx][row]
                self.removeRow(row)

        myWindow2.setTable()

class Group(QGroupBox):
    def __init__(self):
        super().__init__()

        self.group_layout = QVBoxLayout()
        self.setLayout(self.group_layout)


if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow1 = courseSearch()
    myWindow2 = Magic()
    myWindow3 = timeTable()

    #프로그램 화면을 보여주는 코드
    myWindow1.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
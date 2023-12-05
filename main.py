import Course

from functools import partial
from itertools import product
import CourseDB
from Basket import Candidate
from Basket import Basket
import FileManager

import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import *
from PyQt5 import uic

from os import environ # 환경변수 조절 용

def suppress_qt_warnings():   # 해상도 별 UI크기 강제 고정
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "2"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

def time_table_maker(must_group, prefer_group, credit_limit):
    must_group = [i for i in must_group.get_groups() if i != []]
    prefer_group = [i for i in prefer_group.get_groups() if i != []]
    possible_table = []#꼭에 관한 가능한 시간표를 담아서 나중에 반환
    prefer_combinations = []#들으면 좋음에 관한 모든 경우의 수를 찾아서 반환
    must_combinations = list(product(*must_group))#가능한 모든 경우의 수를 뽑음

    for combination in product(*prefer_group):
        for mask in product(range(2), repeat=len(prefer_group)):
            result = [item if flag else None for item, flag in zip(combination, mask)]
            prefer_combinations.append(result)
    prefer_combinations = list(set(tuple(filter(lambda x: x is not None, combination)) for combination in prefer_combinations))

    for i in must_combinations:#모든 경우에 수에 대해서
        for j in prefer_combinations:
            if magician(list(i)+list(j), credit_limit):#가능한 시간표인지 판단
                possible_table.append(list(i)+list(j))#가능한 시간표라면 추가
    return possible_table#반환

#후보 하나가 주어지면 이 후보로 시간표가 작성이 가능한지 판단
def magician(time_group, credit_limit):
    day = {'일':0, '월':1, '화':2, '수':3, '목':4, '금':5, '토':6}
    compare_time = [[],[],[],[],[],[],[]]#리스트에 넣고 돌리려면 필요했음.
    credit_sum = 0
    for i in range(len(time_group)):
        credit_sum += float(time_group[i].credit.split("-")[0])
    if credit_sum > credit_limit:
        return False
    for i in range(len(time_group)):#주어진 수업의 갯수만큼
        for j in range(len(time_group[i].time)):#한 수업이 가진 분할 수업의 갯수만큼
            compare_time[day[time_group[i].time[j].day]].extend(list(range(time_group[i].time[j].startmin,time_group[i].time[j].endmin)))
            #이 코드가 startmin과 endmin사이의 모든 분을 만들어서 각 요일 리스트에 추가
    for i in range(len(compare_time)):#일-토까지
        if len(compare_time[i]) != len(set(compare_time[i])):#겹치는 시간이 있는 지 비교
            return False
    return True

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

# UI파일 연결
form_class1 = uic.loadUiType("test.ui")[0]
form_class2 = uic.loadUiType("magic.ui")[0]
form_class3 = uic.loadUiType("table.ui")[0]
form_class4 = uic.loadUiType("create.ui")[0]

####### 전역변수 ########
condition = ["","","","",""]    # 검색 조건
searched_course = []            # 검색 조건에 부합하는 강의 리스트
selected_course = []            # 장바구니에 담을 강의 리스트
Must_group = Candidate()        # 꼭 그룹 (한 그룹 = 강의[], 그룹들의 [])
Must_layout = []                # 꼭 그룹에 추가되는 테이블 모음
Prefer_group = Candidate()      # 들으면 좋음 그룹 (한 그룹 = 강의[], 그룹들의 [])
Prefer_layout = []              # 들으면 좋음 그룹에 추가되는 테이블 모음
selected_schedule = []          # 선택한 최종 시간표 

TABLE_ROW_SIZE = 40 # 테이블 행 크기
SAVE_AND_LOAD_FILE = True

# 파일 로드
fm = FileManager.FileManager()
fm.save_and_load = SAVE_AND_LOAD_FILE
if SAVE_AND_LOAD_FILE:
    is_loaded = fm.load()
    if is_loaded:
        if fm.get("selected_course"):
            selected_course = fm.get("selected_course")
        if fm.get("Must_group"):
            Must_group = fm.get("Must_group")
        if fm.get("Prefer_group"):
            Prefer_group = fm.get("Prefer_group")
        if fm.get("Must_layout"):
            Must_layout = fm.get("Must_layout")
        if fm.get("Prefer_group"):
            Prefer_group = fm.get("Prefer_group")


# 닫을 때 Event 호출하게 하려면 이거 상속받으면 됨
class SaveOnClose:
    def closeEvent(self, event):
        if SAVE_AND_LOAD_FILE:
            fm.add("selected_course", selected_course)
            fm.add("Must_group", Must_group)
            fm.add("Prefer_group", Prefer_group)
            #fm.add("Must_layout", Must_layout)
            #fm.add("Prefer_layout", Prefer_layout)
            fm.save()

# 강의 검색 창
class courseSearch(QMainWindow, form_class1, SaveOnClose) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 버튼
        self.Button_Search.clicked.connect(self.Button_SearchFunction)  # 강의 검색하는 버튼
        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 최종 시간표 창으로 이동하는 버튼
        self.Button_Magic.clicked.connect(self.Button_MagicFunction)  # 마법사 창으로 이동하는 버튼

        # 조건 검색
        # self.comboBoxCollege.addItems([""] + list(set(course.college for course in DB.course_list)))  # 대학 검색
        # self.comboBoxCollege.model().sort(0, Qt.AscendingOrder)
        # self.comboBoxCollege.currentIndexChanged.connect(self.comboBoxFunction)

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
        self.setTable() # 처음 생성할 때에도 장바구니 로드

    # 조건 넣고 검색 버튼 누르면 강의 검색 테이블 만들어짐
    def Button_SearchFunction(self):
        global searched_course
        self.Table_Course.setRowCount(0)
        searched_course.clear()
        searched_course = DB.search(condition)
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
            self.Table_Course.setRowHeight(i, TABLE_ROW_SIZE)

        #self.Table_Course.resizeRowsToContents()
        self.Table_Course.resizeColumnsToContents()
        self.Table_Course.setSelectionMode(QAbstractItemView.NoSelection)

    # 장바구니 테이블 생성(최신화)
    def setTable(self):
        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            button = QPushButton("삭제")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Fixed, QSizePolicy.Fixed
            )
            button.clicked.connect(self.outBasketButton)
            self.Course_Basket.setCellWidget(i, 0, button)

            for j in range(1, 14):
                item_text = selected_course[i].total[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Course_Basket.setItem(i, j, item)

            self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE) # 테이블 행 높이
        #self.Course_Basket.resizeRowsToContents()
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)

    # 강의 검색 창에서 장바구니 버튼 누르면 해당 강의가 장바구니로 이동
    def inBasketButton(self, row):
        if (searched_course[row] not in selected_course and
            all(searched_course[row] not in group for group in Must_group.get_groups()) and
            all(searched_course[row] not in group for group in Prefer_group.get_groups())):

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
                    item_text = selected_course[i].total[j - 1]
                    item = QTableWidgetItem(item_text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.Course_Basket.setItem(i, j, item)
                self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)
            self.Course_Basket.resizeColumnsToContents()
            self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)
        else:
            QMessageBox.information(self, 'note', '이미 장바구니에 담았습니다.')

    # 장바구니에서 삭제 버튼 누르면 해당 강의를 장바구니에서 삭제
    def outBasketButton(self):
        button = self.sender()
        if button:
            index = self.Course_Basket.indexAt(button.pos())
            row = index.row()

            if row != -1:
                del selected_course[row]
                self.Course_Basket.removeRow(row)
                print(selected_course)

    # 시간표 버튼 눌렀을 때 (최종 시간표 보는 창으로 이동)
    def Button_ScheduleFunction(self):
        myWindow3.create_Table()
        myWindow3.show()
        self.close()

    # 마법사 버튼 눌렀을 때 (마법사 창으로 이동)
    def Button_MagicFunction(self):
        myWindow2.setTable()
        # myWindow2.setGroup()
        myWindow2.show()
        self.close()

    # 조건 검색에 활용하는 메소드
    def comboBoxFunction(self):
        sender = self.sender()

        # if sender == self.comboBoxCollege:
        #     selected_data = self.comboBoxCollege.currentText()
        #     condition[0] = selected_data
        if sender == self.comboBoxDepartment:
            selected_data = self.comboBoxDepartment.currentText()
            condition[1] = selected_data
        elif sender == self.comboBoxDay:
            selected_data = self.comboBoxDay.currentText()
            condition[3] = selected_data
        elif sender == self.comboBoxPeriod:
            selected_data = self.comboBoxPeriod.currentText()
            condition[4] = selected_data

    def printFunction(self):
        condition[2] = self.titleInput.text()

# 마법사
class Magic(QMainWindow, form_class2, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 최종 시간표 창으로 이동하는 버튼
        self.Button_Courses.clicked.connect(self.Button_CoursesFunction)    # 강의 검색 창으로 이동하는 버튼
        self.Button_Create.clicked.connect(self.Button_CreateFunction)      # 시간표 생성 창으로 이동하는 버튼
        self.Must_Remove.clicked.connect(self.must_RemoveFunction)          # 꼭 그룹에서 그룹 삭제 버튼
        self.Prefer_Remove.clicked.connect(self.prefer_RemoveFunction)      # 들으면 좋음 그룹에서 그룹 삭제 버튼

        self.groupMust.setLayout(QVBoxLayout(self.groupMust))
        self.groupPrefer.setLayout(QVBoxLayout(self.groupPrefer))

        # 꼭 버튼 누르면 뜨는 버튼 그룹
        self.must_button_group = QGroupBox()
        self.must_group_layout = QFormLayout(self.must_button_group)
        # 들으면 좋음 버튼 누르면 뜨는 버튼 그룹
        self.prefer_button_group = QGroupBox()
        self.prefer_group_layout = QFormLayout(self.prefer_button_group)
        # 꼭에서 그룹삭제 누르면 뜨는 버튼 그룹
        self.delete_must_button_group = QGroupBox()
        self.delete_must_group_layout = QFormLayout(self.delete_must_button_group)
        # 들으면 좋음에서 그룹 삭제 누르면 뜨는 버튼 그룹
        self.delete_prefer_button_group = QGroupBox()
        self.delete_prefer_layout = QFormLayout(self.delete_prefer_button_group)
        self.setTable()
        self.setGroup()
        

    #  장바구니 테이블 생성하는 메소드
    def setTable(self):
        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            must_button = QPushButton("꼭")
            must_button.setStyleSheet("background-color: rgb(242, 255, 255);")
            must_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            must_button.clicked.connect(self.onMustButtonPress)

            prefer_button = QPushButton("들으면 좋음")
            prefer_button.setStyleSheet("background-color: rgb(242, 255, 255);")
            prefer_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            prefer_button.clicked.connect(self.onPreferButtonPress)

            self.Course_Basket.setCellWidget(i, 0, must_button)
            self.Course_Basket.setCellWidget(i, 1, prefer_button)

            for j in range(2, 15):
                item_text = selected_course[i].total[j-2]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Course_Basket.setItem(i, j, item)
            self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)
        #self.Course_Basket.resizeRowsToContents()
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)

    # 기존에 저장된 그룹들 꼭이랑 들으면 좋음에 나타내기(initialize) : 프로그램 아예 재실행했을 때만 이니셜라이즈하게 재작성해야함
    def setGroup(self):
        for course_group in Must_group.get_groups():
            if course_group:
                new_group = Table()
                new_group.createTable_1(course_group)
                # Must_layout.append(new_group)
                self.groupMust.layout().addWidget(new_group)

        for course_group in Prefer_group.get_groups():
            if course_group:
                new_group = Table()
                new_group.createTable_2(course_group)
                # Prefer_layout.append(new_group)
                self.groupPrefer.layout().addWidget(new_group)

    # 장바구니에서 꼭 버튼 눌렀을 때
    def onMustButtonPress(self):
    #def inGroupButton1(self):
        if self.must_button_group.isVisible():
            # 이미 눌렀으면 아무 것도 안함
            return
        self.layout().removeWidget(self.must_button_group)
        while self.must_group_layout.count():
            item = self.must_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        c_button = self.sender()

        if c_button:
            index = self.Course_Basket.indexAt(c_button.pos())
            row = index.row()

            if row != -1:
                course = selected_course[row]
                del selected_course[row]
                self.Course_Basket.removeRow(row)

                for i in range(len(Must_layout)):
                    button = QPushButton('그룹' + str(i+1))
                    button.clicked.connect(partial(self.addCourse1, i, course))
                    self.must_group_layout.addWidget(button)

                button = QPushButton('그룹 추가')
                button.clicked.connect(partial(self.must_AddFunction, course))
                self.must_group_layout.addWidget(button)

                self.layout().addWidget(self.must_button_group)
                self.must_button_group.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.must_button_group.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                self.must_button_group.show()

    # 장바구니에서 들으면 좋음 버튼 눌렀을 때
    def onPreferButtonPress(self):
    #def inGroupButton2(self):
        if self.prefer_button_group.isVisible():
            # 이미 눌렀으면 아무 것도 안함
            return
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
                    button = QPushButton('그룹 ' + str(i+1))
                    button.clicked.connect(partial(self.addCourse2, i, course))
                    self.prefer_group_layout.addWidget(button)

                button = QPushButton('그룹 추가')
                button.clicked.connect(partial(self.prefer_AddFunction, course))
                self.prefer_group_layout.addWidget(button)

                self.layout().addWidget(self.prefer_button_group)
                self.prefer_button_group.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.prefer_button_group.move(c_button_pos.x() - 100, c_button_pos.y() - 150)
                self.prefer_button_group.show()

    # 장바구니에서 꼭 버튼 -> 그룹 번호 선택
    def addCourse1(self, i, course):
        self.layout().removeWidget(self.must_button_group)
        while self.must_group_layout.count():
            item = self.must_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.must_button_group.hide()

        widget = Must_layout[i]
        Must_group.add_course(i, course)
        widget.createTable1(i)

    # 장바구니에서 꼭 버튼 -> 그룹 추가 버튼
    def must_AddFunction(self, course):
        new_group = Table()
        course_group = []
        Must_group.add(course_group)
        Must_layout.append(new_group)
        self.groupMust.layout().addWidget(new_group)

        self.addCourse1(self.groupMust.layout().count() - 1, course)

    # 꼭에서 그룹 삭제 버튼 클릭
    def must_RemoveFunction(self):
        if self.delete_must_button_group.isVisible(): 
            # 이미 눌러져있으면 아무것도 안함
            return
        if Must_layout:
            for i in range(len(Must_layout)):
                button = QPushButton('그룹' + str(i + 1))
                button.clicked.connect(partial(self.removeFunction1, i))
                self.delete_must_group_layout.addWidget(button)

            self.layout().addWidget(self.buttdelete_must_button_grouponGroup3)
            self.delete_must_button_group.adjustSize()
            self.delete_must_button_group.move(650, 500)
            self.delete_must_button_group.show()

    # 꼭에서 그룹 삭제 버튼 -> 그룹 번호 선택
    def removeFunction1(self, i):
        Must_group.delete(i)
        del Must_layout[i]

        item = self.groupMust.layout().takeAt(i)
        widget = item.widget()
        if widget:
            widget.deleteLater()

        self.layout().removeWidget(self.delete_must_button_group)
        while self.delete_must_group_layout.count():
            item = self.delete_must_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.delete_must_button_group.hide()

    # 장바구니에서 들으면 좋음 버튼 -> 그룹 번호 선택
    def addCourse2(self, i, course):
        self.layout().removeWidget(self.prefer_button_group)
        while self.prefer_group_layout.count():
            item = self.prefer_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.prefer_button_group.hide()

        widget = Prefer_layout[i]
        Prefer_group.add_course(i, course)
        widget.createTable2(i)

    # 장바구니에서 들으면 좋음 버튼 -> 그룹 추가 버튼
    def prefer_AddFunction(self, course):
        new_group = Table()
        course_group = []
        Prefer_group.add(course_group)
        Prefer_layout.append(new_group)
        self.groupPrefer.layout().addWidget(new_group)

        self.addCourse2(self.groupPrefer.layout().count() - 1, course)

    # 들으면 좋음에서 그룹 삭제 버튼 클릭
    def prefer_RemoveFunction(self):
        if self.delete_prefer_button_group.isVisible(): 
            # 이미 눌러져있으면 아무것도 안함
            return
        if Prefer_layout:
            for i in range(len(Prefer_layout)):
                button = QPushButton('그룹' + str(i + 1))
                button.clicked.connect(partial(self.removeFunction2, i))
                self.delete_prefer_layout.addWidget(button)

            self.layout().addWidget(self.delete_prefer_button_group)
            self.delete_prefer_button_group.adjustSize()
            self.delete_prefer_button_group.move(1450, 500)
            self.delete_prefer_button_group.show()

    # 들으면 좋음에서 그룹 삭제 버튼 -> 그룹 번호 선택
    def removeFunction2(self, i):
        Prefer_group.delete(i)
        del Prefer_layout[i]

        item = self.groupPrefer.layout().takeAt(i)
        widget = item.widget()
        if widget:
            widget.deleteLater()

        self.layout().removeWidget(self.delete_prefer_button_group)
        while self.delete_prefer_layout.count():
            item = self.delete_prefer_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.delete_prefer_button_group.hide()


    # 시간표 버튼 클릭 (최종 시간표 창으로 이동)
    def Button_ScheduleFunction(self):
        myWindow3.create_Table()
        myWindow3.show()
        self.close()

    # 강의 검색 버튼 클릭 (강의 검색 창으로 이동)
    def Button_CoursesFunction(self):
        myWindow1.setTable()
        myWindow1.show()
        self.close()

    # 시간표 만들기 (시간표 생성 창으로 이동)
    def Button_CreateFunction(self):
        myWindow4.create_Header()
        myWindow4.show()
        self.close()

# 최종 시간표 보여주는 창
class timeTable(QMainWindow, form_class3, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.button_search = QPushButton('강의 검색')            # 강의 검색 창으로 이동하는 버튼
        self.button_magic = QPushButton('마법사')                # 마법사 창으로 이동하는 버튼
        self.button_candidate = QPushButton('시간표 생성')        # 시간표 생성 창으로 이동하는 버튼

        self.button_search.clicked.connect(self.button_Search)
        self.button_magic.clicked.connect(self.button_Magic)
        self.button_candidate.clicked.connect(self.button_Candidate)

    # 최종 시간표를 생성하는 메소드
    def create_Table(self):
        while self.central_layout.count():
            item = self.central_layout.takeAt(0)
            if item.layout():
                item.layout().deleteLater()

        group = QGroupBox()
        group_layout = QHBoxLayout(group)
        group_layout.addWidget(self.button_magic)
        group_layout.addWidget(self.button_search)
        group_layout.addWidget(self.button_candidate)

        table = Schedule_table(selected_schedule)

        self.central_layout.addWidget(group)
        self.central_layout.addWidget(table)

    # 강의 검색 버튼 클릭 (강의 검색 창으로 이동)
    def button_Search(self):
        myWindow1.setTable()
        myWindow1.show()
        self.close()

    # 마법사 버튼 클릭 (마법사 창으로 이동)
    def button_Magic(self):
        myWindow2.setTable()
        # myWindow2.setGroup()
        myWindow2.show()
        self.close()

    # 시간표 생성 버튼 클릭 (시간표 생성 창으로 이동)
    def button_Candidate(self):
        myWindow4.create_Header()
        myWindow4.show()
        self.close()

class CenterAlignDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignCenter
        super().paint(painter, option, index)

# 시간표 후보 생성 창
class ScheduleCandidates(QMainWindow, form_class4, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.time_tables = []
        self.current_table_index = -1

        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    # 시간표 생성 창에서 위쪽 글씨랑 버튼 모음
    def create_Header(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.layout():
                item.layout().deleteLater()

        self.time_tables = time_table_maker(Must_group, Prefer_group, 20)  # 시간표 후보들 임의로 학점 제한 20인데 이거 나중에 설정할 수 있게 바꿔야 함.
        self.time_tables.sort(key=lambda x: len(x), reverse=True)

        header = QGroupBox()
        header_layout = QVBoxLayout(header)

        button_schedule = QPushButton('시간표')
        button_schedule.clicked.connect(self.button_Schedule)
        button_magic = QPushButton('마법사')
        button_magic.clicked.connect(self.button_Magic)
        button_search = QPushButton('강의 검색')
        button_search.clicked.connect(self.button_Search)

        group = QGroupBox()
        group_layout = QHBoxLayout(group)

        group_layout.addWidget(button_schedule)
        group_layout.addWidget(button_search)
        group_layout.addWidget(button_magic)

        header_layout.addWidget(group)
        print(f"possible schedules : {self.time_tables}")
        if len(self.time_tables) > 1:
            label = QLabel(f"결과 보기\n총 {len(self.time_tables)}개의 시간표가 만들어졌습니다.\n마음에 드는 시간표를 저장하세요.")
            label.setAlignment(Qt.AlignCenter)

            button_layout = QHBoxLayout()

            tableBox = QLineEdit('그룹 1');
            tableBox.setAlignment(Qt.AlignCenter)
            tableBox.setReadOnly(True)

            left_button = QPushButton('<')
            left_button.clicked.connect(lambda: self.leftbuttonClicked(tableBox, num_of_table))
            right_button = QPushButton('>')
            right_button.clicked.connect(lambda: self.rightbuttonClicked(tableBox, num_of_table))

            button_layout.addWidget(left_button)
            button_layout.addWidget(tableBox)
            button_layout.addWidget(right_button)

            num_of_table = QComboBox();
            num_of_table.setEditable(True)
            num_of_table.lineEdit().setAlignment(Qt.AlignCenter)
            num_of_table.lineEdit().setReadOnly(True)

            num_of_table.currentIndexChanged.connect(lambda: self.comboBoxFunction(tableBox))
            items = ['']
            for i in range(len(self.time_tables)):
                items.append('그룹 ' + str(i + 1))
            num_of_table.addItems(items)

            header_layout.addWidget(label)
            header_layout.addLayout(button_layout)
            header_layout.addWidget(num_of_table)

            self.main_layout.addWidget(header)
            self.create_Table(0)

        else:
            label = QLabel('만들어진 시간표가 없습니다. 강의를 그룹에 추가하세요')
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            header_layout.addWidget(label)
            self.main_layout.addWidget(header)

    def leftbuttonClicked(self, lineEdit, comboBox):
        i = int(lineEdit.text().split()[-1]) - 1
        num = len(self.time_tables)
        if i == 0:
            i = num - 1
        else:
            i = i - 1
        lineEdit.setText('그룹 ' + str(i+1))
        comboBox.setCurrentIndex(i+1)
        self.create_Table(i)

    def rightbuttonClicked(self, lineEdit, comboBox):
        i = int(lineEdit.text().split()[-1]) - 1
        num = len(self.time_tables)
        if i == num - 1:
            i = 0
        else:
            i = i + 1
        lineEdit.setText('그룹 ' + str(i+1))
        comboBox.setCurrentIndex(i+1)
        self.create_Table(i)

    def comboBoxFunction(self, lineEdit):
        sender = self.sender()
        if sender.currentText() != '':
            i = int(sender.currentText().split()[-1]) - 1
            lineEdit.setText('그룹 ' + str(i + 1))
            self.create_Table(i)

    # 시간표 보여주기 (초기화)
    def create_Table(self, index):
        if self.main_layout.count() > 1:
            current_widget = self.main_layout.itemAt(1)
            if current_widget:
                widget_to_remove = current_widget.widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)
                    widget_to_remove.deleteLater()

        group = QGroupBox()
        group.setLayout(QVBoxLayout(group))

        schedule = Schedule_table(self.time_tables[index])

        button = QPushButton('저장')
        button.clicked.connect(lambda _, idx=index: self.select_Table(idx))

        group.layout().addWidget(schedule)
        group.layout().addWidget(button)

        self.main_layout.addWidget(group)

    # 강의 검색 버튼 클릭 (강의 검색 창으로 이동)
    def button_Search(self):
        myWindow1.setTable()
        myWindow1.show()
        self.close()

    # 마법사 버튼 클릭 (마법사 창으로 이동)
    def button_Magic(self):
        myWindow2.setTable()
        # myWindow2.setGroup()
        myWindow2.show()
        self.close()

    # 시간표 버튼 클릭 (시간표 창으로 이동)
    def button_Schedule(self):
        myWindow3.create_Table()
        myWindow3.show()
        self.close()

    # 시간표 후보 중 최종 시간표를 저장
    def select_Table(self, index):
        selected_schedule.clear()
        for course in self.time_tables[index]:
            selected_schedule.append(course)

# 시간표 테이블 1개에 대한 class
class Schedule_table(QTableWidget):
    def __init__(self, courses):
        super().__init__()
        self.setColumnCount(8)
        self.setRowCount(64)
        self.setHorizontalHeaderLabels(
            ['교시', '시간', '월요일(Mon)', '화요일(Tue)', '수요일(Wed)', '목요일(Thu)', '금요일(Fri)', '토요일(Sat)'])
        h = [''] * 64
        self.setVerticalHeaderLabels(h)

        for row in range(0, 64, 4):
            self.setSpan(row, 0, 4, 1)

        count = 0
        for row in range(0, 64, 4):
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item)
            count += 1

        time_format = "{:02d}:{:02d}"
        count_hours = 8
        count_minutes = 0

        for row in range(0, 64):
            time_item = QTableWidgetItem(time_format.format(count_hours, count_minutes))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, time_item)
            count_minutes += 15
            if count_minutes == 60:
                count_minutes = 0
                count_hours += 1
            if count_hours == 24:
                count_hours = 0

        for course in courses:
            for time_block in course.time:
                day_column = self.get_day_index(time_block.day)
                start_row = self.get_time_index(time_block.start_time)
                end_row = self.get_time_index(time_block.end_time)

                for row in range(start_row, end_row - 1):
                    hours, minutes = map(int, time_block.course_time.split(':'))
                    total_minutes = hours * 60 + minutes
                    span_size = total_minutes // 15
                    self.setSpan(start_row, day_column, span_size, 1)

                    parts = course.time_info_raw_string.split('/')
                    if len(parts) >= 3:
                        result = '/'.join(parts[2:])
                    elif len(parts) == 2:
                        result = parts[1]
                    else:
                        result = course.time_info_raw_string

                    info_text = f"{course.title}\n{course.instructor}\n{result}"
                    item = QTableWidgetItem(info_text)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, day_column, item)

        fixed_row_height = 15
        fixed_column_width = 300
        for row in range(self.rowCount()):
            self.setRowHeight(row, fixed_row_height)
        for column in range(self.columnCount()):
            if column == 0 or column == 1:
                self.setColumnWidth(column, 50)
            else:
                self.setColumnWidth(column, fixed_column_width)

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def get_day_index(self, day):
        day_mapping = {'월': 2, '화': 3, '수': 4, '목': 5, '금': 6, '토': 7}
        return day_mapping.get(day)

    def get_time_index(self, time_str):
        hours, minutes = map(int, time_str.split(':'))
        return (hours - 8) * 4 + (1 if minutes == 15 else 0)

# 꼭, 들으면 좋음에서 추가되는 하나의 그룹을 테이블로 표현함
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
        #self.setRowCount(len(Must_group[index]))
        self.setRowCount(len(Must_group.get_groups()[index]))

        #for i in range(len(Must_group[index])):
        for i in range(len(Must_group.get_groups()[index])):
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
                    #item_text = Must_group[index][i].total[7]
                    item_text = Must_group.get_group(index)[i].total[7]
                elif j == 2:
                    #item_text = Must_group[index][i].total[6]
                    item_text = Must_group.get_group(index)[i].total[6]
                elif j == 3:
                    #item_text = Must_group[index][i].total[9]
                    item_text = Must_group.get_group(index)[i].total[9]
                elif j == 4:
                    #item_text = Must_group[index][i].total[11]
                    item_text = Must_group.get_group(index)[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        #self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 꼭에서 그룹 생성하는건데 얘는 창을 끄고 키거나 했을 때 기존에 저장된 그룹 복원 용도
    def createTable_1(self, courses):
        self.setRowCount(len(courses))

        for i in range(len(courses)):
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
                    item_text = courses[i].total[7]
                elif j == 2:
                    item_text = courses[i].total[6]
                elif j == 3:
                    item_text = courses[i].total[9]
                elif j == 4:
                    item_text = courses[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        #self.resizeRowsToContents()
        self.resizeColumnsToContents()


    # 들으면 좋음에서 그룹 생성
    def createTable2(self, index):
        #self.setRowCount(len(Prefer_group[index]))
        self.setRowCount(len(Prefer_group.get_group(index)))


        #for i in range(len(Prefer_group[index])):
        for i in range(len(Prefer_group.get_group(index))):
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
                    #item_text = Prefer_group[index][i].total[7]
                    item_text = Prefer_group.get_group(index)[i].total[7]
                elif j == 2:
                    #item_text = Prefer_group[index][i].total[6]
                    item_text = Prefer_group.get_group(index)[i].total[6]
                elif j == 3:
                    #item_text = Prefer_group[index][i].total[9]
                    item_text = Prefer_group.get_group(index)[i].total[9]
                elif j == 4:
                    #item_text = Prefer_group[index][i].total[11]
                    item_text = Prefer_group.get_group(index)[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        #self.resizeRowsToContents()  # 칸 크기 맞추기
        self.resizeColumnsToContents()  # 칸 크기 맞추기

    # 들으면 좋음에서 그룹 생성하는건데 얘는 창을 끄고 키거나 했을 때 기존에 저장된 그룹 복원 용도
    def createTable_2(self, courses):
        self.setRowCount(len(courses))

        for i in range(len(courses)):
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
                    item_text = courses[i].total[7]
                elif j == 2:
                    item_text = courses[i].total[6]
                elif j == 3:
                    item_text = courses[i].total[9]
                elif j == 4:
                    item_text = courses[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        #self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 꼭 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton1(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Must_layout.index(self) # 오류

            if row != -1:
                #selected_course.append(Must_group[idx][row])
                selected_course.append(Must_group.get_group(idx)[row])
                #del Must_group[idx][row]
                del Must_group.get_group(idx)[row]
                self.removeRow(row)

        myWindow2.setTable()

    # 들으면 좋음 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton2(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Prefer_layout.index(self) # 오류

            if row != -1:
                #selected_course.append(Prefer_group[idx][row])
                selected_course.append(Prefer_group.get_group(idx)[row])
                del Prefer_group.get_group(idx)[row]
                self.removeRow(row)

        myWindow2.setTable()

if __name__ == "__main__" :
    suppress_qt_warnings()
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    for s in set([c.department for c in DB.course_list]):
        print(s)
    #각 창의 인스턴스 생성
    myWindow1 = courseSearch()
    myWindow2 = Magic()
    myWindow3 = timeTable()
    myWindow4 = ScheduleCandidates()

    #프로그램 화면을 보여주는 코드
    myWindow1.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
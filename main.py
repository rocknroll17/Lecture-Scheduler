import Course
from functools import partial
from itertools import product
import CourseDB
import FileManager

import sys

from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import *
from PyQt5 import uic

from os import environ       # environ 를 import 해야 아래 suppress_qt_warnings 가 정상 동작하니다

def suppress_qt_warnings():   # 해상도별 글자크기 강제 고정하는 함수
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

def time_table_maker(must_group, prefer_group,credit_limit):
    must_group = [i for i in must_group if i != []]
    prefer_group = [i for i in prefer_group if i != []]
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

# 처음 모든 강의 목록을 볼 수 있는 창
# -> 왼쪽에 버튼 3개 (강의목록 / 시간표 / 마법사)
# -> 오른쪽에 강의 목록 보여주기
# 검색 조건을 선택하면(condition_search), 이 조건에 맞는 강의들을 강의DB 객체에서 뽑아옴(searched_course), 그리고 여기서 장바구니에 넣을 강의들을 선택해서 뽑음(selected_course)

# 시간표를 볼 수 있는 창
# 마법사로 들어가는 창 (버튼 클릭)

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class1 = uic.loadUiType("test.ui")[0]
form_class2 = uic.loadUiType("magic.ui")[0]
form_class3 = uic.loadUiType("table.ui")[0]
form_class4 = uic.loadUiType("create.ui")[0]

####### 전역변수 ########
condition = ["","","","",""]    # 검색 조건
searched_course = []            # 검색 조건에 부합하는 강의 리스트
selected_course = []            # 장바구니에 담을 강의 리스트
Must_group = []                 # 꼭 그룹 (한 그룹 = 강의[], 그룹들의 [])
Must_layout = []                # 꼭 그룹에 추가되는 테이블 모음
Prefer_group = []               # 들으면 좋음 그룹 (한 그룹 = 강의[], 그룹들의 [])
Prefer_layout = []              # 들으면 좋음 그룹에 추가되는 테이블 모음

TABLE_ROW_SIZE = 50 # 테이블 행 크기

# 파일 로드
fm = FileManager.FileManager()
is_loaded = fm.load()
if is_loaded:
    if fm.basket: # 나중에 list를 Basket으로 바꿔야댐
        selected_course = fm.basket
    if fm.must_group:
        Must_group = fm.must_group
    if fm.prefer_group:
        Prefer_group = fm.prefer_group




# 닫을 때 Event 호출하게 하려면 이거 상속받으면 됨
class SaveOnClose:
    def closeEvent(self, event):
        fm.save(selected_course, Must_group, Prefer_group)
        '''
        # 종료 창 출력
        quit_msg = "종료하시겠습니까?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        '''

# 강의 검색 창
class courseSearch(QMainWindow, form_class1, SaveOnClose) :
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
        self.setTable() # 처음 생성할 때에도 장바구니 로드

    # 조건 넣고 검색버튼 누르면 강의 검색 테이블 만들어짐
    def Button_SearchFunction(self):
        global searched_course
        self.Table_Course.setRowCount(0)
        searched_course.clear()

        '''
        for course in DB.course_list:
            if (not condition[1] or course.department == condition[1]) and \
                (not condition[2] or course.title == condition[2]) and \
                (not condition[3] or (condition[3] in [time.day for time in course.time])) and \
                (not condition[4] or any(time.day == condition[3] and str(time.period) == condition[4] for time in course.time)):
                searched_course.append(course)
        '''
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

    # 장바구니 테이블 최신화
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
                self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)
            #self.Course_Basket.resizeRowsToContents()
            self.Course_Basket.resizeColumnsToContents()
            self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)
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
class Magic(QMainWindow, form_class2, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 최종 시간표 확인
        self.Button_Courses.clicked.connect(self.Button_CoursesFunction)    # 강의 검색 창
        self.Button_Create.clicked.connect(self.Button_CreateFunction)      # 시간표 생성(마법사)
        self.group1Button.clicked.connect(self.g1buttonFunction)
        self.group2Button.clicked.connect(self.g2buttonFunction)

        self.groupMust.setLayout(QVBoxLayout(self.groupMust))
        self.groupPrefer.setLayout(QVBoxLayout(self.groupPrefer))

        self.group1 = QGroupBox()
        self.g_layout1 = QVBoxLayout(self.group1)

        self.group2 = QGroupBox()
        self.g_layout2 = QVBoxLayout(self.group2)

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
            self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)
        #self.Course_Basket.resizeRowsToContents()
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)

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

                label = QLabel('그룹 번호 선택')
                comboBox = QComboBox()
                items = ['']
                for i in range(len(Must_layout)):
                    items.append('그룹' + ' ' + str(i+1))
                comboBox.addItems(items)
                comboBox.model().sort(0, Qt.AscendingOrder)
                comboBox.currentIndexChanged.connect(partial(self.comboBoxFunction1, course))

                self.g_layout1.addWidget(label)
                self.g_layout1.addWidget(comboBox)

                self.layout().addWidget(self.group1)
                self.group1.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.group1.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                self.group1.show()

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

                label = QLabel('그룹 번호 선택')
                comboBox = QComboBox()
                items = ['']
                for i in range(len(Prefer_layout)):
                    items.append('그룹' + ' ' + str(i + 1))
                comboBox.addItems(items)
                comboBox.model().sort(0, Qt.AscendingOrder)
                comboBox.currentIndexChanged.connect(partial(self.comboBoxFunction2, course))

                self.g_layout2.addWidget(label)
                self.g_layout2.addWidget(comboBox)

                self.layout().addWidget(self.group2)
                self.group2.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                self.group2.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                self.group2.show()

    # 꼭 그룹의 그룹번호 선택하기
    def comboBoxFunction1(self, course):
        sender = self.sender()
        words = sender.currentText().split()
        for word in words:
            if word.isdigit():
                i = int(word) - 1
                self.addCourse1(i, course)
                break

    def addCourse1(self, i, course):
        self.layout().removeWidget(self.group1)
        while self.g_layout1.count():
            item = self.g_layout1.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.group1.hide()
        widget = Must_layout[i]
        Must_group[i].append(course)
        widget.createTable1(i)

    # 들으면 좋음 그룹의 그룹번호 선택하기
    def comboBoxFunction2(self, course):
        sender = self.sender()
        words = sender.currentText().split()
        for word in words:
            if word.isdigit():
                i = int(word) - 1
                self.addCourse2(i, course)
                break

    def addCourse2(self, i, course):
        self.layout().removeWidget(self.group2)
        while self.g_layout2.count():
            item = self.g_layout2.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.group2.hide()
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

    # 시간표 만들기
    def Button_CreateFunction(self):
        myWindow4.show()

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

# 최종 시간표 보여주는 창
class timeTable(QMainWindow, form_class3, SaveOnClose):
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

# 시간표
class Schedule_table(QTableWidget):
    def __init__(self, courses):
        super().__init__()
        self.setColumnCount(8)
        self.setRowCount(32)
        self.setHorizontalHeaderLabels(['교시', '시간', '월요일(Mon)', '화요일(Tue)', '수요일(Wed)', '목요일(Thu)', '금요일(Fri)', '토요일(Sat)'])
        h = [''] * 32
        self.setVerticalHeaderLabels(h)

        for row in range(0, 32, 2):
            self.setSpan(row, 0, 2, 1)

        count = 0
        for row in range(0, 32, 2):
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item)
            count += 1

        time_format = "{:02d}:{:02d}"
        count_hours = 8
        count_minutes = 0
        for row in range(0, 32):
            time_item = QTableWidgetItem(time_format.format(count_hours, count_minutes))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, time_item)
            count_minutes += 30
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
                    if time_block.course_time == '01:00':
                        self.setSpan(row, day_column, 2, 1)
                    elif time_block.course_time == '01:30':
                        self.setSpan(row, day_column, 3, 1)
                    elif time_block.course_time == '02:00':
                        self.setSpan(row, day_column, 4, 1)

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

        fixed_row_height = 30
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
        return (hours - 8) * 2 + (1 if minutes == 30 else 0)

# 시간표 후보 생성 창
class Candidate(QMainWindow, form_class4, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.time_tables = []

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_layout = QHBoxLayout(self.central_widget)

        self.pushButton.clicked.connect(self.buttonFunction)    # 실험용
        self.central_layout.addWidget(self.pushButton)

    def select_Table(self):
        print('선택됨')

    def buttonFunction(self):

        self.time_tables = time_table_maker(Must_group, Prefer_group, 20)  # 시간표 후보들 임의로 학점 제한 20인데 이거 나중에 설정할 수 있게 바꿔야 함.
        print('꼭 그룹 리스트 : ')
        print(Must_group)
        print('들으면 좋음 그룹 리스트 : ')
        print(Prefer_group)
        print('시간표 리스트 : ')
        print(self.time_tables)

        for i in range(len(self.time_tables)):
            group = QGroupBox()
            group.setLayout(QVBoxLayout(group))

            schedule = Schedule_table(self.time_tables[i])
            button = QPushButton('선택')
            button.clicked.connect(self.select_Table)

            group.layout().addWidget(schedule)
            group.layout().addWidget(button)

            self.central_layout.addWidget(group)


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

if __name__ == "__main__" :
    suppress_qt_warnings()
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow1 = courseSearch()
    myWindow2 = Magic()
    myWindow3 = timeTable()
    myWindow4 = Candidate()

    #프로그램 화면을 보여주는 코드
    myWindow1.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
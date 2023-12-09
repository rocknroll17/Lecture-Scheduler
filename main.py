from ScheduleManager import ScheduleManager
import CourseDB
from Candidate import Candidate
from Candidate import CourseGroup
from Schedule import Schedule
import FileManager
import random

from functools import partial

import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QCursor
from PyQt5.QtCore import Qt, QTime, QTimer, QPropertyAnimation
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QColor

from os import environ  # 환경변수 조절 용
import MainStyleSheet

# UI파일 연결
form_class1 = uic.loadUiType("test.ui")[0]
form_class2 = uic.loadUiType("magic.ui")[0]
form_class3 = uic.loadUiType("table.ui")[0]
form_class4 = uic.loadUiType("create.ui")[0]

####### 전역변수 ########
condition = ["", "", "", "", ""]  # 검색 조건
searched_course = CourseGroup(filter_by_id=False)  # 검색 조건에 부합하는 강의 리스트 -> 과목번호 중복돼도 받아들임
selected_course = CourseGroup()  # 장바구니에 담을 강의 리스트
Must_group = Candidate()  # 꼭 그룹 (그룹 하나: Course 객체의 리스트, 그룹들의 리스트)
Must_layout = []  # 꼭 그룹에 추가되는 테이블 모음 (Table 객체의 리스트)
Prefer_group = Candidate()  # 들으면 좋음 그룹 (그룹 하나 = Course 객체의 리스트, 그룹들의 리스트)
Prefer_layout = []  # 들으면 좋음 그룹에 추가되는 테이블 모음
selected_schedule = Schedule()  # 선택한 최종 시간표
tot_credits = 50  # 최대 학점

DB = CourseDB.CourseDB('Data/lecture.txt')

TABLE_ROW_SIZE = 40  # 테이블 행 크기
TABLE_COL_SIZE_COLLEGE = 80  # 대학 열 너비
TABLE_COL_SIZE_DEPARTMENT = 100  # 학과 열 너비
TABLE_COL_SIZE_TITLE = 180  # 과목명 열 너비
SAVE_AND_LOAD_FILE = True  # 저장 여부
width = 0  # 해상도
height = 0  # 해상도

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
        if fm.get("selected_schedule"):
            selected_schedule = fm.get("selected_schedule")


class Notification(QWidget):
    def __init__(self, message, pos_x, pos_y):
        super(Notification, self).__init__()

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.message_label)
        self.setLayout(layout)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setDuration(1500)  # 1500 milliseconds (1.5 seconds)

        # 페이드 아웃 시간까지 딜레이
        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.start_fade_out)

        # 창의 이동에 따라서 알림 위치 지정
        self.setGeometry(pos_x+630, pos_y+420, 200, 50)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200); color: white;")

    def show_notification(self):
        self.show()
        self.delay_timer.start(300)  # 300밀리초 딜레이

    def start_fade_out(self):
        self.delay_timer.stop()
        self.fade_animation.start() #페이드 아웃


# 창 닫을 때 Event 호출하게 해주는 클래스 -> 창 닫힐때 저장하도록 만듬
# 닫을 때 정보 저장하고 싶은 창은 이 클래스 상속받으면 됨
class SaveOnClose:
    def closeEvent(self, event):
        # QMainWindow 클래스는 창 닫을 때 closeEvent를 호출하도록 짜여있다.
        # -> closeEvent 재정의하면 창 닫힐 때 원하는 작업 실행 가능.  여기선 파일 저장하도록 재정의함
        if SAVE_AND_LOAD_FILE:
            fm.add("selected_course", selected_course)
            musts = Candidate()
            musts.set_groups([m for m in Must_group.get_groups() if m])  # 빈 리스트 제거
            fm.add("Must_group", musts)
            prefers = Candidate()
            prefers.set_groups([p for p in Prefer_group.get_groups() if p])  # 빈 리스트 제거
            fm.add("Prefer_group", prefers)
            fm.add("selected_schedule", selected_schedule)
            fm.save()


# 강의 검색 창
class courseSearch(QMainWindow, form_class1, SaveOnClose):
    # 세가지 클래스 상속. QMainWindow : 윈도우창 / form_class1 : ui파일 / SaveOnClose : 닫을 때 저장
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.college = ""  # 대학 검색 조건
        self.setWindowTitle("강의 검색")
        # 버튼
        self.Button_Search.clicked.connect(self.Button_SearchFunction)  # 강의 검색하는 버튼
        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 최종 시간표 창으로 이동하는 버튼
        self.Button_Magic.clicked.connect(self.Button_MagicFunction)  # 마법사 창으로 이동하는 버튼

        # 조건 검색
        self.comboBoxCollege.addItems([""] + list(set(course.college for course in DB.course_list)))  # 대학 검색
        self.comboBoxCollege.model().sort(0, Qt.AscendingOrder)
        self.comboBoxCollege.currentIndexChanged.connect(self.comboBoxFunction)
        self.comboBoxCollege.setCurrentIndex(0)  # 대학(전체)
        self.college = self.comboBoxCollege.currentText()

        self.comboBoxDepartment.addItems(
            list(set(course.department for course in DB.course_list if course.college == self.college)))  # 학과 검색
        self.comboBoxDepartment.model().sort(0, Qt.AscendingOrder)
        self.comboBoxDepartment.currentIndexChanged.connect(self.comboBoxFunction)

        self.titleInput.textChanged.connect(self.printFunction)  # 과목명 입력

        self.comboBoxDay.addItems(["", "월", "화", "수", "목", "금", "토"])  # 요일 검색
        self.comboBoxDay.currentIndexChanged.connect(self.comboBoxFunction)

        periods = list(
            set(int(period) for course in DB.course_list for time in course.time for period in [time.period]))
        periods.sort()
        self.comboBoxPeriod.addItems([""] + [str(period) for period in periods])  # 교시 검색
        self.comboBoxPeriod.currentIndexChanged.connect(self.comboBoxFunction)

        self.Table_Course.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setTable()  # 처음 생성할 때에도 장바구니 로드

    def keyPressEvent(self, qKeyEvent):  # 키보드 이벤트 핸들러
        if qKeyEvent.key() == Qt.Key_Return:
            self.Button_SearchFunction()

            # 조건 넣고 검색 버튼 누르면 강의 검색 테이블 만들어짐

    def Button_SearchFunction(self):
        global searched_course
        # print(condition)
        self.Table_Course.setRowCount(0)
        searched_course.clear()
        # DB에서 검색 & 반환한 리스트를 CourseGroup 객체로 변환해서 저장
        searched_course = CourseGroup(DB.search(condition), filter_by_id=False) 
        self.createTable()

    # 강의 검색 테이블 생성
    def createTable(self):
        # 테이블 수직헤더 너비 고정
        self.Table_Course.verticalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.Table_Course.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.Table_Course.verticalHeader().setFixedWidth(30)

        self.Table_Course.setRowCount(len(searched_course))

        for i in range(0, len(searched_course)):
            button = QPushButton("담기")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(lambda _, index=i: self.inBasketButton(index))
            self.Table_Course.setCellWidget(i, 0, button)

            # 인덱스 : 버튼 0 대학 1 개설학과 2 과목명 8 담당교수 10 강의시간 12 비고 13
            for j in range(1, 14):
                item_text = searched_course[i].total[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Table_Course.setItem(i, j, item)
            self.Table_Course.setRowHeight(i, TABLE_ROW_SIZE)
        self.Table_Course.resizeColumnsToContents()
        self.Table_Course.setColumnWidth(1, TABLE_COL_SIZE_COLLEGE)
        self.Table_Course.setColumnWidth(2, TABLE_COL_SIZE_DEPARTMENT)
        self.Table_Course.setColumnWidth(8, TABLE_COL_SIZE_TITLE)
        self.Table_Course.setSelectionMode(QAbstractItemView.NoSelection)

    # 장바구니 테이블 생성(최신화)
    def setTable(self):
        # 테이블 수직헤더 너비 고정
        self.Course_Basket.verticalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.Course_Basket.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.Course_Basket.verticalHeader().setFixedWidth(30)

        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            button = QPushButton("삭제")
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

            self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)  # 테이블 행 높이
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setColumnWidth(1, TABLE_COL_SIZE_COLLEGE)
        self.Course_Basket.setColumnWidth(2, TABLE_COL_SIZE_DEPARTMENT)
        self.Course_Basket.setColumnWidth(8, TABLE_COL_SIZE_TITLE)
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
            self.Course_Basket.setColumnWidth(1, TABLE_COL_SIZE_COLLEGE)
            self.Course_Basket.setColumnWidth(2, TABLE_COL_SIZE_DEPARTMENT)
            self.Course_Basket.setColumnWidth(8, TABLE_COL_SIZE_TITLE)
            self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)
        else:
            notification = Notification("이미 장바구니에 담았습니다.", self.pos().x(), self.pos().y()) #현재 창의 위치
            notification.show_notification()

    # 장바구니에서 삭제 버튼 누르면 해당 강의를 장바구니에서 삭제
    def outBasketButton(self):
        button = self.sender()
        if button:
            index = self.Course_Basket.indexAt(button.pos())
            row = index.row()

            if row != -1:
                #del selected_course[row]
                selected_course.delete(row)
                self.Course_Basket.removeRow(row)
                # print(selected_course)

    # 시간표 버튼 눌렀을 때 (최종 시간표 보는 창으로 이동)
    def Button_ScheduleFunction(self):
        myWindow3.create_Table()
        myWindow3.showMaximized()
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

        if sender == self.comboBoxCollege:
            selected_data = self.comboBoxCollege.currentText()
            condition[0] = selected_data
            self.comboBoxDepartment.clear()
            self.comboBoxDepartment.addItems(
                list(set(course.department for course in DB.course_list if course.college == selected_data)))  # 학과 검색
            self.comboBoxDepartment.model().sort(0, Qt.AscendingOrder)
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
        self.setWindowTitle("시간표 마법사")
        self.row = -1

        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 최종 시간표 창으로 이동하는 버튼
        self.Button_Courses.clicked.connect(self.Button_CoursesFunction)  # 강의 검색 창으로 이동하는 버튼
        self.Button_Create.clicked.connect(self.Button_CreateFunction)  # 시간표 생성 창으로 이동하는 버튼
        self.Must_Remove.clicked.connect(self.must_RemoveFunction)  # 꼭 그룹에서 그룹 삭제 버튼
        self.Prefer_Remove.clicked.connect(self.prefer_RemoveFunction)  # 들으면 좋음 그룹에서 그룹 삭제 버튼
        self.credit_edit.textChanged.connect(self.text_changed)  # 최대 학점 입력하는 칸

        self.must_scroll = QWidget(self.groupMust)
        self.must_scroll_layout = QVBoxLayout(self.must_scroll)

        self.prefer_scroll = QWidget(self.groupPrefer)
        self.prefer_scroll_layout = QVBoxLayout(self.prefer_scroll)

        # 꼭 버튼 누르면 뜨는 버튼 그룹
        self.must_button_group = QGroupBox()
        self.must_group_layout = QHBoxLayout(self.must_button_group)
        # 들으면 좋음 버튼 누르면 뜨는 버튼 그룹
        self.prefer_button_group = QGroupBox()
        self.prefer_group_layout = QHBoxLayout(self.prefer_button_group)
        # 꼭에서 그룹삭제 누르면 뜨는 버튼 그룹
        self.delete_must_button_group = QGroupBox()
        self.delete_must_group_layout = QFormLayout(self.delete_must_button_group)
        # 들으면 좋음에서 그룹 삭제 누르면 뜨는 버튼 그룹
        self.delete_prefer_button_group = QGroupBox()
        self.delete_prefer_group_layout = QFormLayout(self.delete_prefer_button_group)
        self.initializeMustLayout()
        self.initializePreferLayout()
        self.setTable()

    def text_changed(self):
        text = self.credit_edit.text()
        if text != "":
            global tot_credits
            tot_credits = int(text)

    #  장바구니 테이블 생성하는 메소드
    def setTable(self):
        # 테이블 수직 헤더 너비 고정
        self.Course_Basket.verticalHeader().setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.Course_Basket.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.Course_Basket.verticalHeader().setFixedWidth(30)
        self.Course_Basket.setRowCount(len(selected_course))

        for i in range(len(selected_course)):
            must_button = QPushButton("필수 강의")
            must_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            must_button.clicked.connect(self.onMustButtonPress)

            prefer_button = QPushButton("희망 강의")
            prefer_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            prefer_button.clicked.connect(self.onPreferButtonPress)

            self.Course_Basket.setCellWidget(i, 0, must_button)
            self.Course_Basket.setCellWidget(i, 1, prefer_button)

            for j in range(2, 15):
                item_text = selected_course[i].total[j - 2]
                item = QTableWidgetItem(item_text)

                item.setTextAlignment(Qt.AlignCenter)
                self.Course_Basket.setItem(i, j, item)
            self.Course_Basket.setRowHeight(i, TABLE_ROW_SIZE)
        self.Course_Basket.resizeColumnsToContents()
        self.Course_Basket.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Course_Basket.setSelectionMode(QAbstractItemView.NoSelection)

    # 저장된 Must_group이 있는 경우, 이를 바탕으로 관련 변수 초기화 & 화면에 그림
    def initializeMustLayout(self):
        global Must_layout
        Must_layout = []

        # 꼭 그룹의 각 강의그룹에 대해서
        for i in range(len(Must_group.get_groups())):
            # Table 객체를 만들고
            table = Table()
            table.createTable1(i)
            Must_layout.append(table)  # Must_layout : 전역변수
            # 맨 앞에 몇 번째 그룹인지 표시해주고
            groupbox = QGroupBox()
            groupbox.setStyleSheet("border: 0px;")
            box_layout = QHBoxLayout(groupbox)
            label = QLabel('그룹' + str(self.must_scroll_layout.count() + 1))

            box_layout.addWidget(label, alignment=Qt.AlignLeft)
            box_layout.addWidget(table)
            # 레이아웃에 추가
            groupbox.setMinimumHeight(200)
            self.must_scroll_layout.addWidget(groupbox)
            self.groupMust.setWidget(self.must_scroll)

    # 저장된 Prefer_group이 있는 경우, 이를 바탕으로 관련 변수 초기화 & 화면에 그림
    def initializePreferLayout(self):
        global Prefer_layout
        Prefer_layout = []
        # 들으면 좋음 그룹의 각 강의그룹에 대해서
        for i in range(len(Prefer_group.get_groups())):
            # Table 객체를 만들고
            table = Table()
            table.createTable2(i)
            Prefer_layout.append(table)
            # 맨 앞에 몇 번째 그룹인지 표시해주고
            groupbox = QGroupBox()
            groupbox.setStyleSheet("border: 0px;")
            box_layout = QHBoxLayout(groupbox)
            label = QLabel(str(self.prefer_scroll_layout.count() + 1) + '순위')

            box_layout.addWidget(label, alignment=Qt.AlignLeft)
            box_layout.addWidget(table)
            # 레이아웃에 추가
            groupbox.setMinimumHeight(200)
            self.prefer_scroll_layout.addWidget(groupbox)
            self.groupPrefer.setWidget(self.prefer_scroll)

    # 장바구니에서 꼭 버튼 눌렀을 때
    def onMustButtonPress(self):
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        # 원래 들어가있었던 버튼 그룹 삭제  (ex) ['추가하지 않음','그룹 1','그룹 추가'])
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
            self.row = index.row()
            # print(self.row)

            if self.row != -1:
                course = selected_course[self.row]

                xButton = QPushButton('추가 안 함')
                xButton.clicked.connect(self.must_removeGroup1)
                self.must_group_layout.addWidget(xButton)
                for i in range(len(Must_layout)):
                    button = QPushButton('그룹' + str(i + 1))
                    button.clicked.connect(partial(self.addCourse1, i, course))
                    self.must_group_layout.addWidget(button)

                button = QPushButton('그룹 추가')
                button.clicked.connect(partial(self.must_AddFunction, course))
                self.must_group_layout.addWidget(button)

                self.layout().addWidget(self.must_button_group)
                self.must_button_group.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                # self.must_button_group.move(c_button_pos.x() - 50, c_button_pos.y() - 150)
                # 커서 위치에 뜨도록 한다
                self.must_button_group.move(QCursor.pos().x() - self.pos().x(), QCursor.pos().y() - self.pos().y() - 59)
                #동적으로 생성되는 객체가 화면과 마우스의 움직임을 따라가기 위한 코드
                self.must_button_group.show()

    # 꼭 버튼 눌렀을 때 나오는 그룹리스트 버튼
    def must_removeGroup1(self):
        self.must_button_group.hide()

    # 장바구니에서 들으면 좋음 버튼 눌렀을 때
    def onPreferButtonPress(self):
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        self.layout().removeWidget(self.prefer_button_group)
        while self.prefer_group_layout.count():
            item = self.prefer_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        c_button = self.sender()

        if c_button:
            index = self.Course_Basket.indexAt(c_button.pos())
            self.row = index.row()

            if self.row != -1:
                course = selected_course[self.row]

                xButton = QPushButton('추가 안 함')
                xButton.clicked.connect(self.prefer_removeGroup1)
                self.prefer_group_layout.addWidget(xButton)
                for i in range(len(Prefer_layout)):
                    button = QPushButton(str(i + 1) + '순위')
                    button.clicked.connect(partial(self.addCourse2, i, course))
                    self.prefer_group_layout.addWidget(button)

                button = QPushButton('그룹 추가')
                button.clicked.connect(partial(self.prefer_AddFunction, course))
                self.prefer_group_layout.addWidget(button)

                self.layout().addWidget(self.prefer_button_group)
                self.prefer_button_group.adjustSize()
                c_button_pos = c_button.mapToGlobal(c_button.pos())
                # self.prefer_button_group.move(c_button_pos.x() - 100, c_button_pos.y() - 150)
                self.prefer_button_group.move(QCursor.pos().x() - self.pos().x(),
                                              QCursor.pos().y() - self.pos().y() - 59)
                #동적으로 생성되는 객체가 화면과 마우스의 움직임을 따라가기 위한 코드
                self.prefer_button_group.show()

    # 꼭 버튼 눌렀을 때 나오는 그룹리스트 버튼 삭제
    def prefer_removeGroup1(self):
        self.prefer_button_group.hide()

    # 장바구니에서 꼭 버튼 -> 그룹 번호 선택
    def addCourse1(self, i, course):
        #del selected_course[self.row]
        selected_course.delete(self.row)
        self.Course_Basket.removeRow(self.row)
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
        groupbox = QGroupBox()
        groupbox.setStyleSheet("border: 0px;")
        box_layout = QHBoxLayout(groupbox)
        label = QLabel('그룹' + str(self.must_scroll_layout.count() + 1))
        box_layout.addWidget(label, alignment=Qt.AlignLeft)

        new_group = Table()
        course_group = []
        Must_group.add(course_group)
        Must_layout.append(new_group)

        box_layout.addWidget(new_group)

        groupbox.setMinimumHeight(200)
        self.must_scroll_layout.addWidget(groupbox)
        self.groupMust.setWidget(self.must_scroll)
        self.addCourse1(self.must_scroll_layout.count() - 1, course)

    # 꼭에서 그룹 삭제 버튼 클릭
    def must_RemoveFunction(self):
        self.layout().removeWidget(self.delete_must_button_group)
        while self.delete_must_group_layout.count():
            item = self.delete_must_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        if Must_layout:
            xButton = QPushButton('삭제 안 함')
            xButton.clicked.connect(self.must_removeGroup2)
            self.delete_must_group_layout.addWidget(xButton)

            for i in range(len(Must_layout)):
                button = QPushButton('그룹' + str(i + 1))
                button.clicked.connect(partial(self.removeFunction1, i))
                self.delete_must_group_layout.addWidget(button)

            self.layout().addWidget(self.delete_must_button_group)
            self.delete_must_button_group.adjustSize()
            # self.delete_must_button_group.move(int((width*(self.Must_Remove.pos().x() + 50))/1920), int((height*(self.Must_Remove.pos().y() - 50))/1080))
            self.delete_must_button_group.move(QCursor.pos().x() - self.pos().x(),
                                               QCursor.pos().y() - self.pos().y() - 59)
            #동적으로 생성되는 객체가 화면과 마우스의 움직임을 따라가기 위한 코드
            self.delete_must_button_group.show()

    def must_removeGroup2(self):
        self.delete_must_button_group.hide()

    # 꼭에서 그룹 삭제 버튼 -> 그룹 번호 선택
    def removeFunction1(self, i):
        # 안에 있는 강의 그룹을 장바구니로 돌린다
        for course in Must_group.get_group(i):
            selected_course.append(course)
            # 그룹 삭제
        Must_group.delete(i)
        del Must_layout[i]
        # 장바구니 최신화
        self.setTable()

        item = self.must_scroll_layout.takeAt(i)
        widget = item.widget()
        if widget:
            widget.deleteLater()

        # 그룹 번호 최신화
        for index in range(self.must_scroll_layout.count()):
            item = self.must_scroll_layout.itemAt(index)
            if item and isinstance(item.widget(), QGroupBox):
                label = item.widget().layout().itemAt(0).widget()
                if label and isinstance(label, QLabel):
                    label.setText('그룹' + str(index + 1))

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
        #del selected_course[self.row]
        selected_course.delete(self.row)
        self.Course_Basket.removeRow(self.row)
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
        groupbox = QGroupBox()
        groupbox.setStyleSheet("border: 0px;")
        box_layout = QHBoxLayout(groupbox)
        label = QLabel(str(self.prefer_scroll_layout.count() + 1) + '순위')
        box_layout.addWidget(label, alignment=Qt.AlignLeft)

        new_group = Table()
        course_group = []
        Prefer_group.add(course_group)
        Prefer_layout.append(new_group)

        box_layout.addWidget(new_group)

        groupbox.setMinimumHeight(200)
        self.prefer_scroll_layout.addWidget(groupbox)
        self.groupPrefer.setWidget(self.prefer_scroll)
        self.addCourse2(self.prefer_scroll_layout.count() - 1, course)

    # 들으면 좋음에서 그룹 삭제 버튼 클릭
    def prefer_RemoveFunction(self):
        self.layout().removeWidget(self.delete_prefer_button_group)
        while self.delete_prefer_group_layout.count():
            item = self.delete_prefer_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        if Prefer_layout:
            xButton = QPushButton('삭제 안 함')
            xButton.clicked.connect(self.prefer_removeGroup2)
            self.delete_prefer_group_layout.addWidget(xButton)
            for i in range(len(Prefer_layout)):
                button = QPushButton(str(i + 1) + '순위')
                button.clicked.connect(partial(self.removeFunction2, i))
                self.delete_prefer_group_layout.addWidget(button)

            self.layout().addWidget(self.delete_prefer_button_group)
            self.delete_prefer_button_group.adjustSize()
            # self.delete_prefer_button_group.move(int((width*(self.Prefer_Remove.pos().x() - 100))/1920), int((height*(self.Prefer_Remove.pos().y() - 50))/1080))
            self.delete_prefer_button_group.move(QCursor.pos().x() - self.pos().x() - 100,
                                                 QCursor.pos().y() - self.pos().y() - 59)
            self.delete_prefer_button_group.show()

    def prefer_removeGroup2(self):
        self.delete_prefer_button_group.hide()

    # 들으면 좋음에서 그룹 삭제 버튼 -> 그룹 번호 선택
    def removeFunction2(self, i):
        # TODO: 그룹삭제시 해당 강의그룹 장바구니로 돌려야됨
        # 안에 있는 강의 그룹을 장바구니로 돌린다
        for course in Prefer_group.get_group(i):
            selected_course.append(course)
            # 그룹 삭제
        Prefer_group.delete(i)
        del Prefer_layout[i]
        # 장바구니 최신화
        self.setTable()

        item = self.prefer_scroll_layout.takeAt(i)
        widget = item.widget()
        if widget:
            widget.deleteLater()

        # 그룹 번호 최신화
        for index in range(self.prefer_scroll_layout.count()):
            item = self.prefer_scroll_layout.itemAt(index)
            if item and isinstance(item.widget(), QGroupBox):
                label = item.widget().layout().itemAt(0).widget()
                if label and isinstance(label, QLabel):
                    label.setText(str(index + 1) + '순위')

        self.layout().removeWidget(self.delete_prefer_button_group)
        while self.delete_prefer_group_layout.count():
            item = self.delete_prefer_group_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        self.delete_prefer_button_group.hide()

    # 시간표 버튼 클릭 (최종 시간표 창으로 이동)
    def Button_ScheduleFunction(self):
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        myWindow3.create_Table()
        myWindow3.showMaximized()
        myWindow3.show()
        self.close()

    # 강의 검색 버튼 클릭 (강의 검색 창으로 이동)
    def Button_CoursesFunction(self):
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        myWindow1.setTable()
        myWindow1.show()
        self.close()

    # 시간표 만들기 (시간표 생성 창으로 이동)
    def Button_CreateFunction(self):
        if self.must_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움
            self.must_button_group.setVisible(False)
        elif self.prefer_button_group.isVisible():
            # 그룹박스 이미 띄워져있으면 창 지움 2
            self.prefer_button_group.setVisible(False)
        elif self.delete_must_button_group.isVisible():
            # 이미 꼭 삭제창 띄워져있으면 지움
            self.delete_must_button_group.setVisible(False)
        elif self.delete_prefer_button_group.isVisible():
            # 이미 들으면 좋음 삭제창 띄워져있으면 지움
            self.delete_prefer_button_group.setVisible(False)
        myWindow4.create_Header()
        myWindow4.showMaximized()
        myWindow4.show()
        self.close()


# 최종 시간표 보여주는 창
class timeTable(QMainWindow, form_class3, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("시간표")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_layout = QVBoxLayout(self.central_widget)

        self.button_search = QPushButton('강의 검색')  # 강의 검색 창으로 이동하는 버튼
        self.button_magic = QPushButton('마법사')  # 마법사 창으로 이동하는 버튼
        self.button_candidate = QPushButton('시간표 생성')  # 시간표 생성 창으로 이동하는 버튼

        self.button_search.clicked.connect(self.button_Search)
        self.button_magic.clicked.connect(self.button_Magic)
        self.button_candidate.clicked.connect(self.button_Candidate)

        self.setStyleSheet(MainStyleSheet.window_stylesheet)

    # 최종 시간표를 생성하는 메소드
    def create_Table(self):
        while self.central_layout.count():
            item = self.central_layout.takeAt(0)
            if item.layout():
                item.layout().deleteLater()

        group = QGroupBox()
        group.setStyleSheet("border: 0px;")
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
        myWindow4.showMaximized()
        myWindow4.show()

        self.close()


# 시간표 후보 생성 창
class ScheduleCandidates(QMainWindow, form_class4, SaveOnClose):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.time_tables = []
        self.current_table_index = -1
        self.setWindowTitle("마법사 결과")
        # self.showMaximized()

        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.setStyleSheet(MainStyleSheet.window_stylesheet)

    # 시간표 생성 창 initialize
    def create_Header(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Schedule의 리스트
        self.time_tables = ScheduleManager.time_table_maker(Must_group, Prefer_group, int(tot_credits))

        self.time_tables.sort(key=lambda x: ''.join(map(str, x[1])), reverse=False)
        self.time_tables.sort(key=lambda x: len(x[1]), reverse=True)

        #정렬 순위
        #1. 가장 많은 희망 강의를 반영한 시간표
        #2. 순위가 높은 시간표를 반영한 시간표

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

        group.setStyleSheet("border: 0px;")

        header_layout.addWidget(group)
        # print(f"possible schedules : {self.time_tables}")
        if len(self.time_tables) > 0:
            label = QLabel(f"결과 보기\n총 {len(self.time_tables)}개의 시간표가 만들어졌습니다.\n마음에 드는 시간표를 저장하세요.")
            label.setAlignment(Qt.AlignCenter)

            button_layout = QHBoxLayout()

            button_layout.addStretch()
            preferences = ', '.join(f'{j}순위' for j in self.time_tables[0][1])
            if not self.time_tables[0][1]:
                tableBox = QLineEdit('후보 ' + str(1) + " - 희망 강의 반영 안 됨")
            else:
                tableBox = QLineEdit('후보 ' + str(1) + " - " + preferences + " 반영")
            tableBox.setAlignment(Qt.AlignCenter)
            tableBox.setReadOnly(True)
            tableBox.setMaximumWidth(300)
            tableBox.setMinimumHeight(30)

            left_button = QPushButton('<')
            left_button.clicked.connect(lambda: self.leftbuttonClicked(tableBox, num_of_table))
            left_button.setFixedSize(100, 30)
            # left_button.setMaximumWidth(100)
            # left_button.setMinimumHeight(30)
            right_button = QPushButton('>')
            right_button.clicked.connect(lambda: self.rightbuttonClicked(tableBox, num_of_table))
            left_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            left_button.setFixedSize(100, 30)
            right_button.setFixedSize(100, 30)
            # right_button.setMaximumWidth(100)
            # right_button.setMinimumHeight(30)

            num_of_table = QComboBox()
            num_of_table.setEditable(True)
            num_of_table.lineEdit().setAlignment(Qt.AlignCenter)
            num_of_table.lineEdit().setReadOnly(True)
            num_of_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            num_of_table.setFixedSize(300, 30)

            button_layout.addWidget(left_button)
            button_layout.addWidget(tableBox)
            button_layout.addWidget(right_button)
            button_layout.addWidget(num_of_table)

            button_layout.addStretch()

            num_of_table.currentIndexChanged.connect(lambda: self.comboBoxFunction(tableBox))
            items = ['']
            for i in range(len(self.time_tables)):
                preferences = ', '.join(f'{j}순위' for j in self.time_tables[i][1])
                if not self.time_tables[i][1]:
                    items.append('후보 ' + str(i + 1) + " - 희망 강의 반영 안 됨")
                else:
                    items.append('후보 ' + str(i + 1) + " - " + preferences + " 반영")
            num_of_table.addItems(items)
            header_layout.addWidget(label)
            header_layout.addLayout(button_layout)

            self.main_layout.addWidget(header)
            self.create_Table(0)
        else:
            label = QLabel('만들어진 시간표가 없습니다. 강의를 그룹에 추가하세요')
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            header_layout.addWidget(label)
            self.main_layout.addWidget(header)

    def leftbuttonClicked(self, lineEdit, comboBox):
        i = int(lineEdit.text().split()[1]) - 1
        print('왼쪽' + str(i))
        num = len(self.time_tables)
        if i == 0:
            i = num - 1
        else:
            i = i - 1

        preferences = ', '.join(f'{j}순위' for j in self.time_tables[i][1])
        if not self.time_tables[i][1]:
            lineEdit.setText('후보 ' + str(i + 1) + " - 희망 강의 반영 안 됨")
        else:
            lineEdit.setText('후보 ' + str(i + 1) + " - " + preferences + " 반영")
        comboBox.setCurrentIndex(i + 1)
        self.create_Table(i)

    def rightbuttonClicked(self, lineEdit, comboBox):
        i = int(lineEdit.text().split()[1]) - 1
        print('오른쪽' + str(i))
        num = len(self.time_tables)
        if i == num - 1:
            i = 0
        else:
            i = i + 1

        preferences = ', '.join(f'{j}순위' for j in self.time_tables[i][1])
        if not self.time_tables[i][1]:
            lineEdit.setText('후보 ' + str(i + 1) + " - 희망 강의 반영 안 됨")
        else:
            lineEdit.setText('후보 ' + str(i + 1) + " - " + preferences + " 반영")
        comboBox.setCurrentIndex(i + 1)
        self.create_Table(i)

    def comboBoxFunction(self, lineEdit):
        sender = self.sender()
        if sender.currentText() != '':
            i = int(sender.currentText().split()[1]) - 1
            preferences = ', '.join(f'{j}순위' for j in self.time_tables[i][1])
            if not self.time_tables[i][1]:
                lineEdit.setText('후보 ' + str(i + 1) + " - 희망 강의 반영 안 됨")
            else:
                lineEdit.setText('후보 ' + str(i + 1) + " - " + preferences + " 반영")
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

        schedule = Schedule_table(self.time_tables[index][0], self.time_tables[index][1])

        button = QPushButton('저장')
        button.setFixedSize(100, 30)
        button.clicked.connect(lambda _, idx=index: self.select_Table(idx))

        group.layout().addWidget(button, alignment=Qt.AlignRight)
        group.layout().addWidget(schedule)

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
        myWindow3.showMaximized()
        myWindow3.show()
        self.close()

    # 시간표 후보 중 최종 시간표를 저장
    def select_Table(self, index):
        selected_schedule.clear()
        for course in self.time_tables[index][0]:
            selected_schedule.append(course)


# 시간표 테이블 1개에 대한 class
class Schedule_table(QTableWidget):
    def __init__(self, courses, rank=[]):
        super().__init__()
        self.setColumnCount(8)
        self.setRowCount(56)
        self.setHorizontalHeaderLabels(
            ['교시', '시간', '월요일(Mon)', '화요일(Tue)', '수요일(Wed)', '목요일(Thu)', '금요일(Fri)', '토요일(Sat)'])
        h = [''] * 56
        self.setVerticalHeaderLabels(h)

        for row in range(0, 56, 4):
            self.setSpan(row, 0, 4, 1)

        count = 0
        for row in range(0, 56, 4):
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 0, item)
            count += 1

        time_format = "{:02d}:{:02d}"
        count_hours = 8
        count_minutes = 0

        for row in range(0, 56):
            time_item = QTableWidgetItem(time_format.format(count_hours, count_minutes))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, time_item)
            count_minutes += 15
            if count_minutes == 60:
                count_minutes = 0
                count_hours += 1
            if count_hours == 24:
                count_hours = 0
        used_colors = []
        for course in courses:
            color = self.random_color()  # 시간표 블럭에 칠할 색 -> 랜덤으로 정한다
            while color in used_colors:
                color = self.random_color()
            used_colors.append(color)
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
                    item.setForeground(QColor(0, 0, 0))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(row, day_column, item)

                    self.item(row, day_column).setBackground(QColor(*color))

        fixed_row_height = 5
        fixed_column_width = 265

        for row in range(self.rowCount()):
            self.setRowHeight(row, fixed_row_height)
        for column in range(self.columnCount()):
            self.resizeColumnToContents(column) if column in (0, 1) else self.setColumnWidth(column, fixed_column_width)

        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(0)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def random_color(self):
        color = [255, 117, 115 + 35 * random.randint(1, 4)]
        random.shuffle(color)
        return color

    def get_day_index(self, day):
        day_mapping = {'월': 2, '화': 3, '수': 4, '목': 5, '금': 6, '토': 7}
        return day_mapping.get(day)

    def get_time_index(self, time_str):
        hours, minutes = map(int, time_str.split(':'))
        return (hours - 8) * 4 + (1 if minutes == 15 else 0)


# 꼭, 들으면 좋음에서 추가되는 하나의 그룹을 테이블로 표현함
class Table(QTableWidget):
    widget_counts = 0

    def __init__(self):
        super().__init__()
        self.id = Table.widget_counts
        Table.widget_counts += 1
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["", '과목명', '과목번호', '담당교수', '강의시간'])
        self.setStyleSheet(MainStyleSheet.table_stylesheet)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(0)

    # 꼭에서 그룹 생성
    def createTable1(self, index):
        # self.setRowCount(len(Must_group[index]))
        self.setRowCount(len(Must_group.get_groups()[index]))

        # for i in range(len(Must_group[index])):
        for i in range(len(Must_group.get_groups()[index])):
            button = QPushButton("X")
            button.setStyleSheet(MainStyleSheet.button_stylesheet)
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.outGroupButton1)
            self.setCellWidget(i, 0, button)

            for j in range(1, 5):
                item_text = ""
                if j == 1:
                    # item_text = Must_group[index][i].total[7]
                    item_text = Must_group.get_group(index)[i].total[7]
                elif j == 2:
                    # item_text = Must_group[index][i].total[6]
                    item_text = Must_group.get_group(index)[i].total[6]
                elif j == 3:
                    # item_text = Must_group[index][i].total[9]
                    item_text = Must_group.get_group(index)[i].total[9]
                elif j == 4:
                    # item_text = Must_group[index][i].total[11]
                    item_text = Must_group.get_group(index)[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        # self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 꼭에서 그룹 생성하는건데 얘는 창을 끄고 키거나 했을 때 기존에 저장된 그룹 복원 용도
    def createTable_1(self, courses):
        self.setRowCount(len(courses))

        for i in range(len(courses)):
            button = QPushButton("X")
            button.setStyleSheet(MainStyleSheet.button_stylesheet)
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

        # self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 들으면 좋음에서 그룹 생성
    def createTable2(self, index):
        # self.setRowCount(len(Prefer_group[index]))
        self.setRowCount(len(Prefer_group.get_group(index)))

        # for i in range(len(Prefer_group[index])):
        for i in range(len(Prefer_group.get_group(index))):
            button = QPushButton("X")
            button.setStyleSheet(MainStyleSheet.button_stylesheet)
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.outGroupButton2)
            self.setCellWidget(i, 0, button)

            for j in range(1, 5):
                item_text = ""
                if j == 1:
                    item_text = Prefer_group.get_group(index)[i].total[7]
                elif j == 2:
                    item_text = Prefer_group.get_group(index)[i].total[6]
                elif j == 3:
                    item_text = Prefer_group.get_group(index)[i].total[9]
                elif j == 4:
                    item_text = Prefer_group.get_group(index)[i].total[11]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(i, j, item)
            self.setRowHeight(i, TABLE_ROW_SIZE)

        # self.resizeRowsToContents()  # 칸 크기 맞추기
        self.resizeColumnsToContents()  # 칸 크기 맞추기

    # 들으면 좋음에서 그룹 생성하는건데 얘는 창을 끄고 키거나 했을 때 기존에 저장된 그룹 복원 용도
    def createTable_2(self, courses):
        self.setRowCount(len(courses))

        for i in range(len(courses)):
            button = QPushButton("X")
            button.setStyleSheet(MainStyleSheet.button_stylesheet)
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

        # self.resizeRowsToContents()
        self.resizeColumnsToContents()

    # 꼭 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton1(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Must_layout.index(self)  # 오류?

            if row != -1:
                selected_course.append(Must_group.get_group(idx)[row])
                del Must_group.get_group(idx)[row]
                self.removeRow(row)

        myWindow2.setTable()

    # 들으면 좋음 그룹에서 X 버튼 누르면 강의가 장바구니로 이동함
    def outGroupButton2(self):
        button = self.sender()
        if button:
            index = self.indexAt(button.pos())
            row = index.row()
            idx = Prefer_layout.index(self)  # 오류

            if row != -1:
                # selected_course.append(Prefer_group[idx][row])
                selected_course.append(Prefer_group.get_group(idx)[row])
                del Prefer_group.get_group(idx)[row]
                self.removeRow(row)

        myWindow2.setTable()


def suppress_qt_warnings():  # 해상도 별 UI크기 강제 고정
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "2"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


suppress_qt_warnings()
# QApplication : 프로그램을 실행시켜주는 클래스
app = QApplication(sys.argv)
screen_rect = app.desktop().screenGeometry()
width = screen_rect.width()
height = screen_rect.height()

for s in set([c.department for c in DB.course_list]):
    # print(s)
    pass
# 각 창의 인스턴스 생성
myWindow1 = courseSearch()
myWindow2 = Magic()
myWindow3 = timeTable()
myWindow4 = ScheduleCandidates()

# 프로그램 화면을 보여주는 코드
myWindow1.show()

# 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
app.exec_()


import Course
import CourseDB

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
        # # Timeblock 파싱 확인용
        print(f"{course.title[:5]}", end=" ")
        for t in course.time:
            print(t, end=" ")
        print(f" '{course.time_info_raw_string}'",end=" ")
        print()

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

selected_course = []            # 장바구니에 담을 강의 리스트
condition = ["","","","",""]    # 검색 조건
searched_course = []            # 검색 조건에 부합하는 강의 리스트

# 강의 검색 창
class courseSearch(QMainWindow, form_class1) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Search.clicked.connect(self.Button_SearchFunction)  # 강의 검색 버튼
        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction)  # 시간표 창으로 이동하는 버튼
        self.Button_Magic.clicked.connect(self.Button_MagicFunction)  # 마법사 창으로 이동하는 버튼
        self.Button_Select.clicked.connect(self.getSelectedRows)  # 장바구니 담기 버튼

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

    def Button_SearchFunction(self):
        self.Table_Course.setRowCount(0)
        searched_course.clear()

        for course in DB.course_list:
            if (not condition[1] or course.department == condition[1]) and \
                (not condition[2] or course.title == condition[2]) and \
                (not condition[3] or (condition[3] in [time.day for time in course.time])) and \
                (not condition[4] or any(time.day == condition[3] and str(time.period) == condition[4] for time in course.time)):
                searched_course.append(course)

        self.Table_Course.setRowCount(len(searched_course))

        for i in range(0, len(searched_course)):
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox {margin-left: 10%; margin-right: 10%;}")
            self.Table_Course.setCellWidget(i, 0, checkbox)  # 첫 번째 열에 체크박스 추가

            for j in range(1, 13):
                item_text = searched_course[i].total[j-1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Table_Course.setItem(i, j, item)

        self.Table_Course.resizeRowsToContents()  # 칸 크기 맞추기
        self.Table_Course.resizeColumnsToContents()   # 칸 크기 맞추기

    def Button_ScheduleFunction(self):
        myWindow3.show()
        self.close()

    def Button_MagicFunction(self):
        myWindow2.createTable()
        myWindow2.show()
        myWindow2.setTable()
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

    def getSelectedRows(self):
        for i in range(self.Table_Course.rowCount()):
            checkbox_widget = self.Table_Course.cellWidget(i, 0)

            if checkbox_widget.isChecked() and searched_course[i] not in selected_course:
                selected_course.append(searched_course[i])
            elif checkbox_widget.isChecked() == False and searched_course[i] in selected_course:
                selected_course.remove(searched_course[i])

        print(selected_course)

class CustomTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("dd")
            # self.startDrag(Qt.MoveAction)
        super().mousePressEvent(event)

    def startDrag(self, dropActions):
        selected_row = self.currentRow()
        if selected_row != -1:
            selected_course_object = selected_course[selected_row]

            mime_data = QMimeData()
            serialized_data = f"{selected_course_object.title},{selected_course_object.instructor},{selected_course_object.time_info_raw_string}"
            mime_data.setText(serialized_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(dropActions)
# 마법사
class Magic(QMainWindow, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Button_Schedule.clicked.connect(self.Button_ScheduleFunction) # Button to move to timetable window
        self.Button_Courses.clicked.connect(self.Button_CoursesFunction) # Button to move to the course search window
        self.group1Button.clicked.connect(self.g1buttonFunction) # Button to add group to
        self.group2Button.clicked.connect(self.g2buttonFunction) # Button to add group to Good to Hear

        self.groupMust.setLayout(QVBoxLayout(self.groupMust))
        self.groupPrefer.setLayout(QVBoxLayout(self.groupPrefer))

        self.table = CustomTable()
        self.table.setGeometry(500, 400, 1151, 221)
        headers = ["", '대학', '개설학과', '캠퍼스', '학년', '과정', '이수구분', '과목번호', '과목명', '학점-시간', '담당교수', '폐강여부', '강의시간', '비고']
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.layout().addWidget(self.table)

    def setTable(self):
        self.table.setRowCount(len(selected_course))
        # self.table.setDragEnabled(True)

        for i in range(len(selected_course)):
            button = QPushButton("장바구니 삭제")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.buttonClicked)
            self.table.setCellWidget(i, 0, button)  # Add delete button to first column

            for j in range(1, 14):
                item_text = selected_course[i].total[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.resizeRowsToContents()  # Adjust column size
        self.table.resizeColumnsToContents()  # Resize columns
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

    #  장바구니 테이블 생성하는 메소드
    def createTable(self):
        self.Table_Course.setRowCount(len(selected_course))
        # self.Table_Course.setDragEnabled(True)

        for i in range(len(selected_course)):
            button = QPushButton("장바구니 삭제")
            button.setStyleSheet("background-color: rgb(242, 255, 255);")
            button.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )
            button.clicked.connect(self.buttonClicked)
            self.Table_Course.setCellWidget(i, 0, button)  # 첫 번째 열에 삭제버튼 추가

            for j in range(1, 14):
                item_text = selected_course[i].total[j-1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.Table_Course.setItem(i, j, item)

        self.Table_Course.resizeRowsToContents()  # 칸 크기 맞추기
        self.Table_Course.resizeColumnsToContents()  # 칸 크기 맞추기
        self.Table_Course.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Table_Course.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.Table_Course.setSelectionMode(QAbstractItemView.SingleSelection)

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         print('!!')
    #         self.startDrag(Qt.MoveAction)
    #     super().mousePressEvent(event)
    #
    # def startDrag(self, dropActions):
    #     selected_row = self.Table_Course.currentRow()
    #     print(selected_row)
    #     if selected_row != -1:
    #         selected_course_object = selected_course[selected_row]
    #
    #         mime_data = QMimeData()
    #         serialized_data = f"{selected_course_object.title},{selected_course_object.instructor},{selected_course_object.time_info_raw_string}"
    #         mime_data.setText(serialized_data)
    #
    #         drag = QDrag(self)
    #         drag.setMimeData(mime_data)
    #         drag.exec_(dropActions)

    def buttonClicked(self):
        button = self.sender()
        if button:
            index = self.Table_Course.indexAt(button.pos())
            row = index.row()

            if row != -1:
                del selected_course[row]
                self.Table_Course.removeRow(row)
                print(selected_course)

    def Button_ScheduleFunction(self):
        myWindow3.show()
        self.close()

    def Button_CoursesFunction(self):
        myWindow1.show()
        self.close()

    def g1buttonFunction(self):
        new_group = Table()
        self.groupMust.layout().addWidget(new_group)

    def g2buttonFunction(self):
        new_group = Table()
        self.groupPrefer.layout().addWidget(new_group)

# 시간표
class timeTable(QMainWindow, form_class3):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_1.clicked.connect(self.button1Function) # 마법사 창으로 이동하는 버튼
        self.pushButton_2.clicked.connect(self.button2Function) # 강의 검색 창으로 이동하는 버튼

    def button1Function(self):
        myWindow2.show()
        self.close()

    def button2Function(self):
        myWindow1.show()
        self.close()

class Table(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        self.setColumnCount(14)
        self.setHorizontalHeaderLabels(["", '대학', '개설학과', '캠퍼스', '학년', '과정', '이수구분', '과목번호', '과목명', '학점-시간', '담당교수', '폐강여부', '강의시간', '비고'])

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def startDrag(self, dropActions):
        selected_row = self.currentRow()
        if selected_row != -1:
            selected_course_object = selected_course[selected_row]

            mime_data = QMimeData()
            serialized_data = f"{selected_course_object.title},{selected_course_object.instructor},{selected_course_object.time_info_raw_string}"
            mime_data.setText(serialized_data)

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(dropActions)

    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        mime_data = e.mimeData()
        if mime_data.hasText():
            print("!!")
        # self.resizeRowsToContents()
        # self.resizeColumnsToContents()
        e.acceptProposedAction()

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
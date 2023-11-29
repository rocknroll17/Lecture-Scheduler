import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5 import uic

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

course = ['소프트웨어대학', '소프트웨어학부', '3', '전공', '수치해석', '3-3', '이창하', '월 7,8 / 수 7 / 310관 728호', '대면수업', '공학인증(BSM)']
selected_course_index = []      # 장바구니에 담을 객체 index
selected_course = []            # 장바구니에 담을 객체 리스트
condition_search = ["","","","","",""]      # 검색 조건
searched_course = []                        # 검색 조건에 부합하는 강의 리스트

# 강의 검색 창
class courseSearch(QMainWindow, form_class1) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_1.clicked.connect(self.button1Function)  # 강의 검색 버튼
        self.pushButton_2.clicked.connect(self.button2Function)  # 시간표 창으로 이동하는 버튼
        self.pushButton_3.clicked.connect(self.button3Function)  # 마법사 창으로 이동하는 버튼
        self.pushButton_4.clicked.connect(self.getSelectedRows)  # 장바구니 담기 버튼

        self.comboBox_1.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 대학
        self.comboBox_2.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 학과
        self.comboBox_3.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 과목명
        self.comboBox_4.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 요일
        self.comboBox_5.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 교시
        self.comboBox_6.currentIndexChanged.connect(self.comboBoxFunction)  # 조건 검색 : 캠퍼스

        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def button1Function(self):
        # 강의 검색 버튼을 누르면 일단 검색조건(condition_search)랑 부합하는 course들을 꺼내서 course 리스트를 searched_course에 저장하고 얘를 테이블에 추가하면 됨

        self.table1.setRowCount(10)

        i=0
        while i<10:
            if course[0] != condition_search[0] and condition_search[0] != "":
                self.table1.setRowCount(0)
                break
            if course[1] != condition_search[1] and condition_search[1] != "":
                self.table1.setRowCount(0)
                break
            if course[4] != condition_search[2] and condition_search[2] != "":
                self.table1.setRowCount(0)
                break
            if condition_search[3] != "":
                parts = course[7].split('/')
                parts = [part.strip() for part in parts]

                if parts[0][0] != condition_search[3][0] and parts[1][0] != condition_search[3][0]:
                    self.table1.setRowCount(0)
                    break

            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox {margin-left: 10%; margin-right: 10%;}")
            self.table1.setCellWidget(i, 0, checkbox)  # 첫 번째 열에 체크박스 추가

            for j in range(1, 11):
                item_text = course[j - 1]
                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table1.setItem(i, j, item)

            i+=1

        self.table1.resizeRowsToContents()  # 칸 크기 맞추기
        self.table1.resizeColumnsToContents()   # 칸 크기 맞추기
        total_width = sum(self.table1.columnWidth(i) for i in range(self.table1.columnCount()))
        total_height = sum(self.table1.rowHeight(i) for i in range(self.table1.rowCount()))
        self.table1.setFixedSize(total_width, total_height)

    def button2Function(self):
        myWindow3.show()
        self.close()

    def button3Function(self):
        myWindow2.show()
        self.close()

    def comboBoxFunction(self):
        sender = self.sender()

        if sender == self.comboBox_1:
            selected_data = self.comboBox_1.currentText()
            condition_search[0] = selected_data
        elif sender == self.comboBox_2:
            selected_data = self.comboBox_2.currentText()
            condition_search[1] = selected_data
        elif sender == self.comboBox_3:
            selected_data = self.comboBox_3.currentText()
            condition_search[2] = selected_data
        elif sender == self.comboBox_4:
            selected_data = self.comboBox_4.currentText()
            condition_search[3] = selected_data
        elif sender == self.comboBox_5:
            selected_data = self.comboBox_5.currentText()
            condition_search[4] = selected_data
        elif sender == self.comboBox_6:
            selected_data = self.comboBox_6.currentText()
            condition_search[5] = selected_data

        print(condition_search)

    def getSelectedRows(self):
        # 장바구니 담기 버튼을 누르면 searched_course중 체크된 애들만 selected_course에 옮겨 담으면 됨
        for i in range(self.table1.rowCount()):
            checkbox_widget = self.table1.cellWidget(i, 0)

            if checkbox_widget.isChecked():
                selected_course_index.append(i)

        print("장바구니에 담을 강의 index:", selected_course_index)

# 마법사
class Magic(QMainWindow, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton_1.clicked.connect(self.button1Function)     # 시간표 창으로 이동하는 버튼
        self.pushButton_2.clicked.connect(self.button2Function)     # 강의 검색 창으로 이동하는 버튼
        self.group1Button.clicked.connect(self.g1buttonFunction)    # 꼭에 그룹 추가하는 버튼
        # self.group2Button.clicked.connect(self.g2buttonFunction)    # 들으면 좋음에 그룹 추가하는 버튼

        self.groupBox_1.setLayout(QVBoxLayout())  # groupBox_1의 레이아웃 초기화
        self.groupBox_2.setLayout(QVBoxLayout())  # groupBox_2의 레이아웃 초기화

        self.groupRects = {}  # 그룹들의 위치 정보를 저장할 딕셔너리

        self.table1.setRowCount(10)
        for j in range(0, 10):
            item_text = course[j]
            item = QTableWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignCenter)
            self.table1.setItem(0, j, item)

        self.table1.resizeRowsToContents()  # 칸 크기 맞추기
        self.table1.resizeColumnsToContents()   # 칸 크기 맞추기
        # total_width = sum(self.table1.columnWidth(i) for i in range(self.table1.columnCount()))
        # total_height = sum(self.table1.rowHeight(i) for i in range(self.table1.rowCount()))
        # self.table1.setFixedSize(total_width, total_height)
        self.table1.setFixedSize(self.table1.size())
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def button1Function(self):
        myWindow3.show()
        self.close()

    def button2Function(self):
        myWindow1.show()
        self.close()

    def g1buttonFunction(self):
        new_group = QGroupBox("그룹")
        new_group.setAcceptDrops(True)
        group_layout = QVBoxLayout()
        # group_layout.addWidget(QLabel("웹프로그래밍"))
        # group_layout.addWidget(QLabel("김상욱"))
        # group_layout.addWidget(QLabel("화7,8,9 / 310관 619호"))
        new_group.setLayout(group_layout)
        self.groupBox_1.layout().addWidget(new_group)
        # 그룹의 위치 정보 저장
        self.groupRects[new_group] = new_group.geometry()

    def g2buttonFunction(self):
        new_group = QGroupBox("그룹")
        group_layout = QVBoxLayout(new_group)
        self.groupBox_2.layout().addWidget(new_group)

    def dropEvent(self, event):
        pos = event.pos()

        # 드롭된 위치와 그룹들의 위치를 비교하여 어느 그룹에 드롭되었는지 판별
        for group, rect in self.groupRects.items():
            if rect.contains(pos):
                dropped_item_text = self.table1.selectedItems()[0].text()
                label = QLabel(dropped_item_text)
                group.layout().addWidget(label)
                print(f"Dropped on {group.title()}")

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

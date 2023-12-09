# window 스타일시트
#동적으로 생성되는 객체들의 스타일 시트를 정의
window_stylesheet = """

/* 스크롤바 필요한 widget stylesheet에 입력 */

#Dialog {
	background-color: #1e1f22;
}

QTableWidget {
	border-radius: 10px;
	color: white;
	border: 2px solid #ccc;
	background-color: #2b2d31;
    gridline-color: #404349;
}

QScrollBar:vertical {
	boder: none;
	background-color: transparent;
	width: 14px;
	margin: 0px 0 0px 0;
	boder-radius: 0px;
}

QScrollBar::handle:vertical {
	background-color: #1e1f23;
	min-height: 30px;
	border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
	background-color: #1a1b1e;
}

QScrollBar::handle:vertical:pressed {
	background-color: #141416;
}

QScrollBar::sub-line:vertical {
	border: none;
}

QScrollBar::add-line:vertical {
	border: none;
}

QScrollBar::up-arrow:vertical, QScrollBar:down-arrow:vertical {
	background: none;
}

QScrollBar::add-page:vertical, QScrollBar:sub-page:vertical {
	background: none;
}

/* horizontal */

QScrollBar:horizontal {
	boder: none;
	background-color: transparent;
	height: 14px;
	margin: 0 0px 0 0px;
	boder-radius: 0px;
}

QScrollBar::handle:horizontal {
	background-color: #1e1f23;
	min-height: 30px;
	border-radius: 7px;
}

QScrollBar::handle:horizontal:hover {
	background-color: #1a1b1e;
}

QScrollBar::handle:horizontal:pressed {
	background-color: #141416;
}

QScrollBar::sub-line:horizontal {
	border: none;
}

QScrollBar::add-line:horizontal {
	border: none;
}

QScrollBar::up-arrow:horizontal, QScrollBar:down-arrow:horizontal {
	background: none;
}

QScrollBar::add-page:horizontal, QScrollBar:sub-page:horizontal {
	background: none;
}

QTableView QTableCornerButton::section {
    background-color: #1e1f23;
}

QGroupBox{
	color: white;
}

QLabel {
	color: white;
}

QPushButton {
	background-color: #42454c;
	color: white;
	padding: 6px;

}

QPushButton:hover {
	background-color: #383b40;
}

QPushButton:pressed {
	background-color: #1d1e21;
}

toQHeaderView {
	border-radius: 10px;
}

QHeaderView::section {
	background-color: #1e1f23;
    color: white;
    border-style: none;
    font-family: 'Montserrat', sans-serif;
	/*border-bottom: 2px solid #fffff8;
    border-top: 2px solid #fffff8;*/
}

QHeaderView::section:horizontal {
	background-color: #1e1f23;
	default-background-color: #3d5673;
    margin: 0px;
    padding: 0px;
}

QHeaderView::section:vertical {
	background-color: #1e1f23;
	default-background-color: #3d5673;
    margin: 0px;
    padding: 0px;
}

QHeaderView {
    background-color: #1e1f23;
}

"""

# QTableWidget 스타일시트

table_stylesheet = """

toQHeaderView {
	border-radius: 10px;
}

QHeaderView::section {
	background-color: #1e1f23;
    color: white;
    border-style: none;
    font-family: 'Montserrat', sans-serif;
	/*border-bottom: 2px solid #fffff8;
    border-top: 2px solid #fffff8;*/
}

QTableWidget {
	border-radius: 10px;
    border: 2px solid #ccc;
	background-color: #2b2d31;
    gridline-color: #404349;
}

QHeaderView::section:horizontal {
	background-color: #1e1f23;
	default-background-color: #3d5673;
    margin: 0px;
    padding: 0px;
}

QHeaderView::section:vertical {
	background-color: #1e1f23;
	default-background-color: #3d5673;
    margin: 0px;
    padding: 0px;
}
QHeaderView {
    background-color: #1e1f23;
}
"""

# QPushButton 스타일시트

button_stylesheet = """

QPushButton {
	background-color: #42454c;
	color: #fff;

}

QPushButton:hover {
	background-color: #383b40;
}

QPushButton:pressed {
	background-color: #1d1e21;
}
"""



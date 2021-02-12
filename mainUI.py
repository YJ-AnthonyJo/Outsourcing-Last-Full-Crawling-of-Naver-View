import sys
from PyQt5.QtWidgets import *  # noqa: F403
from PyQt5 import uic, QtCore

from_class = uic.loadUiType("./UI/mainUI.ui")[0]
checkQuery_ui = uic.loadUiType("./UI/CheckQuery.ui")[0]
def DelOverlap(li):
	tmp_list = []
	for v in li:
		if v not in tmp_list and v != '':
			tmp_list.append(v)
	li[:] = tmp_list # 가르키는 object는 동일하다. -> 해당 object를 수정하기 위해 [:]을 사용

class CheckQueryWindow(QMainWindow, checkQuery_ui):  # noqa: F405
	def __init__(self, Queryes):
		super().__init__()
		self.Queryes = Queryes
		self.setupUi(self)
		self.setFixedSize(172, 262)
		self.QueryBrowseAndEdit_PTextEdit.setLineWrapMode(0)
		self.QueryBrowseAndEdit_PTextEdit.setPlainText('\n'.join(Queryes))
		self.Save_btn.clicked.connect(self.Save_)

	def Save_(self, Queryes):
		self.Queryes[:] = self.QueryBrowseAndEdit_PTextEdit.toPlainText().split('\n') # 가르키는 object는 동일하다. -> 해당 object를 수정하기 위해 [:]을 사용
		DelOverlap(self.Queryes)

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Escape:
			self.Queryes[:] = self.QueryBrowseAndEdit_PTextEdit.toPlainText().split('\n') # 가르키는 object는 동일하다. -> 해당 object를 수정하기 위해 [:]을 사용
			DelOverlap(self.Queryes)
			self.close()

class WindowClass(QMainWindow, from_class):  # noqa: F405
	Queryes = []

	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setFixedSize(640, 480)

		self.AddQuery_btn.clicked.connect(self.AssociatedQuery('Func_AddQuery_btn'))
		self.Query_LineEdit.returnPressed.connect(self.AssociatedQuery('Func_AddQuery_btn'))
		self.openFile_btn.clicked.connect(self.AssociatedQuery('Func_openFile_btn'))
		self.CheckQuery_btn.clicked.connect(self.AssociatedQuery('Func_CheckQuery_btn'))
		self.AssociatedQuery('FileDIR_Default')

		self.activateFunc_btn.clicked.connect(self.activateFunc_btn_F)

		self.AssociatedTable('SetDefaultTable')
		self.ViewResult_table.setEditTriggers(QTableWidget.NoEditTriggers)  # noqa: F405
		self.FlagEditable_chbox.stateChanged.connect(self.AssociatedTable('Func_FlagEditable_chbox'))
		self.SelectKeyword_cbox.currentIndexChanged.connect(self.AssociatedTable('Func_SelectKeyword_cbox'))

	def AssociatedQuery(self, funcName):
		# Query(keyword input)과 관련있는 Function들의 집합
		def Func_openFile_btn(): 
			# 실행조건 : openFile_btn이 눌렸을 때
			# 동작 : Open file & get keywords(\n기준) & append to Queryes(앞뒤 공백 제거 후)
			fname = QFileDialog.getOpenFileName(self)  # noqa: F405 # file창 하나 열기
			self.FileDIR_Browser.setPlainText(fname[0])
			f = open(fname[0], 'r')
			self.Queryes += [i.rstrip().lstrip() for i in f.readlines()]
			DelOverlap(self.Queryes)

		def Func_AddQuery_btn(): 
			# 실행조건 : Query_LineEdit에서 enter누르거나, AddQuery_btn을 눌렀을 때 실행
			# 동작 : Query_LineEdit의 text를 공백 제거 후 Queryes에 append함
			# 이후 Query_LineEdit은 ''(Blank)로 돌아감
			self.Queryes.append(self.Query_LineEdit.text().rstrip().lstrip())
			self.Query_LineEdit.setText('')
			DelOverlap(self.Queryes)

		def Func_CheckQuery_btn():
			# 실행조건 : CheckQuery_btn이 눌렸을 때
			# 동작 : CheckQueryWindow Class의 __init__()에 지금까지 입력된 Queryes를 인자로 보내고 이 클래스(window)를 실행(show)한다.
			self.CheckQueryWindow_ = CheckQueryWindow(self.Queryes)
			self.CheckQueryWindow_.show()

		def FileDIR_Default():
			# 실행조건 : 초기 설정(초기 1회만 실행됨)
			# 동작 : \n으로 구분된 keywords가 있는 메모장을 불러오기 전, 파일의 경로를 나타내는 FileDIR_Browser가 비어있을 때, 공백으로 채움
			self.FileDIR_Browser.setPlainText(' ' * 100)
			self.FileDIR_Browser.horizontalScrollBar().setValue(0)
			self.FileDIR_Browser.setLineWrapMode(0)

		return (Func_openFile_btn if funcName == 'Func_openFile_btn' else
			Func_AddQuery_btn if funcName == 'Func_AddQuery_btn' else
			Func_CheckQuery_btn if funcName == 'Func_CheckQuery_btn' else
			FileDIR_Default() if funcName == 'FileDIR_Default' else
			None)

	def AssociatedTable(self, funcname): # 미완
		# 실행 후 결과가 나타나는 table에 관련된 Function들의 집합
		def Func_SelectKeyword_cbox(): # 미완
			# UI 하단의 결과 창에 나타낼 결과 data를 keyword로 선택하는 것
			self.index_ = self.SelectKeyword.currentIndex()
			self.SetTable(self.index_) # 해당 keyword의 index를 가져옴

		def Func_FlagEditable_chbox():
			# 실행조건 : FlagEditable_chbox의 상태가 변했을 때
			# 동작 : 체크시 해당 keyword의 result Data 수정가능
			if self.FlagEditable_chbox.isChecked():
				self.ViewResult_table.setEditTriggers(QTableWidget.DoubleClicked)  # noqa: F405
			else:
				self.ViewResult_table.setEditTriggers(QTableWidget.NoEditTriggers)  # noqa: F405

		def SetDefaultTable():
			# 실행조건 : 초기 설정(초기 1회만 실행됨)
			# 동작 : ViewResult_table을 초기화
			self.ViewResult_table.setRowCount(10) # data가 공백인 10개의 행(빈 행일시 User experience가 좋지 않을 것을 대비함)
			self.ViewResult_table.setColumnCount(3) # column의 개수
			items = ['url', '제목', '날짜']
			self.ViewResult_table.setHorizontalHeaderLabels(items) # column의 header지정

		return (Func_SelectKeyword_cbox if funcname == 'Func_SelectKeyword_cbox' else
			Func_FlagEditable_chbox if funcname == 'Func_FlagEditable_chbox' else
			SetDefaultTable() if funcname == 'SetDefaultTable' else
			None)

	def activateFunc_btn_F(self): # 미완
		print("btn1 clicked")
		Result = {'a':[],'a':[],'a':[],'a':[]}
		for i in range(len(Result['a'])):
			self.ViewResult.setItem()

# query(keywords) 받는 부분은 마무리됨. start버튼으로 crawling하는 부분과 그 결과 data를 얻는 부분, 선택한 keyword에 해당하는 data를 table에 나타내는 부분, 그 data를 excel로 저장하는 부분 남음(예상)

if __name__ == "__main__":
	app = QApplication(sys.argv)   # noqa: F405
	myWindow = WindowClass()
	myWindow.show()
	app.exec_()
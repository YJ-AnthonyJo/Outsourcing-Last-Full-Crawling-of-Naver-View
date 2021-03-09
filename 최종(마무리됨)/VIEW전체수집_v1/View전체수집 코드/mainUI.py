import sys, ast
from PyQt5.QtWidgets import *  # noqa: F403
from PyQt5 import uic, QtCore
import crawling
from pprint import pprint
from pathlib import Path
import pandas as pd
from datetime import datetime


from_class = uic.loadUiType("./UI/mainUI_V2.ui")[0]
def DelOverlap(li): #추측: 중복제거
    tmp_list = []
    for v in li:
        if v not in tmp_list and v != '':
            tmp_list.append(v)
    li[:] = tmp_list # 가르키는 object는 동일하다. -> 해당 object를 수정하기 위해 [:]을 사용

class CheckQueryWindow(QDialog):  # noqa: F405
    def __init__(self, Queryes):
        QDialog.__init__(self, None)
        uic.loadUi('./UI/CheckQuery.ui', self)

        self.Queryes = Queryes
#self.setFixedSize(172, 262)
        self.setWindowTitle('키워드 확인/수정')
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
    changed_item = []
    def __init__(self):
        super().__init__()
        self.setupUi(self)
#self.setFixedSize(640, 480)
        self.resize(640,600)
        self.setWindowTitle('View전체수집')

        self.AddQuery_btn.clicked.connect(self.AssociatedQuery('Func_AddQuery_btn'))
        self.Query_LineEdit.returnPressed.connect(self.AssociatedQuery('Func_AddQuery_btn'))
        self.openFile_btn.clicked.connect(self.AssociatedQuery('Func_openFile_btn'))
        self.CheckQuery_btn.clicked.connect(self.AssociatedQuery('Func_CheckQuery_btn'))
        self.AssociatedQuery('FileDIR_Default')

        self.activateFunc_btn.clicked.connect(self.Func_activateFunc_btn)

        self.AssociatedTable('SetDefaultTable')
        self.ViewResult_table.setEditTriggers(QTableWidget.NoEditTriggers)  # noqa: F405
        self.FlagEditable_chbox.stateChanged.connect(self.AssociatedTable('Func_FlagEditable_chbox'))
        self.SelectKeyword_cbox.currentIndexChanged.connect(self.AssociatedTable('Func_SelectKeyword_cbox'))
#self.SelectKeyword_cbox.activated.connect(self.AssociatedTable('Func_ViewResult_table_admitChange')
        self.changeAdmit_btn.setEnabled(False)
        self.changeAdmit_btn.clicked.connect(self.AssociatedTable('Func_ViewResult_table_admitChanges'))
        self.ViewResult_table.cellDoubleClicked.connect(self.AssociatedTable('Func_ViewResult_table_doubleClicked'))
        self.SaveAsFIle_btn.clicked.connect(self.Func_SaveAsFile_btn)

        f = open('path.json','r')
        self.path = ast.literal_eval(f.read())
        f.close()
        self.for_display = {'driver':None, 'save':None}

        for key in self.path:
            if self.path[key][-1] == '\n':
                self.path[key] = self.path[key][:-1]
            self.for_display[key] = (self.path[key][:40]+'  ...  '+self.path[key][-40:]) if len(self.path[key]) > 100 else self.path[key]


        self.menubar = self.menuBar()

        self.show_current_path = QAction('현재경로 : '+ self.for_display['driver'], self)###in menubar
        chrome_action = QAction('&ChromeDriver경로 설정', self)### in menubar
        chrome_action.triggered.connect(self.chrome)#### for QAction
        
        chrome_driver = self.menubar.addMenu('&Chrome Driver')# MenuBar
        chrome_driver.addAction(self.show_current_path)## insert in MenuBar
        chrome_driver.addAction(chrome_action) ## insert in MenuBar

        
        self.show_current_path_save = QAction('현재경로 : '+ self.for_display['save'], self)
        save_path_action =  QAction('파일저장위치 설정', self)
        save_path_action.triggered.connect(self.save_dir_f)
        
        save_dir_a =  self.menubar.addMenu('파일저장위치')# MenuBar
        save_dir_a.addAction(self.show_current_path_save)## insert in MenuBar
        save_dir_a.addAction(save_path_action)## insert in MenuBar

    def chrome(self):
        fname = QFileDialog.getOpenFileName(self)  # noqa: F405 # file창 하나 열기

        self.path['driver'] = fname[0] if fname[0] !='' else self.path['driver']
        self.for_display['driver'] = (self.path['driver'][:40]+'  ...  '+self.path['driver'][-40:]) if len(self.path['driver']) > 100 else self.path['driver']
        self.show_current_path.setText('현재경로 : '+ self.for_display['driver'])

        self.update_path()
    def update_path(self):
        f = open('path.json', 'w')
        f.write(str(self.path))
        f.close()
    def save_dir_f(self):
        fname = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.path['save'] = fname if fname != '' else self.path['save']
        self.for_display['save'] = (self.path['save'][:40]+'  ...  '+self.path['save'][-40:]) if len(self.path['save']) > 100 else self.path['save']
        self.show_current_path_save.setText('현재경로 : '+ self.for_display['save'])

        self.update_path()
    def AssociatedQuery(self, funcName):
        # Query(keyword input)과 관련있는 Function들의 집합
        def Func_openFile_btn(): 
            # 실행조건 : openFile_btn이 눌렸을 때
            # 동작 : Open file & get keywords(\n기준) & append to Queryes(앞뒤 공백 제거 후)
            fname = QFileDialog.getOpenFileName(self)  # noqa: F405 # file창 하나 열기
            self.FileDIR_Browser.setPlainText(fname[0])
            if fname[0] != '':
                f = open(fname[0], 'r', encoding='utf8')
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
            self.FileDIR_Browser.setPlainText(' ' * 200)
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
            self.index_ = self.SelectKeyword_cbox.currentIndex()
            self.ViewResult_table.setRowCount(len(self.Result[self.index_][0]))
            for col in range(3):
                for row in range(len(self.Result[self.index_][col])):
                    self.ViewResult_table.setItem(row, col, QTableWidgetItem(str(self.Result[self.index_][col][row])))

        def Func_ViewResult_table_admitChanges():
            try:
                if len(self.Result) != 0:
                    for item in self.changed_item:
                        self.Result[item[0]][item[1]][item[2]] = self.ViewResult_table.item(item[2], item[1]).text()
                    self.changed_item = []
                else:
                    QMessageBox.about(self, 'INFO', '수집된 결과가 없습니다.')
            except:
                QMessageBox.about(self,'INFO','수집된 Data가 없습니다.')

        def Func_FlagEditable_chbox():
            # 실행조건 : FlagEditable_chbox의 상태가 변했을 때
            # 동작 : 체크시 해당 keyword의 result Data 수정가능
            if self.FlagEditable_chbox.isChecked():
                self.ViewResult_table.setEditTriggers(QTableWidget.DoubleClicked)  # noqa: F405
                self.changeAdmit_btn.setEnabled(True)
            else:
                self.changeAdmit_btn.setEnabled(False)
                self.ViewResult_table.setEditTriggers(QTableWidget.NoEditTriggers)  # noqa: F405

        def Func_ViewResult_table_doubleClicked():
            self.row_ = self.ViewResult_table.currentRow() 
            self.col_ = self.ViewResult_table.currentColumn() 
            self.index_ = self.SelectKeyword_cbox.currentIndex()
            if self.FlagEditable_chbox.isChecked():
                self.changed_item.append([self.index_, self.col_, self.row_])
               

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
            Func_ViewResult_table_doubleClicked if funcname == 'Func_ViewResult_table_doubleClicked' else 
            Func_ViewResult_table_admitChanges if funcname == 'Func_ViewResult_table_admitChanges' else
            None)

    def Func_activateFunc_btn(self): # 미완
        if len(self.Queryes) != 0:
            self.Result = [crawling.view(self.Queryes[i], self.path['driver']) for i in range(len(self.Queryes))]
            if self.Result[0] == 'driver_path Error':
                QMessageBox.about(self, 'Error', '크롬드라이버 경로가 잘못되었습니다.')
                self.Result = []
            else:
                for i in self.Queryes:
                    self.SelectKeyword_cbox.addItem(i)
                self.ViewResult_table.setRowCount(len(self.Result[0][0]))#어차피 길이알고자하는것 따라서 그냥 [0][0]으로 함
                for col in range(3):
                    for row in range(len(self.Result[0][col])):
                        self.ViewResult_table.setItem(row, col, QTableWidgetItem(str(self.Result[0][col][row])))
        else:
            QMessageBox.about(self, 'INFO','검색할 키워드가 존재하지 않습니다.')

    def getTime(self, slice_='second', char='-'):
        r"""
        인자 설명
        slice_ : 어디까지 표현할 것인지(day, hour, minute, second, all)
            (기본(미 설정시) : second)
        char : 구분 문자 설정, 사용불가 문자 :(\ / : * ? " < > |)
            (기본(미 설정시) : -)
        """
        if char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            raise ValueError("char must not be in ['\\', '/', ':', '*', '?', '\"', '<', '>', '|']")
        time = str(datetime.now())
        if slice_ == 'day':
            time = time[:time.index(' ')]
        elif slice_ == 'hour':
            time = time[:time.index(':')]
        elif slice_ == 'minute':
            index_ = time.index(':')
            index_ += time[index_+1:].index(':') + 1
            time = time[:index_]
        elif slice_ == 'second':
            time = time[:time.index('.')]
        elif slice_ == 'all':
            pass
        else :
            raise ValueError("slice_ must be in ['day', 'hour', 'minute', 'second', 'all']")
        time = time.replace(':', '-')
        if char != '-':
            time = time.replace('-', char)
        return time
    def Func_SaveAsFile_btn(self):
        folder_dir = self.path['save'] + '/View전체수집' if self.path['save'] != 'None' else 'View전체수집'
        Path(folder_dir).mkdir(parents=True, exist_ok=True)
        time_ = self.getTime() 
        try:
            if len(self.Result) != 0:
                for data_, keyword in zip(self.Result, self.Queryes):
                    data = {}
                    data['Rank'] = data_[3]
                    data['URL'] = data_[0]
                    data['제목'] = data_[1]
                    data['날짜'] = data_[2]
                    df = pd.DataFrame(data)
                    print('{}/{}_{}.xlsx'.format(folder_dir, keyword, time_))
                    df.to_excel('{}/{}_{}.xlsx'.format(folder_dir, keyword, time_), index=False)
                QMessageBox.about(self,'INFO','저장완료           ')
            else:
                QMessageBox.about(self,'INFO','수집된 Data가 없습니다.')
            
        except Exception as e:
            QMessageBox.about(self,'INFO','수집된 Data가 없습니다.')
            

# query(keywords) 받는 부분은 마무리됨. start버튼으로 crawling하는 부분과 그 결과 data를 얻는 부분, 선택한 keyword에 해당하는 data를 table에 나타내는 부분, 그 data를 excel로 저장하는 부분 남음(예상)

if __name__ == "__main__":
    app = QApplication(sys.argv)   # noqa: F405
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

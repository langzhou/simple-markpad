#coding=utf-8


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT,QFile,QString
import Highlighter, Constants, Model, Controller
import os, os.path,platform, subprocess,sys,re
from shutil import copy
from types import StringType



class View(QtGui.QMainWindow):
    def __init__(self):
        super(View, self).__init__()

        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.showSidebar = 1
        self.last_dir = ''
        self.Model = Model.Model()
        self.configs = self.Model.read_config('config.ini','default')

        self.isMac = False
        self.ctrlText = 'Ctrl'
        if platform.system() == "Darwin":
            self.isMac = True
            self.ctrlText = 'Cmd'  

        self.setup_css()
        self.setup_ui()



    #窗口关闭事件
    def closeEvent(self,e):  

        if not self.inputEdit.document().isModified() or self.inputEdit.toPlainText() == "":
            e.accept()
        else:            

            button=QtGui.QMessageBox.question(self,u"文档没有保存！", u"仍然要退出么？",QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)  

            if button==QtGui.QMessageBox.Ok:  
                e.accept()
            else:
                e.ignore()


    def resizeEvent(self,e):
       
        text_width= self.inputEdit.width()
        windows_width = self.width()
        if self.showSidebar == 1:
            tree_width = self.tree.width()
        else:
            tree_width = 0
        web_width=self.web.width()
        width = windows_width-tree_width-22  
        
        if width>800 and self.showSidebar!=1:
            width = 800

        self.web.setFixedWidth(width)

###########################################
    def setup_css(self):
        style_css = QFile("style/default.css")
        style_css.open(QFile.ReadOnly)
        style = QString(style_css.readAll())
        self.setStyleSheet(style)

    def setup_ui(self):

        self.hbox = QtGui.QHBoxLayout()  
        self.hbox2 = QtGui.QHBoxLayout()  

        #self.hbox.setMargin(0) 
        self.hbox.setContentsMargins(8,5,8,0)    
        widget = QtGui.QWidget()
        self.make_menu()
        self.make_sidebar()
        self.make_statusbar()
        self.make_shortcut()

        self.inputEdit = Editor()
        self.web = web()
        size = QtGui.QSizePolicy()
        size.setHorizontalPolicy(QtGui.QSizePolicy.Expanding)
        policy = QtGui.QSizePolicy.Ignored
        #self.web.setSizePolicy(policy,policy)


        self.is_test = 1

        self.hbox2.addWidget(self.web)
        self.hbox2.addWidget(self.inputEdit)

        self.hbox.addLayout(self.hbox2)
        

        widget.setLayout(self.hbox)     
        self.setCentralWidget(widget) 
        self.setWindowTitle( Constants.APP_TITLE )
        self.setWindowIcon(QtGui.QIcon('image/icon/simple-markpad.png'))     
        self.resize(800,600)
        self.show()
        self.web.close()

    def set_win_title(self,title):
        self.setWindowTitle(title)

    def make_menu(self):
        #add file menu
        self.newAction = QtGui.QAction(QtGui.QIcon(''), '&New', self)
        self.newAction.setShortcut('Ctrl+N')
        self.newAction.setStatusTip('New ('+self.ctrlText+'+N)')
   
        self.openAction = QtGui.QAction(QtGui.QIcon(''), '&Open', self)
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open file ('+self.ctrlText+'+O)')

        self.saveAction = QtGui.QAction(QtGui.QIcon(''), '&Save', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save file ('+self.ctrlText+'+S)')

        self.saveasAction = QtGui.QAction(QtGui.QIcon(''), '&Save As', self)
        self.saveasAction.setShortcut('Shift+Ctrl+S')
        self.saveasAction.setStatusTip('Save as ('+self.ctrlText+'+S)')

        self.exitAction = QtGui.QAction(QtGui.QIcon(''), '&Exit', self)        
        self.exitAction.setShortcut('Alt+F4')
        self.exitAction.setStatusTip('Exit application (Alt+F4)')
        self.exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        self.menubar = menubar

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveasAction)
        fileMenu.addAction(self.exitAction)

        # add edit menu
        self.boldAction = QtGui.QAction(QtGui.QIcon(''), '&Bold', self)        
        self.boldAction.setShortcut('Ctrl+B')
        self.boldAction.setStatusTip('Bold ('+self.ctrlText+'+B)')
        self.boldAction.triggered.connect(self.text_make_bold)
        
        self.italicAction = QtGui.QAction(QtGui.QIcon(''), '&Italic', self)        
        self.italicAction.setShortcut('Ctrl+I')
        self.italicAction.setStatusTip('Italic ('+self.ctrlText+'+I)')
        self.italicAction.triggered.connect(self.text_make_italic)

        self.linkAction = QtGui.QAction(QtGui.QIcon(''), '&Link', self)        
        self.linkAction.setShortcut('Ctrl+K')
        self.linkAction.setStatusTip('Link ('+self.ctrlText+'+K)')
        self.linkAction.triggered.connect(self.insert_link)

        self.imageAction = QtGui.QAction(QtGui.QIcon(''), '&Image', self)        
        self.imageAction.setShortcut('Ctrl+G')
        self.imageAction.setStatusTip('Image ('+self.ctrlText+'+G)')
        self.imageAction.triggered.connect(self.add_image)

        self.footnoteAction = QtGui.QAction(QtGui.QIcon(''), '&FootNote', self)        
        self.footnoteAction.setShortcut('Ctrl+E')
        self.footnoteAction.setStatusTip('FootNote ('+self.ctrlText+'+E)')
        self.footnoteAction.triggered.connect(self.add_footnote)

        editMenu = menubar.addMenu('&Edit')        
        editMenu.addAction(self.boldAction)
        editMenu.addAction(self.italicAction)
        editMenu.addAction(self.linkAction)
        editMenu.addAction(self.imageAction)
        editMenu.addAction(self.footnoteAction)


        # add action menu
        self.setProjectAction = QtGui.QAction(QtGui.QIcon(''), 'Set &Project Folder', self)
       
        self.setProjectAction.setStatusTip('Set Project Folder')
        self.setProjectAction.triggered.connect(self.set_project)

        self.exportHTMLAction = QtGui.QAction(QtGui.QIcon(''), '&Export to HTML', self)
        
        self.exportHTMLAction.setShortcut('Ctrl+H')
        self.exportHTMLAction.setStatusTip('Export to HTML ('+self.ctrlText+'+H)')

        self.previewAction = QtGui.QAction(QtGui.QIcon(''), 'Document &Preview', self)        
        self.previewAction.setShortcut('F5')
        self.previewAction.setStatusTip('Full Screen')

        self.fullscreenAction = QtGui.QAction(QtGui.QIcon(), '&FullScreen Switch', self)        
        self.fullscreenAction.setShortcut('F11')
        self.fullscreenAction.setStatusTip('Full Screen')
        self.fullscreenAction.triggered.connect(self.show_fullscreen)
        
        actionMenu = menubar.addMenu('&Action')  
        actionMenu.addAction(self.setProjectAction)        
        actionMenu.addAction(self.previewAction)        
        actionMenu.addAction(self.fullscreenAction)
        actionMenu.addAction(self.exportHTMLAction) 


        # add help menu     
        '''   
        self.syntaxAction = QtGui.QAction(QtGui.QIcon(), 'Markdown &Syntax', self)
        self.syntaxAction.setStatusTip('Markdown Syntax')
        '''
        self.aboutAction = QtGui.QAction(QtGui.QIcon(''), '&About', self)        
        self.aboutAction.setStatusTip('About')
        self.aboutAction.triggered.connect(self.dialog_about)

        helpMenu = menubar.addMenu('&Help')        
        #helpMenu.addAction(self.syntaxAction)
        helpMenu.addAction(self.aboutAction)

    def make_shortcut(self):
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Ctrl+K"), self, self.delet_block) #删除整行
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Ctrl+Delete"), self, self.delet_rest_line)  #删除该行余下内容
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Ctrl+D"), self, self.copy_current_line) #复制该行
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Ctrl+P"), self, self.show_sidebar) #复制该行
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+T"), self, self.test) 

    def test(self):
        if self.is_test == 1:
            

            self.web.show()
            self.inputEdit.close()
            self.is_test = 0 - self.is_test
        else:
            self.inputEdit.show()
            self.web.close()
            self.is_test = 0 - self.is_test       


    def set_project(self):
        a = Model.Model().read_config('config.ini','default')
  
        root_dir = QtGui.QFileDialog.getExistingDirectory(self, 'Set Project Root', "/", QtGui.QFileDialog.ShowDirsOnly)
        print( "Set Project Root to: " + root_dir )
        if root_dir:
            #更新配置文件
            Model.Model().update_config('config.ini','default','project_path',root_dir)
            self.tree.setRootIndex(self.model.setRootPath(root_dir) )
          
            project = root_dir.split('\\')
            project = project[-1]
            self.project_name.setText(project)
        else:
            return False


    def make_statusbar(self):
        self.counter = QtGui.QLabel('Ready')
        self.counter.setMinimumSize(self.counter.sizeHint())
        self.counter.setAlignment(QtCore.Qt.AlignCenter)
        self.statusBar().addWidget(self.counter,1)

    def make_sidebar(self):
        #目录浏览
        self.tree = TreeView()
        #self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.connect(self.tree,SIGNAL("customContextMenuRequested(const QPoint &)"),self.doMenu)
        

        model = QtGui.QFileSystemModel()

        self.model = model
        icon = TreeViewIcon()
        model.setIconProvider(icon)
        file_filter = QtCore.QStringList(["*.md","*.txt"] )
        model.setNameFilters(file_filter)
        model.setNameFilterDisables(False)
        model.setReadOnly(False)

        self.tree.setModel(model)
        self.tree.setRootIndex(model.setRootPath(self.configs['project_path'].decode('utf8')) )
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        self.tree.header().close()

        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(0)
        project = QtGui.QLabel(Model.Model().Project_name.decode('utf8'))
        project.setStyleSheet("font-family:Microsoft Yahei;padding:5px 10px;border-bottom:1px solid #e6e6e6;background:#f3f3f3;color:#444;font-size:14px;")

        self.project_name = project
        vbox.addWidget(project)
        vbox.addWidget(self.tree)

        self.hbox.addLayout(vbox)

############# 字数统计 ###############
    def showCounter(self,label,cn,en):          
        cn = str(cn)
        en = str(en)
        msg = label+":ZH:"+cn+"-EN:"+en
        self.counter.setText(msg)
#################################
    def show_fullscreen(self):
        if  self.isFullScreen():
            self.resize(800,600)
            self.center()
        else:
            self.showFullScreen()


    def center(self):
        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

########### 快捷键 ######################

    def show_sidebar(self):
        if self.showSidebar == 1:
            self.tree.close()
            self.project_name.close()

            self.inputEdit.setMaximumWidth(800)
            self.web.setMaximumWidth(800)
            self.showSidebar = 0 - self.showSidebar
        else:
            self.tree.show()
            self.project_name.show()
            self.inputEdit.setMaximumWidth(10000)
            self.web.setMaximumWidth(10000)
            a = self.web.sizeHint()
           
            self.showSidebar = 0 - self.showSidebar


    def delet_block(self):
        cursor = self.inputEdit.textCursor()
        cursor.select(2)
        cursor.removeSelectedText()

    def delet_rest_line(self):
        cursor = self.inputEdit.textCursor()
        position = cursor.position()
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock, QtGui.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

    def copy_current_line(self):
        cursor = self.inputEdit.textCursor()
        block = cursor.block().text()
        cursor.movePosition(QtGui.QTextCursor.EndOfBlock)
        cursor.insertText("\r\n"+block)
        self.inputEdit.setTextCursor(cursor)
############## text format ################

    def add_link(self):
        cursor = self.inputEdit.textCursor()
        p = cursor.position()
        cursor.insertText("[]()")
        p = p+1
        cursor.setPosition(p)
        self.inputEdit.setTextCursor(cursor)


    def add_image(self):
        cursor = self.inputEdit.textCursor()
        p = cursor.position()
        cursor.insertText("![]()")
        p = p+2
        cursor.setPosition(p)
        self.inputEdit.setTextCursor(cursor)

    # 引用        
    def text_make_quote(self):
        inputEdit = self.active_input()
        cursor = inputEdit.textCursor()
        textSelected = cursor.selectedText()
        cursor.insertText( "\n> "+textSelected )
    
    # 加粗
    def text_make_bold(self):
        self.format_text( "**" )    
    # 斜体    
    def text_make_italic(self):
        self.format_text( "*" )
    # 代码    
    def text_make_code(self):
        self.format_text( "`" )

    def format_text(self, character):
        
        cursor = self.inputEdit.textCursor()
        textSelected = cursor.selectedText()
        cursor.insertText( character + textSelected + character )
        if len(textSelected) == 0:
            cursor.setPosition( cursor.position() - len(character) )
            self.inputEdit.setTextCursor(cursor)

    def insert_link(self):

        link = TextDialog('<b>请输入链接：</b>',"名称","网址",'','')

        cursor = self.inputEdit.textCursor()
        p = cursor.position()
        cursor.insertText("["+link.t1+"]("+link.t2+")")
        #p = p+1
        #cursor.setPosition(p)
        #self.inputEdit.setTextCursor(cursor)

    def add_footnote(self):
        num = self.check_footnote()
        num = str(num+1)
        footnote = TextDialog('<b>请输入脚注：</b>','序号','脚注','[^'+num+']','','2')
        cursor = self.inputEdit.textCursor()
        cursor.insertText(footnote.t1)
        fn = footnote.t1 + ": " + footnote.t2
        self.inputEdit.append(fn)    

    #@pyqtSlot()
    def check_footnote(self):
        cursor = self.inputEdit.textCursor()
        position = cursor.position()
        pattern = re.compile(r'\[\^(\d+)\]')
        textContent = self.inputEdit.toPlainText()
        textContent = textContent[0:position]
        s =  unicode(textContent,'utf-8','ignore') 
        match = pattern.findall(s)
        if match:
            return len(match)
        else:
            return 0

##############通用组件
    def get_current_document_content(self):
        return unicode(self.inputEdit.toPlainText())  

    def update_status(self, status):
        
        self.statusBar().showMessage( status,5000 )

    def select_file(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Select file', "", "*.*")
        print( "Selected file: " + fname )
        if fname:
            return fname
        else:
            return False

    def save_file_picker(self):
        print self.Model.Project_path
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', self.Model.Project_path, "*.txt")
        print( "Selected file: " + fname )
        if fname:

            return fname
        else:
            return False

    def set_document(self, document):       
        self.inputEdit.setText( QtCore.QString(document) )

    def no_file_alert(self):
        QtGui.QMessageBox.warning(self, "Alert", "The file does not exist")
        
    def dialog_about(self):
        QtGui.QMessageBox.about(self, "About", "<b>Simple MarkPad</b><br><br>Version: 1.0<br>Author: Allen")        


    def question(self,title,text):
        button=QtGui.QMessageBox.question(self,title,text,QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Ok)  

        if button==QtGui.QMessageBox.Ok:  
            return True
        else:
            return False

##### Theme Class ######################################

class Theme():

    def test(self):
        pass




##### TreeView #########################################

class web(QWebView):
    def __init__(self, parent=None):  
        super(web, self).__init__(parent)


class TreeViewIcon(QtGui. QFileIconProvider):
    def __init__(self): 
        super(TreeViewIcon,self).__init__()  

        self.folder = QtGui.QIcon("icon/file-list.png")
        self.drive = QtGui.QIcon("icon/document-new1.png")
        self.default = QtGui.QIcon("image/icon/dot.png")

    def icon(self,type):
        if type == Folder:
            return self.folder
        if type == Drive:
            return self.drive
        return self.default
    def icon(self,infor):
        if infor.isDir():
            return self.folder
        if infor.isRoot():
            return self.drive
        return self.default

    def type(self,infor):
        if infor.isDir():
            return QtCore.QString("Folder")
        if infor.isRoot():
            return QtCore.QString("Drive")
        return QtCore.QString("File")

class TreeView(QtGui.QTreeView):  
    

    def __init__(self, parent=None):  
        super(TreeView, self).__init__(parent)  
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self,SIGNAL("customContextMenuRequested(const QPoint &)"),self.doMenu)


        self.connect(self, SIGNAL("doubleClicked(QModelIndex)"), self.getCurrentIndex)   #将click信号与getCurrentIndex函数绑定  


    def getCurrentIndex(self, index):  
        index = self.currentIndex()
        temp = index.sibling(index.row(),1)
        temp = self.model().itemData(temp).values()[0].toString()   
        file_path = QtGui.QFileSystemModel().filePath(index)
        self.emit(SIGNAL("sin"),file_path)

    @pyqtSlot() 
    def doMenu(self,point):

        rename = QtGui.QAction(QtGui.QIcon(''), '&rename', self)        
        rename.triggered.connect(self.rename)
        delete = QtGui.QAction(QtGui.QIcon(''), '&delete', self)        
        delete.triggered.connect(self.delete)
        idx = self.indexAt(point)
        popupmenu = QtGui.QMenu()
        #popupmenu.addAction(rename)
        popupmenu.addAction(delete)
        popupmenu.exec_(QtGui.QCursor.pos())
    
    def edit(self, index, trigger, event):
        # 禁止双击重命名
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            return False
        return QtGui.QTreeView.edit(self, index, trigger, event)


    

    def rename(self):
        index = self.currentIndex()
        self.edit(index)


    def delete(self):
        index = self.currentIndex()
        
        temp = index.sibling(index.row(),1)
        temp = self.model().itemData(temp).values()[0].toString()   
        file_path = QtGui.QFileSystemModel().filePath(index)
        file_path = unicode(file_path,'utf-8','ignore') 
        os.remove(file_path)
##### Editor Class ######################################

class Editor(QtGui.QTextEdit):
    def __init__(self, parent=None):  
        super(Editor, self).__init__(parent)




        self.model = Model.Model()
        self.configs = self.model.read_config('config.ini')

        self.set_ui()

        Highlighter.MarkdownHighlighter(self)

        self.connect(self,SIGNAL("editor_test"),self.editor_test)


    def dragEnterEvent(self, e):
        e.acceptProposedAction()
    
    def dragMoveEvent(self, e):
        e.acceptProposedAction()
    
    def dropEvent(self, e):    
        
        if e.mimeData().hasFormat('text/uri-list'):
            
            urls = e.mimeData().urls()
            local_path = urls[0].toLocalFile()
            local_path = unicode(local_path,'utf-8','ignore') #decode QString to String type
            types = local_path.split(".")
            names = local_path.split("/")
            file_type = types[-1]
            file_name = names[-1]
            file_name = file_name.replace(" ","%20")

            if self.configs['blog_url'] == '':
                url = self.configs['image_folder']
            else:
                url = self.configs['blog_url']

            if file_type in ['png','jpg']:
                if self.copy_img(local_path):
                    cursor = self.textCursor()
                    cursor.insertText("!["+file_name+"]("+ url + "/" + file_name +")")
                    self.document().setModified(True)
                   

    #copy pic to blog folder
    def copy_img(self,path):
        save_path = self.configs['image_folder'].decode('utf8')
        try:
            if not os.path.isdir(save_path):
                os.makedirs(save_path)

            copy(path,save_path)
            return True
            
        except Exception, e:
            print e 



    def set_ui(self):
        theme = self.model.read_config('theme/'+self.model.configs['editor_theme']+'.txt','editor_theme')
        self.theme = theme
        font = QtGui.QFont();
        font.setFamily( theme['font'].decode('utf-8'));
        font.setStyleHint(QtGui.QFont.Monospace);
        font.setFixedPitch(True)
        font.setPointSize(int(theme['font_size']))
        self.setFont( font )
        self.setTabStopWidth(20) 
        self.setAcceptRichText(False)
        self.setAcceptDrops(True)
        self.setFocus()
        self.setCursorWidth(2) #光标宽度
        self.setStyleSheet("background-color:"+theme['background'])

        # 设置光标颜色                
        a = self.palette()
        a.setColor(QtGui.QPalette.Text,QtGui.QColor(theme['cursor_color']))
        self.setPalette(a)         

        # set line height
        fmt = QtGui.QTextBlockFormat()
        line_height = float(theme['line_height'])*100
        fmt.setLineHeight(line_height,QtGui.QTextBlockFormat.ProportionalHeight)
        cur = self.textCursor()
        cur.setBlockFormat(fmt)
        self.setTextCursor(cur)



    # 括号自动完成
    def keyReleaseEvent(self,e):
       
        cursor = self.textCursor()
        position = cursor.position()
        if e.text() == '[':
            self.insertPlainText(']')
            cursor.setPosition(cursor.position()-1)
            self.setTextCursor(cursor)
            
        # 列表缩进
        if e.key() == 16777220:
            cursor.setPosition(cursor.position()-1)
            block = cursor.block()
            c = str(block.text()).decode('utf-8')
            
            pattern = re.compile(r'^(\-|\*|\d+\.) (.*)')
            match = pattern.findall(c)             
            if match:
                if match[0][1]:
                    if match[0][0] in ["-","*"]:
                        temp = match[0][0]
                        cursor.setPosition(cursor.position()+1)
                        cursor.insertText(temp+" ")
                    else:
                        temp = int(match[0][0].replace(".","")) + 1
                        cursor.setPosition(cursor.position()+1)
                        cursor.insertText(str(temp)+". ")
                else:
                    cursor.movePosition(QtGui.QTextCursor.StartOfBlock, QtGui.QTextCursor.KeepAnchor)
                    cursor.removeSelectedText()

    def editor_test(self):
        print "editor_test"

    def set_lingheight(self):
        block_count = self.document().blockCount()
        cursor = self.textCursor()
        cursor.movePosition(1)
        end = cursor.atEnd()
        for a in range(0,block_count):
            
            fmt = QtGui.QTextBlockFormat()
            line_height = float(self.theme['line_height'])*100
            fmt.setLineHeight(line_height,QtGui.QTextBlockFormat.ProportionalHeight)            
            cursor.setBlockFormat(fmt)
            self.setTextCursor(cursor)
            cursor.movePosition(16) 


####### 自定义组件 ##########
class TextDialog(QtGui.QDialog):
    def __init__(self,l1='',l2='',l3='',t1='',t2='',focus='',parent=None):
        super(TextDialog, self).__init__(parent)

        self.text1 = QtGui.QLineEdit()
        self.text2 = QtGui.QLineEdit()
        self.label = QtGui.QLabel()
        self.label2 = QtGui.QLabel('test1')
        self.label3 = QtGui.QLabel('test2')

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.label)

        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.label2)
        hbox1.addWidget(self.text1)
        mainLayout.addLayout(hbox1)

        hbox2 = QtGui.QHBoxLayout()
        hbox2.addWidget(self.label3)
        hbox2.addWidget(self.text2)   
        mainLayout.addLayout(hbox2)   

        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.setWindowTitle("Dialog")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.resize(300,150)
        style_css = QFile("style/dialog.css")
        style_css.open(QFile.ReadOnly)
        style = QString(style_css.readAll())
        self.setStyleSheet(style)        

        l1 = unicode(l1,'utf-8','ignore')
        l2 = unicode(l2,'utf-8','ignore')
        l3 = unicode(l3,'utf-8','ignore')

        if l1:
            self.label.setText(l1)
        if l2:
            self.label2.setText(l2)
        if l3:
            self.label3.setText(l3)
        if t1:
            self.text1.setText(t1)
        if t2:
            self.text2.setText(t2)
        
        if focus != "":
            self.text2.setFocus()

        self.exec_()


    def accept(self):       
        
        self.t1 = unicode(self.text1.text(),'utf-8','ignore')
        self.t2 = unicode(self.text2.text(),'utf-8','ignore')        
        self.close()


class WarningBox(QtGui.QDialog):
    def __init__(self,title,text,parent=None):
        super(WarningBox, self).__init__(parent)

        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(2) 
        self.msg.setWindowTitle(title)
        self.msg.setText(text)
        #msg.setInformativeText("Do you want to Quit?")
        self.resize(500,400)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg.setDefaultButton(QtGui.QMessageBox.Ok)        
            

    def show(self):
        button = self.msg.exec_()
        return False





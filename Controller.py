#coding=utf-8

import markdown, Constants,sys
from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL
from subprocess import call



class Controller():
    '''
    classdocs
    '''

    def __init__(self, view, model):
        '''
        Constructor
        '''

        self.VIEW = view
        self.MODEL = model
        self.CONTROLLER = self

        self.is_preview = 1

        reload(sys)
        sys.setdefaultencoding('utf-8')
       
        self.inputEdit = self.VIEW.inputEdit
        self.inputEdit.connect(self.inputEdit,SIGNAL("textChanged()"),self.docCount)        
        self.inputEdit.connect(self.inputEdit,SIGNAL("textChanged()"),self.show_unsaved)
        self.inputEdit.connect(self.inputEdit,SIGNAL("selectionChanged()"),self.selectionCount)
        self.inputEdit.connect(self.VIEW.tree,SIGNAL("sin"),self.treeView)
        

        self.VIEW.newAction.triggered.connect(self.new_file)
        self.VIEW.openAction.triggered.connect(self.open_file)
        self.VIEW.saveAction.triggered.connect(self.save_file)
        self.VIEW.saveasAction.triggered.connect(self.save_as)
        self.VIEW.previewAction.triggered.connect(self.preview)
        self.VIEW.exportHTMLAction.triggered.connect(self.export_html)


    def new_file(self):
        #content = self.VIEW.inputEdit.toPlainText()
        if self.MODEL.FILE_PATH == '':
            a = self.VIEW.question(u'文档发生更改',u'请先保存文档！')
            if a:
                self.save_file()
            else:
                return
        self.VIEW.inputEdit.setText("")
        self.MODEL.FILE_PATH = ""
        self.VIEW.set_win_title(Constants.APP_TITLE)
        if self.is_preview !=1:
            self.preview()



    def open_file_path(self, file_path):
        file_content = self.MODEL.get_file_content(file_path)
        '''
        if file_content:
            try:
                file_content = file_content.decode('gbk')
            except:
                file_content = file_content.decode('utf8')
        else:
            return False
        '''
              
        self.MODEL.FILE_PATH = file_path          
        
        inputEdit = self.VIEW.inputEdit
        inputEdit.css = self.MODEL.get_css()
            
        self.VIEW.set_document(file_content)
        self.VIEW.inputEdit.set_lingheight()
        self.VIEW.inputEdit.document().setModified(False)
        self.VIEW.set_win_title(file_path+' - '+ Constants.APP_TITLE)
        
        return file_path

            
    def open_file(self):

        content = self.VIEW.inputEdit.toPlainText()
        if content and self.MODEL.FILE_PATH:
            self.save_file()

        file_path = self.VIEW.select_file()
        if file_path != False:
            self.open_file_path(file_path)
            
    
    def save_file(self):
        current_document = self.VIEW.get_current_document_content()

        # 保存新文件
        if self.MODEL.FILE_PATH == '':
            file_path = self.VIEW.save_file_picker()             

            if file_path != False:
                self.MODEL.FILE_PATH = file_path
                self.MODEL.save_document_path(file_path)
                self.MODEL.write_file_content( self.MODEL.FILE_PATH, current_document )
                #self.MODEL.add_recent_document(file_path)                
                self.VIEW.update_status('Document saved to ' + self.MODEL.FILE_PATH)
                self.VIEW.inputEdit.document().setModified(False)
                self.VIEW.set_win_title(self.MODEL.FILE_PATH + ' - '+ Constants.APP_TITLE)

        else:
            self.MODEL.write_file_content( self.MODEL.FILE_PATH, current_document )
            self.VIEW.inputEdit.document().setModified(False)
            self.VIEW.set_win_title(self.MODEL.FILE_PATH + ' - '+ Constants.APP_TITLE)
            self.VIEW.update_status('Document saved to ' + self.MODEL.FILE_PATH)


    def save_as(self):
        self.MODEL.set_file_path('')
        self.save_file()


    def treeView(self,string):
        if self.MODEL.FILE_PATH != '':
            self.save_file()
        elif self.VIEW.inputEdit.toPlainText() != "":
            a = self.VIEW.question(u'新文件未保存',u'是否保存文件')
            if a == True:
                self.save_file()

        if string != self.MODEL.FILE_PATH:            
            self.open_file_path(string)

        if self.is_preview !=1:
            self.preview()
    
            

    @pyqtSlot()
    def selectionCount(self):
        cursor = self.VIEW.inputEdit.textCursor()
        text = str(cursor.selectedText())
        if text:
            count = self.MODEL.wordsCounter(text)
            self.VIEW.showCounter('<b>Selection</b>',count[0],count[1])
        else:
            self.docCount()


    @pyqtSlot()
    def docCount(self):
        textContent = self.inputEdit.toPlainText()
        count = self.MODEL.wordsCounter(textContent)
        self.VIEW.showCounter('Words',count[0],count[1])  


    def preview(self):
        if self.is_preview == 1:

            content = self.VIEW.inputEdit.toPlainText()

            html = markdown.markdown( unicode(content),extensions=['footnotes','tables'] )

            char = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
            css = self.MODEL.preview_css()
            html = char + "<style>" + css + "</style>" + html

            # add by allen
            if isinstance(html, unicode):
                html = html.encode('utf-8')
            else:
                html = html.decode('utf-8').encode('ascii')
            
            
            self.VIEW.web.setContent( html)
            self.is_preview = 0 - self.is_preview

            a = self.inputEdit.size()          
            self.inputEdit.close()
            
            w = self.inputEdit.width()
            self.VIEW.web.setFixedWidth(w)
            self.VIEW.web.show()
        else:
            self.is_preview = 0 - self.is_preview

            self.VIEW.web.close()
            self.inputEdit.show()            



    def preview1(self):
        cursor = self.inputEdit.textCursor()
        if self.is_preview == 1:
            content = self.VIEW.inputEdit.toPlainText()
            self.content = self.VIEW.inputEdit.toHtml()
            self.cursor_position = cursor.position()

            html = markdown.markdown( unicode(content),extensions=['footnotes','tables'] ) 
            char = '<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><head>'
            css = self.MODEL.preview_css()
            content = char + "<style>"+css.decode('utf-8')+"</style></head><body>" + html + "</body></html>"
            self.is_preview = 0 - self.is_preview
            self.inputEdit.setReadOnly(True)
            self.inputEdit.setHtml(content)
        else:
            self.is_preview = 0 - self.is_preview
            content = self.content
            self.inputEdit.setReadOnly(False)
            self.inputEdit.setHtml(content)
            self.inputEdit.set_lingheight()
            cursor.setPosition(self.cursor_position)
            self.inputEdit.setTextCursor(cursor)         

        

    def preview2(self):
        content = self.VIEW.inputEdit.toPlainText()
        html = markdown.markdown( unicode(content),extensions=['footnotes','tables'] )     

        # add by allen
        if isinstance(html, unicode):
            html = html.encode('utf-8')
        else:
            html = html.decode('utf-8').encode('ascii')

        char = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'

        self.VIEW.preview_browser.setContent( char + "<style>"+self.MODEL.base_css+"</style>" + html)

        self.VIEW.preview.show()
        
        
    def export_html(self):
        
        export_path = self.MODEL.FILE_PATH.replace(".txt", ".html")
        current_document = self.VIEW.get_current_document_content()

        #current_document.encode('utf-8')
        html_document = '<!doctype html><html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><body>'
        html_document += "<style type=\"text/css\">" + self.MODEL.base_css + "</style>"
        html_document += markdown.markdown( current_document,extensions=['footnotes','tables'] )
        html_document += "</body></html>"
        
        result = self.MODEL.write_file_content(export_path, html_document)
        if result == True:
            self.VIEW.update_status('File exported to ' + export_path)
            return export_path
        else:
            self.VIEW.update_status('An error occurred...')
            return None

    def show_unsaved(self):
        if self.MODEL.FILE_PATH != '':
            if self.VIEW.inputEdit.document().isModified():
                self.VIEW.set_win_title(self.MODEL.FILE_PATH + ' ●'.decode('utf8')+ ' - '+ Constants.APP_TITLE)
            else:
                self.VIEW.set_win_title(self.MODEL.FILE_PATH + ' - '+ Constants.APP_TITLE)

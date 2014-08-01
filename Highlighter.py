#coding=utf-8

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import Constants,Model

class MarkdownHighlighter(QSyntaxHighlighter):
    '''
    classdocs
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(MarkdownHighlighter, self).__init__(parent)


        configs = Model.Model().read_config('config.ini','default')
      
        configs = Model.Model().read_config('theme/'+configs['editor_theme']+'.txt','editor_theme')


        self.h1_color               = configs['h1_color']
        self.h2_color               = configs['h2_color']
        self.h3_color               = configs['h3_color']
        self.h4_color               = configs['h4_color']
        self.h5_color               = configs['h5_color']
        self.h6_color               = configs['h6_color']
        self.bold_color             = '#000'
        self.italic_color           = '#3C3C3C'
        self.link_color             = configs['link_color']
        self.code_color             = '#7C7676'
        self.anchor_color           = '#7C7676'
        self.block_quotes_color     = '#7C7676'
        self.html_entity_color      = '#7C7676'
        self.hr_color               = '#CCC'
        self.hr_back_color          = '#EFEFEF'
        self.gray                   = '#AAA'
        self.light                  =  '#898989'
        self.font_color             = configs['color']





        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = []

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]
       
     


        self.format = QTextCharFormat()
        self.format.setForeground(QColor('#343434'))

        # font 
        fontFormat = QTextCharFormat()
        fontFormat.setForeground(QColor(self.font_color))
        fontReg = QRegExp(".")
        fontReg.setMinimal(True)
        self.highlightingRules.append((fontReg,fontFormat))

        # italic        
        italicFormat = QTextCharFormat()
        italicFormat.setForeground(QColor(self.italic_color))
        italicFormat.setFontItalic(True)
        italicReg = QRegExp("\*[\s|\w]+\*")
        italicReg.setMinimal(True)
        self.highlightingRules.append((italicReg,italicFormat)) 

        # bold        
        boldFormat = QTextCharFormat()
        boldFormat.setForeground(QColor(self.bold_color))
        boldFormat.setFontWeight(25)
        boldReg = QRegExp("\*\*[\S|\s]+\*\*")
        boldReg.setMinimal(True)
        self.highlightingRules.append((boldReg,boldFormat))


        
        # h1
        h1Format = QTextCharFormat()
        h1Format.setForeground(QColor(self.h1_color))
        h1Format.setFontWeight(23)
        h1Format.setFontPointSize(int(configs['h1_size']))
        self.highlightingRules.append((QRegExp("^#.*$"),h1Format))  
       
        
        # h2
        h2Format = QTextCharFormat()
        h2Format.setForeground(QColor(self.h2_color))
        h2Format.setFontWeight(23)
        h2Format.setFontPointSize(int(configs['h2_size']))
        self.highlightingRules.append((QRegExp("^##.*$"),h2Format))
        
        # h3
        h3Format = QTextCharFormat()
        h3Format.setForeground(QColor(self.h3_color))
        h3Format.setFontWeight(23)
        h3Format.setFontPointSize(int(configs['h3_size']))
        self.highlightingRules.append((QRegExp("^###.*$"),h3Format))
        
        # h4
        h4Format = QTextCharFormat()
        h4Format.setForeground(QColor(self.h4_color))
        h4Format.setFontWeight(23)
        h4Format.setFontPointSize(int(configs['h4_size']))
        self.highlightingRules.append((QRegExp("^####.*$"),h4Format))
        
        # h5
        h5Format = QTextCharFormat()
        h5Format.setForeground(QColor(self.h5_color))
        h5Format.setFontWeight(23)
        h5Format.setFontPointSize(int(configs['h5_size']))
        self.highlightingRules.append((QRegExp("^#####.*$"),h5Format))
        
        # h6
        h6Format = QTextCharFormat()
        h6Format.setForeground(QColor(self.h6_color))
        h6Format.setFontWeight(23)
        h6Format.setFontPointSize(int(configs['h6_size']))
        self.highlightingRules.append((QRegExp("^######.*$"),h6Format))
        '''
        for i in range(0,6):
            hFormat = QTextCharFormat()
            #hFormat.setForeground(QColor(self.gray))
            font_size = [
            int(configs['h1_size']),int(configs['h2_size']),int(configs['h3_size']),
            int(configs['h4_size']),int(configs['h5_size']),int(configs['h6_size'])
            ]
            hFormat.setFontWeight(63)
            hFormat.setFontPointSize(font_size[i])
            j = str(i+1)
            self.highlightingRules.append((QRegExp("^#{"+j+"}"),hFormat))
        '''


        # hr
        hrFormat = QTextCharFormat()
        hrFormat.setForeground(QColor(self.hr_color))
        hrFormat.setFontWeight(65)
        #hrFormat.setBackground(QColor(self.hr_back_color))
        self.highlightingRules.append((QRegExp("^[\-|\*]{3,}$"),hrFormat))
        
        # link
        linkFormat = QTextCharFormat()
        linkFormat.setForeground(QColor(self.link_color))
        linkFormat.setFontUnderline(True)
        linkReg = QRegExp("<(http|www).+>")
        linkReg.setMinimal(True)
        self.highlightingRules.append((linkReg,linkFormat))
        
        # anchor
        anchorFormat = QTextCharFormat()
        anchorFormat.setForeground(QColor(self.gray))
        anchorReg = QRegExp("(\[.+\])(\(.+\))")
        anchorReg.setMinimal(True)
        self.highlightingRules.append((anchorReg,anchorFormat))

        # footnote
        footnoteFormat = QTextCharFormat()
        footnoteFormat.setForeground(QColor(self.gray))
        footnoteFormat.setFontPointSize(int(configs['font_size'])-2)
        self.highlightingRules.append((QRegExp("\[\d+\]"),footnoteFormat))

        numnoteFormat = QTextCharFormat()
        numnoteFormat.setForeground(QColor(self.gray))
        #numnoteFormat.setFontPointSize(int(configs['font_size'])-1)
        noteReg = QRegExp("\[(\^(\w|\d)+|(\S|\w)+)\]")
        noteReg.setMinimal(True)
        self.highlightingRules.append((noteReg,numnoteFormat))

        footnote2Format = QTextCharFormat()
        footnote2Format.setForeground(QColor(self.gray))
        footnote2Format.setFontPointSize(int(configs['font_size'])-2)
        self.highlightingRules.append((QRegExp("^\[\^*[\w|\d]+\]:.+"),footnote2Format))

        # list
        listFormat = QTextCharFormat()
        listFormat.setForeground(QColor(self.gray))
        self.highlightingRules.append((QRegExp("^[\*|\-] "),listFormat))       

        #code
        codeFormat = QTextCharFormat()
        codeFormat.setForeground(QColor(self.code_color))
        codeFormat.setBackground(QColor(self.hr_back_color))
        codeFormat.setFontWeight(23)
        self.highlightingRules.append((QRegExp("`.*`"),codeFormat))
        
        codeFormat2 = QTextCharFormat()
        codeFormat2.setForeground(QColor(self.code_color))
        #codeFormat2.setFontPointSize(12)
        codeFormat2.setFontWeight(23)
        self.highlightingRules.append((QRegExp("^\t.*$"),codeFormat2))
        
        # block quotes
        blockQuotesFormat = QTextCharFormat()
        blockQuotesFormat.setForeground(QColor(self.block_quotes_color))
        blockQuotesFormat.setBackground(QColor(self.hr_back_color))
        self.highlightingRules.append((QRegExp("^> .+"),blockQuotesFormat))


        
        # html entity
        htmlEntityFormat = QTextCharFormat()
        htmlEntityFormat.setForeground(QColor(self.html_entity_color))
        self.highlightingRules.append((QRegExp("&.*;"),htmlEntityFormat))



    def highlightBlock(self, text):

        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)            
            index = expression.indexIn(text)
            
            while index >= 0:

                length = expression.matchedLength()  
  
                temp = expression.pattern()
                self.setFormat(index,length,format)
                
                if temp == "\[(\^(\w|\d)+|(\S|\w)+)\]": 
                    index2 = index + 1
                    length2 = length-2
                    self.setFormat(index2,length2,self.format)

                elif temp == "\[\d+\]":
                    index2 = index + 1
                    length2 = length - 2
                    self.setFormat(index2,length2,self.format)

                elif temp == "(\[.+\])(\(.+\))":
                    len1 = len(expression.cap(1))
                    len2 = len(expression.cap(2))
                    index2 = index + 1
                    length2 = len1 - 2
                    self.setFormat(index2,length2,self.format)
                    index2 = index + len1 + 1
                    length2 = len2 - 2
                    self.setFormat(index2,length2,self.format)
                

                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

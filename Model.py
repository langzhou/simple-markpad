#coding=utf-8
import ConfigParser,re,codecs 
class Model():

    def __init__(self):
        

        

        
        self.FILE_PATH      =   ""
        self.TABS           =   [{ "path": "" }]
        self.Project_path   =   ""
        self.Project_name   =   ""

        self.get_default_config()
        self.get_project_name()
        self.load_css()

    def get_default_config(self):
        self.configs = self.read_config('config.ini','default')

    def get_project_name(self):
        project_path = self.configs['project_path']  
        self.Project_path = project_path      
        project_path = project_path.replace('/','\\')
        project_name = project_path.split('\\')
        self.Project_name = project_name[-1]

        return project_name

    # 读取配置文件
    def read_config(self,path,option='default'):
        cf = ConfigParser.ConfigParser()  
        #cf.read(path)
        cf.readfp(codecs.open(path, "r", "utf-8-sig")) 
        items = cf.options(option)
        config = dict()
        for a in items:
            b = cf.get(option,a)
            c = {a:b}
            config.update(c)
        return config

    def update_config(self,path,option,item,value):
        cf = ConfigParser.ConfigParser()  
        cf.readfp(codecs.open(path, "r", "utf-8-sig")) 
        cf.set(option,item,value)
        cf.write(open(path, "w"))

    def set_file_path(self,path=''):
        self.FILE_PATH = path

    def get_file_name(self, file_path):
        path = str(file_path)
        t = path.split("/")
        return t[ len(t)-1 ]
    
    def get_file_folder(self, file_path):
        path = file_path
        t = path.split("/")
        str = ""
        for ix in range(len(t)-1):
            str = str + t[ix] + "/"
            
        return str
    
    def is_document_present(self, file_path):
        for ix in range(len(self.TABS)):
            if self.TABS[ ix ]['path'] == file_path:
                return ix
        return -1
        
    def append_document(self, file_path):
        self.TABS.append({ "path": file_path })
        self.ACTIVE_TAB = 0
        self.set_document_path(file_path)
        
    def set_active_tab(self, index):
        self.ACTIVE_TAB = index
        self.FILE_PATH = self.TABS[0]['path']
        
    def set_document_path(self, file_path):
        self.FILE_PATH = file_path
        
    def save_document_path(self, file_path):
        self.TABS[0]['path'] = file_path
    
    def get_document_path(self):
        return self.FILE_PATH
        
    def load_css(self):
        self.base_css = self.get_file_content("theme/"+self.configs['preview_theme'])

    def set_css(self, theme_index):
        self.CURRENT_THEME = theme_index
        self.load_css()
        self.save_in_config( "current_theme", int(self.CURRENT_THEME) )
        
    def get_css(self):
        return self.base_css
        
    def get_file_content(self, filename):
        try:
            #f = open(filename, 'r')
            f = codecs.open(filename, "r", "utf-8-sig")
            return f.read()
        except Exception:
            f = codecs.open(filename, "r", "gbk")
            return f.read()
     
    def preview_css(self):
        css = self.get_file_content("theme/"+self.configs['preview_theme'])   
        return css
    
    def write_file_content(self, filename, data):
        f = open(filename, 'w')
        #f = codecs.open(filename,'w','gbk')
        f.write( str(data) )
        f.close()
        return True


    def remove_tab(self, index):
        self.TABS.pop(index)

    # 字数统计
    def wordsCounter(self,text):

        s =  unicode(text,'utf-8','ignore')         
        rx = re.compile(u"[a-zA-Z0-9_\u0392-\u03c9]+|[\u4E00-\u9FFF\u3400-\u4dbf\uf900-\ufaff\u3040-\u309f\uac00-\ud7af]+", re.UNICODE)
        result = []    

        splitted = rx.findall(s)
        cjk_len = 0
        asc_len = 0
        for w in splitted:
            if ord(w[0]) >= 12352:  # \u3040
                cjk_len += len(w)
            else:
                asc_len += 1  
        return [cjk_len,asc_len]  

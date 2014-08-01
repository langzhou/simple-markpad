#coding=utf-8

from PyQt4 import QtGui
import Model, Controller, View,time
    
def main():
    
    start = time.clock()
    app = QtGui.QApplication([])
    model = Model.Model()
    view = View.View()
    controller = Controller.Controller(view, model)
    end = time.clock()
    print "Simple MarkPad v1.0"
    print "Time Cost:",end-start
    app.exec_()


if __name__ == '__main__':
    
    main()
    
    
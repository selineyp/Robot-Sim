import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot
import sys
import re
import json
import subprocess
import collections
import traceback

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Visualization'
        #self.answersets = answersets
        #self.selections = list(range(0,len(self.answersets)))
        #self.selected = 0
        self.left = 0
        self.top = 0
        self.width = 500
        self.height = 200
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # Show widget
        self.show()


    def createTable(self):

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(4)
        ext = self.extractExtensions(self.answersets[self.selected])
        #print repr(ext)

        for i in ext['row']:
            for j in ext['column']:
                self.tableWidget.setItem(i,j, QTableWidgetItem(""))


        self.tableWidget.item(1,0).setBackground(QColor(100,100,150))
        #self.tableWidget.setCurrentCell(1,0)

        # table selection change
        self.tableWidget.doubleClicked.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


def extractExtensions(answerset):
  #print(repr(answer_set))
    field_pattern = re.compile(r'(\w+)\((\d+)\)')
    tuple_pattern = re.compile(r'(\w+)\((.*,.*)\)')#not quite working yet
    extensions = collections.defaultdict(lambda: set())
    for l in answerset:
        try:
            args = field_pattern.match(l).groups()

            head = args[0]
            rest = int(args[1])
            extensions[head].add(rest)
            if args[3]:
                rest.append(str(args[3]).strip('"'))
          #sys.stderr.write(
        #  "got head {} and rest {}\n".format(repr(head), repr(rest))
        except:
        #sys.stderr.write("exception ignored: "+traceback.format_exc())
            pass
    for l in answerset:
        try:
            args = tuple_pattern.match(l).groups()
            #print "for {} got field pattern match {}".format(l, repr(args))
            # first arg = predicate
            # second/third arg = coordinates
            # rest is taken as string if not None but " are stripped
            head = args[0]
            rest = args[1]
            extensions[head].add(rest)
            if args[3]:
              rest.append(str(args[3]).strip('"'))
        #sys.stderr.write(
        #  "got head {} and rest {}\n".format(repr(head), repr(rest))
        except:
        #sys.stderr.write("exception ignored: "+traceback.format_exc())
            pass
    print(extensions)
    return extensions


clingo = subprocess.Popen(
  "clingo --outf=2 {}".format(' '.join(sys.argv[1:])),
  shell=True, stdout=subprocess.PIPE, stderr=sys.stderr)
clingoout, clingoerr = clingo.communicate()
del clingo
clingoout = json.loads(clingoout.decode('utf-8'))
#print(repr(clingoout))
#print(repr(clingoout['Call'][0]['Witnesses']))
#print(repr(clingoout['Call'][0]['Witnesses'][0]['Value']))
witnesses = clingoout['Call'][0]['Witnesses']

display_tk([witness['Value'] for witness in witnesses])

tk.mainloop()

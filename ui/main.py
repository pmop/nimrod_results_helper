from PyQt5.QtWidgets import *


def on_open():
    print('open')


def on_save():
    print('save')


def on_quit():
    print('quit')

app = QApplication([])
window = QMainWindow()
menu_bar = QMenuBar()
file_menu = QMenu()
menu_bar.addMenu(file_menu)
window.setMenuBar(menu_bar)

# Actions
action_open = QAction("Open")
action_save = QAction("Save")
action_quit = QAction("Quit")
# Actions shortcuts
# action_open.setShortcut(QKeySequenceEdit("Ctrl + o"))
# action_save.setShortcut(QKeySequenceEdit("Ctrl + s"))
# action_quit.setShortcut(QKeySequenceEdit("Ctrl + q"))
# Actions triggers
action_quit.triggered(on_quit())
action_open.triggered(on_open())
action_save.triggered(on_save())
# Add actions to menu
file_menu.addAction(action_open)
file_menu.addAction(action_save)
file_menu.addAction(action_quit)


label = QLabel('Hello World!')
label.show()
app.exec_()
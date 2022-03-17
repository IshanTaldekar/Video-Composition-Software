import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi

class MainWindow(QDialog):

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi("vcs-gui.ui", self)

        self.file_dictionary = {
            'introduction': r'',
            'background': r'',
            'outroduction': r'',
            'transition': r'',
            'audio': r'',
            'output': r'/home/wasp/Code/Video-Composition-Software/output.mp4'
        }

        self.IntroductionBrowseButton.clicked.connect(self.browse_introduction_file)

    def browse_introduction_file(self):

        self.file_dictionary['introduction'] = self.search_video_file()
        self.IntroductionLineEdit.setText(self.file_dictionary['introduction'])

    def browse_background_file(self):

        self.file_dictionary['background'] = self.search_video_file()
        self.BackgroundLineEdit.setText(self.file_dictionary['background'])

    def browse_outroduction_file(self):

        self.file_dictionary['outroduction'] = self.search_video_file()
        self.OutroductionLineEdit.setText(self.file_dictionary['outroduction'])

    def browse_transition_file(self):

        self.file_dictionary['transition'] = self.search_video_file()
        self.TransitionLineEdit.setText(self.file_dictionary['transition'])

    def browse_audio_file(self):

        self.file_dictionary['audio'] = self.search_audio_file()
        self.AudioLineEdit.setText(self.file_dictionary['audio'])

    def search_video_file(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open File', '~/')
        return file_name[0]

    def search_audio_file(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open File', '~/')
        return file_name[0]

app = QApplication(sys.argv)
main_window = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setFixedWidth(700)
widget.setFixedHeight(900)
widget.show()
sys.exit(app.exec_())

import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QSlider, QLabel
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5 import uic
from sys import platform
from AVBuilder import *
from WordList import *


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
            'output': ''
        }

        if platform == 'wind32' or platform == 'cygwin':
            self.file_dictionary['output'] = os.getcwd() + '//output.mp4'
        elif platform == 'linux':
            self.file_dictionary['output'] = os.getcwd() + '/output.mp4'

        self.IntroductionBrowseButton.clicked.connect(self.browse_introduction_file)
        self.BackgroundBrowseButton.clicked.connect(self.browse_background_file)
        self.OutroductionBrowseButton.clicked.connect(self.browse_outroduction_file)
        self.TransitionBrowseButton.clicked.connect(self.browse_transition_file)
        self.AudioBrowseButton.clicked.connect(self.browse_audio_file)

        self.word_duration_slider = self.findChild(QSlider, "WordDurationHorizontalSlider")
        self.font_size_slider = self.findChild(QSlider, "FontSizeHorizontalSlider")

        self.word_duration_label = self.findChild(QLabel, "WordDurationLabel")
        self.font_size_label = self.findChild(QLabel, "FontSizeLabel")

        self.word_duration_slider.valueChanged.connect(self.word_duration_changed)
        self.font_size_slider.valueChanged.connect(self.font_size_changed)

        self.LoadButton.clicked.connect(self.load_files)
        self.RunButton.clicked.connect(self.run)

        self.word_visibility_duration = 10
        self.processor = None
        self.random_words = None
        self.random_word_count = 0
        self.font_size = 12

        self.random_words_generator = WordList()

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

    def validate_input_files(self):

        return self.file_dictionary['introduction'] != '' and self.file_dictionary['background'] != '' and \
               self.file_dictionary['outroduction'] != '' and self.file_dictionary['transition'] != '' and \
               self.file_dictionary['audio'] != ''

    def load_files(self):

        if not self.validate_input_files():

            '''
            TODO: Add error prompt.
            '''
            pass

        else:

            self.processor = AVBuilder(self.file_dictionary)
            audio_duration = self.processor.load()
            self.processor.set_word_visibility_duration(self.word_visibility_duration)

            self.random_word_count = int(audio_duration // self.word_visibility_duration)

            self.random_words = self.random_words_generator.get_random_words(self.random_word_count)

            self.display_random_words()

    def display_random_words(self):

        self.WordListTextEdit.clear()

        for word in self.random_words:

            self.WordListTextEdit.append(word)

    def run(self):

        self.read_word_list()
        self.processor.set_word_list(self.random_words)
        self.processor.run()

    def read_word_list(self):

        text = self.WordListTextEdit.toPlainText()
        self.random_words = text.split('\n')
        self.sanitize_random_words_list()

    def sanitize_random_words_list(self):

        while len(self.random_words) > self.random_word_count:
            self.random_words.pop()

    def word_duration_changed(self, value):

        self.word_visibility_duration = value
        self.word_duration_label.setText(str(value))

    def font_size_changed(self, value):

        if self.processor:
            self.processor.set_font_size(value)

        self.font_size_label.setText(str(value))


app = QApplication(sys.argv)
main_window = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setFixedWidth(750)
widget.setFixedHeight(900)
widget.show()
sys.exit(app.exec_())

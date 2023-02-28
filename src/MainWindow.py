import sys
import os
import threading
import time
import pickle

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QSlider, QLabel
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import uic
from sys import platform

from AVBuilder import *
from WordList import *


def threaded(fn):

    def wrapper(*args, **kwargs):

        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


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

        if platform == 'win32' or platform == 'cygwin':

            self.file_dictionary['output'] = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\output.avi'
            self.config_file_path = os.getcwd() + '\\config.p'

        elif platform == 'linux':

            self.file_dictionary['output'] = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + '/output.avi'
            self.config_file_path = os.getcwd() + '/config.p'

        self.IntroductionBrowseButton.clicked.connect(self.browse_introduction_file)
        self.BackgroundBrowseButton.clicked.connect(self.browse_background_file)
        self.OutroductionBrowseButton.clicked.connect(self.browse_outroduction_file)
        self.TransitionBrowseButton.clicked.connect(self.browse_transition_file)
        self.AudioBrowseButton.clicked.connect(self.browse_audio_file)

        self.WordDurationHorizontalSlider.valueChanged.connect(self.word_duration_slider_changed)
        self.FontSizeHorizontalSlider.valueChanged.connect(self.font_size_slider_changed)

        self.WordDurationLineEdit.textChanged.connect(self.word_duration_line_edit_changed)
        self.FontSizeLineEdit.textChanged.connect(self.font_size_line_edit_changed)

        self.LoadButton.clicked.connect(self.load_files)
        self.LoadButton.setEnabled(False)

        self.RunCancelButton.clicked.connect(self.run_cancel_handler)
        self.RunCancelButton.setEnabled(False)

        self.word_visibility_duration = 10
        self.processor = None
        self.random_word_count = 0
        self.font_size = 90

        self.random_words = None
        self.random_words_generator = WordList()

        self.runner_thread = None
        self.runner_thread_stop = False

        self.ProgressBar.setAlignment(Qt.AlignCenter)

        self.config = {}
        self.read_last_configuration()

        self.set_last_config()

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

    def browse_introduction_file(self):

        self.file_dictionary['introduction'] = self.search_video_file()
        self.IntroductionLineEdit.setText(self.file_dictionary['introduction'])

        self.config['introduction'] = self.file_dictionary['introduction']

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

    def browse_background_file(self):

        self.file_dictionary['background'] = self.search_video_file()
        self.BackgroundLineEdit.setText(self.file_dictionary['background'])

        self.config['background'] = self.file_dictionary['background']

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

    def browse_outroduction_file(self):

        self.file_dictionary['outroduction'] = self.search_video_file()
        self.OutroductionLineEdit.setText(self.file_dictionary['outroduction'])

        self.config['outroduction'] = self.file_dictionary['outroduction']

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

    def browse_transition_file(self):

        self.file_dictionary['transition'] = self.search_video_file()
        self.TransitionLineEdit.setText(self.file_dictionary['transition'])

        self.config['transition'] = self.file_dictionary['transition']

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

    def browse_audio_file(self):

        self.file_dictionary['audio'] = self.search_audio_file()
        self.AudioLineEdit.setText(self.file_dictionary['audio'])

        self.config['audio'] = self.file_dictionary['audio']

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

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

        self.ProgressBar.setValue(0)

        self.processor = AVBuilder(self.file_dictionary)
        audio_duration = self.processor.load()
        self.processor.set_word_visibility_duration(self.word_visibility_duration)

        self.random_word_count = int(audio_duration // self.word_visibility_duration)

        self.random_words = self.random_words_generator.get_random_words(self.random_word_count)

        self.display_random_words()

        self.RunCancelButton.setEnabled(True)

    def display_random_words(self):

        self.WordListTextEdit.clear()

        for word in self.random_words:

            self.WordListTextEdit.append(word)

    def run_cancel_handler(self):

        if self.RunCancelButton.text() == 'Run':

            self.runner_thread = self.run()
            self.RunCancelButton.setText('Cancel')

        else:

            if self.runner_thread is not None:

                self.runner_thread_stop = True

            self.RunCancelButton.setText('Run')
            self.RunCancelButton.setEnabled(False)

    @threaded
    def run(self):

        self.read_word_list()

        self.processor.set_word_list(self.random_words)

        self.LoadButton.setEnabled(False)

        self.write_current_configuration()

        self.processor.start()

        completed = 0

        while self.processor.is_alive():

            if self.runner_thread_stop:

                self.processor.stop()
                self.processor = None
                break

            self.ProgressBar.setValue(int(completed))
            time.sleep(1)

            if completed < 99:

                completed += 0.083

        self.runner_thread_stop = False
        self.processor = None
        self.runner_thread = None

        self.ProgressBar.setValue(100)

        self.RunCancelButton.setText('Run')
        self.RunCancelButton.setEnabled(False)
        self.LoadButton.setEnabled(True)

    def read_word_list(self):

        text = self.WordListTextEdit.toPlainText()
        self.random_words = text.split('\n')
        self.sanitize_random_words_list()

    def sanitize_random_words_list(self):
        
        while len(self.random_words) > self.random_word_count:
            self.random_words.pop()

        for word in self.random_words:
            word.strip()

    def word_duration_slider_changed(self, value):

        self.word_visibility_duration = value
        self.WordDurationLineEdit.setText(str(value))

        self.config['word-duration'] = float(value)

    def font_size_slider_changed(self, value):

        if self.processor:

            self.processor.set_font_size(value)

        self.FontSizeLineEdit.setText(str(value))

        self.config['font-size'] = float(value)

    def word_duration_line_edit_changed(self, value):

        if len(value) == 0:

            return

        self.word_visibility_duration = float(value)
        self.WordDurationHorizontalSlider.setValue(int(self.word_visibility_duration))

        self.config['word-duration'] = float(value)

    def font_size_line_edit_changed(self, value):

        if len(value) == 0:

            return

        value = int(float(value))

        if self.processor:

            self.processor.set_font_size(value)

        self.FontSizeHorizontalSlider.setValue(value)

        self.config['font-size'] = float(value)

    def read_last_configuration(self):

        file = open(self.config_file_path, 'rb')

        try:

            self.config = pickle.load(file)

        except EOFError:

            self.config = {'introduction': '',
                           'outroduction': '',
                           'background': '',
                           'transition': '',
                           'audio': '',
                           'word-duration': 10.0,
                           'font-size': 90.0}

        file.close()

    def write_current_configuration(self):

        file = open(self.config_file_path, 'wb')
        pickle.dump(self.config, file)
        file.close()

    def set_last_config(self):

        self.IntroductionLineEdit.setText(self.config['introduction'])
        self.BackgroundLineEdit.setText(self.config['background'])
        self.OutroductionLineEdit.setText(self.config['outroduction'])
        self.TransitionLineEdit.setText(self.config['transition'])
        self.AudioLineEdit.setText(self.config['audio'])

        self.WordDurationHorizontalSlider.setValue(int(self.config['word-duration']))
        self.WordDurationLineEdit.setText(str(self.config['word-duration']))

        self.FontSizeHorizontalSlider.setValue(int(self.config['font-size']))
        self.FontSizeLineEdit.setText(str(self.config['font-size']))

        self.file_dictionary['introduction'] = self.config['introduction']
        self.file_dictionary['background'] = self.config['background']
        self.file_dictionary['outroduction'] = self.config['outroduction']
        self.file_dictionary['transition'] = self.config['transition']
        self.file_dictionary['audio'] = self.config['audio']

        self.word_visibility_duration = self.config['word-duration']

        if self.processor is not None:

            self.processor.set_font_size(int(self.config['font-size']))


app = QApplication(sys.argv)
main_window = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setFixedWidth(750)
widget.setFixedHeight(900)
widget.show()
sys.exit(app.exec_())

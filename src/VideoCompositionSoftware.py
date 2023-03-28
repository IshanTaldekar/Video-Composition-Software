import sys
import os
import threading
import time
import pickle

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.QtCore import QDir
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from sys import platform

from AVBuilder import AVBuilder
from WordList import WordList

from multiprocessing.pool import ThreadPool
from Task import Task


class MainWindow(QDialog):

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi("vcs-gui.ui", self)

        self.file_dictionary = {
            'introduction': r'',
            'background': r'',
            'outroduction': r'',
            'transition': r'',
            'transition': r'',
            'audio': r'',
            'output': ''
        }

        self.file_keep_audio_status = {
            'introduction': False,
            'background': False,
            'outroduction': False,
            'transition': False,
            'audio': True
        }

        if platform == 'win32' or platform == 'cygwin':

            self.file_dictionary['output'] = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\output.mp4'
            self.config_file_path = os.getcwd() + '\\config.p'

        elif platform == 'linux':

            self.file_dictionary['output'] = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop') + '/output.mp4'
            self.config_file_path = os.getcwd() + '/config.p'

        self.IntroductionBrowseButton.clicked.connect(self.browse_introduction_file)
        self.BackgroundBrowseButton.clicked.connect(self.browse_background_file)
        self.OutroductionBrowseButton.clicked.connect(self.browse_outroduction_file)
        self.TransitionBrowseButton.clicked.connect(self.browse_transition_file)
        self.AudioBrowseButton.clicked.connect(self.browse_audio_file)

        self.IntroductionKeepAudioCheckBox.clicked.connect(self.update_introduction_keep_audio_status)
        self.BackgroundKeepAudioCheckBox.clicked.connect(self.update_background_keep_audio_status)
        self.OutroductionKeepAudioCheckBox.clicked.connect(self.update_outroduction_keep_audio_status)
        self.TransitionKeepAudioCheckBox.clicked.connect(self.update_transition_keep_audio_status)

        self.PlayBeatAtVideoStartCheckBox.clicked.connect(self.update_play_beat_at_video_start_status)
        self.UsePhoneAspectRatioCheckBox.clicked.connect(self.update_use_phone_aspect_ratio_status)
        self.GenerateIntroductionCheckBox.clicked.connect(self.update_generate_introduction_status)

        self.WordDurationHorizontalSlider.valueChanged.connect(self.word_duration_slider_changed)
        self.FontSizeHorizontalSlider.valueChanged.connect(self.font_size_slider_changed)

        self.WordDurationLineEdit.textChanged.connect(self.word_duration_line_edit_changed)
        self.FontSizeLineEdit.textChanged.connect(self.font_size_line_edit_changed)

        self.ShowRandomizedSuggestionsCheckBox.clicked.connect(self.update_show_randomized_suggestions_status)

        self.WordListTextEdit.textChanged.connect(self.user_updated_word_list)

        self.LoadButton.clicked.connect(self.load_files)
        self.LoadButton.setEnabled(False)

        self.RunCancelButton.clicked.connect(self.run_cancel_handler)
        self.RunCancelButton.setEnabled(False)

        self.BeatDropAtLineEdit.textChanged.connect(self.beat_drop_at_line_edit_changed)

        self.play_beat_at_video_start_flag = False
        self.use_phone_aspect_ratio_flag = False
        self.generate_introduction_flag = False

        self.ShowRandomizedSuggestionsCheckBox.setChecked(True)
        self.word_list_randomization_flag = True

        self.TotalWordsRequiredTextLabel.setVisible(False)
        self.TotalWordsRequiredValueLabel.setVisible(False)
        self.CurrentWordCountTextLabel.setVisible(False)
        self.CurrentWordCountValueLabel.setVisible(False)

        self.BeatDropAtLabel.setDisabled(True)
        self.BeatDropAtLineEdit.setDisabled(True)

        self.BeatDropAtLabel.setVisible(False)
        self.BeatDropAtLineEdit.setVisible(False)

        self.task = None

        if self.generate_introduction_flag:

            self.BeatDropAtLabel.setDisabled(False)
            self.BeatDropAtLineEdit.setDisabled(False)

            self.BeatDropAtLabel.setVisible(True)
            self.BeatDropAtLineEdit.setVisible(True)

        self.BackgroundKeepAudioCheckBox.setDisabled(True)
        self.BackgroundKeepAudioCheckBox.setVisible(False)

        self.word_visibility_duration = 10
        self.processor = None
        self.word_count_required = 0
        self.font_size = 90
        self.introduction_length = 0
        self.show_randomized_suggestions_flag = True
        self.current_word_count = 0

        self.last_introduction_file_name = ''

        self.prior_file_keep_audio_status = {

            'introduction': False,
            'outroduction': False,
            'transition': False

        }

        self.words = None
        self.random_words_generator = WordList()

        self.runner_thread = None
        self.runner_thread_stop = False

        self.thread_pool = ThreadPool(16)

        self.ProgressBar.setAlignment(Qt.AlignCenter)

        self.config = {}
        self.read_last_configuration()

        self.set_last_config()

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

        if self.current_word_count != self.word_count_required:

            self.TotalWordsRequiredValueLabel.setStyleSheet('color: red')
            self.CurrentWordCountValueLabel.setStyleSheet('color: black')

        else:

            self.TotalWordsRequiredValueLabel.setStyleSheet('color: green')
            self.TotalWordsRequiredValueLabel.setStyleSheet('color: green')

    def browse_introduction_file(self):

        self.file_dictionary['introduction'] = self.search_file()
        self.IntroductionLineEdit.setText(self.file_dictionary['introduction'])

        self.config['introduction'] = self.file_dictionary['introduction']

        self.set_load_and_run_button_status()

    def browse_background_file(self):

        self.file_dictionary['background'] = self.search_file()
        self.BackgroundLineEdit.setText(self.file_dictionary['background'])

        self.config['background'] = self.file_dictionary['background']

        if self.generate_introduction_flag:

            self.file_dictionary['introduction'] = self.file_dictionary['background']
            self.config['introduction'] = self.file_dictionary['introduction']

        self.set_load_and_run_button_status()

    def browse_outroduction_file(self):

        self.file_dictionary['outroduction'] = self.search_file()
        self.OutroductionLineEdit.setText(self.file_dictionary['outroduction'])

        self.config['outroduction'] = self.file_dictionary['outroduction']

        self.set_load_and_run_button_status()

    def browse_transition_file(self):

        self.file_dictionary['transition'] = self.search_file()
        self.TransitionLineEdit.setText(self.file_dictionary['transition'])

        self.config['transition'] = self.file_dictionary['transition']

        self.set_load_and_run_button_status()

    def browse_audio_file(self):

        self.file_dictionary['audio'] = self.search_file()
        self.AudioLineEdit.setText(self.file_dictionary['audio'])

        self.config['audio'] = self.file_dictionary['audio']

        self.set_load_and_run_button_status()

    def set_load_and_run_button_status(self):

        self.RunCancelButton.setEnabled(False)

        if self.validate_input_files():

            self.LoadButton.setEnabled(True)

        else:

            self.LoadButton.setEnabled(False)
            self.RunCancelButton.setEnabled(False)

    def search_file(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open File', '~/')
        return file_name[0]

    def search_save_as_file(self):

        output_file_path = QFileDialog.getSaveFileUrl(parent=self, caption='Save As',
                                                      filter='*.mp4')[0].path()

        if len(output_file_path) == 0:

            return output_file_path

        if output_file_path[-4:] != '.mp4':

            output_file_path = output_file_path + '.mp4'

        output_file_path = QDir.toNativeSeparators(output_file_path)[2:]

        return output_file_path

    def validate_input_files(self):

        if self.generate_introduction_flag and self.introduction_length == -1:

            return False

        if not self.show_randomized_suggestions_flag and self.word_count_required != -1 and\
                self.current_word_count != self.word_count_required:

            return False

        return self.file_dictionary['background'] != '' and self.file_dictionary['audio'] != ''

    def load_files(self):

        self.ProgressBar.setValue(0)

        self.processor = AVBuilder(self.file_dictionary, self.file_keep_audio_status,
                                   self.play_beat_at_video_start_flag, self.use_phone_aspect_ratio_flag,
                                   self.generate_introduction_flag, self.introduction_length)

        self.processor.set_font_size(self.font_size)

        audio_duration = self.processor.load()
        self.processor.set_word_visibility_duration(self.word_visibility_duration)

        if self.generate_introduction_flag:

            audio_duration -= self.introduction_length

        self.word_count_required = int(audio_duration // self.word_visibility_duration)

        if self.show_randomized_suggestions_flag:

            self.words = self.random_words_generator.get_random_words(self.word_count_required)
            self.display_random_words()

        else:

            self.update_word_requirement_labels()

        if self.show_randomized_suggestions_flag or (not self.show_randomized_suggestions_flag and
                                                     self.word_count_required == self.current_word_count):

            self.RunCancelButton.setEnabled(True)

    def display_random_words(self):

        self.WordListTextEdit.clear()

        for word in self.words:

            self.WordListTextEdit.append(word)

    def run_cancel_handler(self):

        if self.RunCancelButton.text() == 'Run':

            self.read_word_list()
            self.processor.set_word_list(self.words)

            output_path = self.search_save_as_file()

            if len(output_path) == 0:

                return

            self.processor.set_output_file(output_path)

            self.write_current_configuration()

            self.task = Task(self.processor)
            self.task.updated.connect(self.run)

            self.thread_pool.apply_async(self.task.video_processing_task)
            self.RunCancelButton.setText('Cancel')

        else:

            if self.task is not None:

                self.task.kill_thread = True

            self.RunCancelButton.setText('Run')
            self.RunCancelButton.setEnabled(False)

    def run(self, load_button_enabled_flag, run_button_enabled_flag, change_text_to_run_flag, progress_bar_value):

        self.LoadButton.setEnabled(load_button_enabled_flag)
        self.RunCancelButton.setEnabled(run_button_enabled_flag)

        if change_text_to_run_flag:

            self.RunCancelButton.setText('Run')

        self.ProgressBar.setValue(progress_bar_value)

    def read_word_list(self):

        text = self.WordListTextEdit.toPlainText()
        self.words = text.split('\n')
        self.sanitize_random_words_list()

        self.current_word_count = len(self.words)

        if self.current_word_count != self.word_count_required:

            self.TotalWordsRequiredValueLabel.setStyleSheet('color: red')
            self.CurrentWordCountValueLabel.setStyleSheet('color: black')

        else:

            self.TotalWordsRequiredValueLabel.setStyleSheet('color: green')
            self.CurrentWordCountValueLabel.setStyleSheet('color: green')

    def sanitize_random_words_list(self):
        
        while len(self.words) > self.word_count_required:
            self.words.pop()

        for i, word in enumerate(self.words):

            if len(word) == 0:

                self.words.pop(i)

            word.strip()

    def word_duration_slider_changed(self, value):

        self.word_visibility_duration = value
        self.WordDurationLineEdit.setText(str(value))

        self.config['word-duration'] = float(value)

        self.set_load_and_run_button_status()

    def font_size_slider_changed(self, value):

        if self.processor is not None:

            self.processor.set_font_size(value)

        self.FontSizeLineEdit.setText(str(value))

        self.config['font-size'] = float(value)

        self.set_load_and_run_button_status()

    def word_duration_line_edit_changed(self, value):

        if len(value) == 0:

            return

        self.word_visibility_duration = float(value)
        self.WordDurationHorizontalSlider.setValue(int(self.word_visibility_duration))

        self.config['word-duration'] = float(value)

        self.set_load_and_run_button_status()

    def font_size_line_edit_changed(self, value):

        if len(value) == 0:

            return

        value = int(float(value))

        if self.processor is not None:

            self.processor.set_font_size(value)

        self.FontSizeHorizontalSlider.setValue(value)

        self.config['font-size'] = float(value)

        self.set_load_and_run_button_status()

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
                           'font-size': 90.0,
                           'introduction-keep-audio': False,
                           'outroduction-keep-audio': False,
                           'transition-keep-audio': False,
                           'play-beat-at-video-start': False,
                           'use-phone-aspect-ratio': False,
                           'generate-introduction': False,
                           'keep-audio-visibility': True,
                           'show-randomized-suggestions': True}

        file.close()

    def write_current_configuration(self):

        self.config['introduction'] = self.file_dictionary['introduction']
        self.config['background'] = self.file_dictionary['background']
        self.config['outroduction'] = self.file_dictionary['outroduction']
        self.config['audio'] = self.file_dictionary['audio']
        self.config['transition'] = self.file_dictionary['transition']

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

        self.font_size = int(self.config['font-size'])

        self.play_beat_at_video_start_flag = self.config['play-beat-at-video-start']
        self.use_phone_aspect_ratio_flag = self.config['use-phone-aspect-ratio']
        self.generate_introduction_flag = self.config['generate-introduction']

        if self.generate_introduction_flag:

            self.BeatDropAtLabel.setVisible(True)
            self.BeatDropAtLineEdit.setVisible(True)

            self.BeatDropAtLabel.setDisabled(False)
            self.BeatDropAtLineEdit.setDisabled(False)

        self.file_keep_audio_status['introduction'] = self.config['introduction-keep-audio']
        self.file_keep_audio_status['outroduction'] = self.config['outroduction-keep-audio']
        self.file_keep_audio_status['transition'] = self.config['transition-keep-audio']

        self.PlayBeatAtVideoStartCheckBox.setChecked(self.play_beat_at_video_start_flag)
        self.UsePhoneAspectRatioCheckBox.setChecked(self.use_phone_aspect_ratio_flag)
        self.GenerateIntroductionCheckBox.setChecked(self.generate_introduction_flag)

        self.IntroductionKeepAudioCheckBox.setChecked(self.file_keep_audio_status['introduction'])
        self.OutroductionKeepAudioCheckBox.setChecked(self.file_keep_audio_status['outroduction'])
        self.TransitionKeepAudioCheckBox.setChecked(self.file_keep_audio_status['transition'])

        self.IntroductionKeepAudioCheckBox.setVisible(self.config['keep-audio-visibility'])
        self.OutroductionKeepAudioCheckBox.setVisible(self.config['keep-audio-visibility'])
        self.TransitionKeepAudioCheckBox.setVisible(self.config['keep-audio-visibility'])

        self.show_randomized_suggestions_flag = self.config['show-randomized-suggestions']

        self.ShowRandomizedSuggestionsCheckBox.setChecked(self.show_randomized_suggestions_flag)

        self.TotalWordsRequiredTextLabel.setVisible(not self.show_randomized_suggestions_flag)
        self.TotalWordsRequiredValueLabel.setVisible(not self.show_randomized_suggestions_flag)

        self.CurrentWordCountTextLabel.setVisible(not self.show_randomized_suggestions_flag)
        self.CurrentWordCountValueLabel.setVisible(not self.show_randomized_suggestions_flag)

    def update_introduction_keep_audio_status(self, is_checked):

        self.file_keep_audio_status['introduction'] = is_checked
        self.config['introduction-keep-audio'] = is_checked

        self.set_load_and_run_button_status()

    def update_background_keep_audio_status(self, is_checked):

        self.file_keep_audio_status['background'] = is_checked
        self.config['background-keep-audio'] = is_checked

        self.set_load_and_run_button_status()

    def update_outroduction_keep_audio_status(self, is_checked):

        self.file_keep_audio_status['outroduction'] = is_checked
        self.config['outroduction-keep-audio'] = is_checked

        self.set_load_and_run_button_status()

    def update_transition_keep_audio_status(self, is_checked):

        self.file_keep_audio_status['transition'] = is_checked
        self.config['transition-keep-audio'] = is_checked

        self.set_load_and_run_button_status()

    def update_play_beat_at_video_start_status(self, is_checked):

        if self.generate_introduction_flag:

            self.PlayBeatAtVideoStartCheckBox.setChecked(True)
            return

        self.play_beat_at_video_start_flag = is_checked
        self.config['play-beat-at-video-start'] = is_checked

        self.set_load_and_run_button_status()

    def update_use_phone_aspect_ratio_status(self, is_checked):

        self.use_phone_aspect_ratio_flag = is_checked
        self.config['use-phone-aspect-ratio'] = is_checked

        self.set_load_and_run_button_status()

    def update_generate_introduction_status(self, is_checked):

        self.generate_introduction_flag = is_checked
        self.config['generate-introduction'] = is_checked
        self.config['play-beat-at-video-start'] = is_checked

        self.introduction_length = -1

        if self.generate_introduction_flag:

            self.BeatDropAtLabel.setDisabled(False)
            self.BeatDropAtLineEdit.setDisabled(False)
            self.BeatDropAtLabel.setVisible(True)
            self.BeatDropAtLineEdit.setVisible(True)

            if self.file_dictionary['introduction'] != self.file_dictionary['background']:

                self.last_introduction_file_name = self.file_dictionary['introduction']

                for file_type in ['introduction', 'outroduction', 'transition']:

                    self.prior_file_keep_audio_status[file_type] = self.file_keep_audio_status[file_type]
                    self.file_keep_audio_status[file_type] = False

            self.config['keep-audio-visibility'] = False

            self.file_dictionary['introduction'] = self.file_dictionary['background']

            self.IntroductionKeepAudioCheckBox.setVisible(False)
            self.OutroductionKeepAudioCheckBox.setVisible(False)
            self.TransitionKeepAudioCheckBox.setVisible(False)

            self.PlayBeatAtVideoStartCheckBox.setChecked(True)
            self.play_beat_at_video_start_flag = True

        else:

            self.BeatDropAtLabel.setDisabled(True)
            self.BeatDropAtLineEdit.setDisabled(True)
            self.BeatDropAtLabel.setVisible(False)
            self.BeatDropAtLineEdit.setVisible(False)

            self.file_dictionary['introduction'] = self.last_introduction_file_name

            self.IntroductionKeepAudioCheckBox.setVisible(True)
            self.OutroductionKeepAudioCheckBox.setVisible(True)
            self.TransitionKeepAudioCheckBox.setVisible(True)

            self.IntroductionKeepAudioCheckBox.setChecked(self.prior_file_keep_audio_status['introduction'])
            self.OutroductionKeepAudioCheckBox.setChecked(self.prior_file_keep_audio_status['outroduction'])
            self.TransitionKeepAudioCheckBox.setChecked(self.prior_file_keep_audio_status['transition'])

            for file_type in ['introduction', 'outroduction', 'transition']:

                self.file_keep_audio_status[file_type] = self.prior_file_keep_audio_status[file_type]

            self.config['keep-audio-visibility'] = True

            self.PlayBeatAtVideoStartCheckBox.setChecked(False)
            self.play_beat_at_video_start_flag = False

        self.IntroductionLineEdit.setText(self.file_dictionary['introduction'])

        self.set_load_and_run_button_status()

    def beat_drop_at_line_edit_changed(self, value):

        value = float(value)

        if value < 5:

            return

        self.introduction_length = value

        self.set_load_and_run_button_status()

    def update_show_randomized_suggestions_status(self, is_checked):

        self.show_randomized_suggestions_flag = is_checked

        if self.show_randomized_suggestions_flag:

            self.TotalWordsRequiredTextLabel.setVisible(False)
            self.TotalWordsRequiredValueLabel.setVisible(False)

            self.CurrentWordCountTextLabel.setVisible(False)
            self.CurrentWordCountValueLabel.setVisible(False)

        else:

            self.TotalWordsRequiredTextLabel.setVisible(True)
            self.TotalWordsRequiredValueLabel.setVisible(True)

            self.CurrentWordCountTextLabel.setVisible(True)
            self.CurrentWordCountValueLabel.setVisible(True)

            self.update_word_requirement_labels()

        self.set_load_and_run_button_status()

    def user_updated_word_list(self):

        if self.show_randomized_suggestions_flag:

            return

        self.update_word_requirement_labels()

        self.set_load_and_run_button_status()

    def update_word_requirement_labels(self):

        self.read_word_list()

        total_words_required_value = self.word_count_required
        current_word_count_value = self.current_word_count

        self.TotalWordsRequiredValueLabel.setText(str(total_words_required_value))
        self.CurrentWordCountValueLabel.setText(str(current_word_count_value))


app = QApplication(sys.argv)
main_window = MainWindow()
widget = QtWidgets.QStackedWidget()
widget.addWidget(main_window)
widget.setFixedWidth(802)
widget.setFixedHeight(874)
widget.show()
sys.exit(app.exec_())

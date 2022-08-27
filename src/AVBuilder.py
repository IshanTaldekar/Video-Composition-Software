from moviepy.editor import *
from AudioData import *
from VideoData import *
import os


class AVBuilder:

    def __init__(self, file_paths_dictionary):

        self.file_paths_dictionary = file_paths_dictionary

        if self.file_paths_dictionary['background'] is None or self.file_paths_dictionary['audio'] is None:
            print('[AVBuilder ERROR] background or audio file were not specified.')

        if self.file_paths_dictionary['output'] is None:
            print('[WARNING] no output file location specified writing to default location.')
            self.output_file_path = os.getcwd()

        self.media_data = {
            'background': VideoData(),
            'audio': AudioData(),
            'introduction': VideoData(),
            'outroduction': VideoData(),
            'transition': VideoData()
        }

        self.output_clip = None
        self.word_list = []

        self.font_color = 'white'
        self.word_visibility_duration = 1
        self.font_size = 18

    def run(self):

        self.process_background()
        self.build()
        self.write()

    def load(self):

        for file_type in self.media_data.keys():

            if self.file_paths_dictionary[file_type] is not None:

                self.media_data[file_type].set_file_path(self.file_paths_dictionary[file_type])
                self.media_data[file_type].read()

        return self.media_data['audio'].get_duration()

    def set_word_visibility_duration(self, duration):

        self.word_visibility_duration = duration

    def set_word_list(self, word_list):

        self.word_list = word_list

    def process_background(self):

        self.media_data['background'].loop(self.media_data['audio'].get_duration())
        self.media_data['background'].set_clip(self.media_data['background'].get_clip().set_audio(self.media_data['audio'].get_clip()))

        start_time = 0

        for word in self.word_list:

            self.media_data['background'].write_text(word, duration=self.word_visibility_duration,
                                                     text_color=self.font_color, font_size=self.font_size,
                                                     start_time=start_time)
            start_time += self.word_visibility_duration

    def build(self):

        self.output_clip = concatenate_videoclips([self.media_data['introduction'].get_clip(),
                                                   self.media_data['transition'].get_clip(),
                                                   self.media_data['background'].get_clip(),
                                                   self.media_data['transition'].get_clip(),
                                                   self.media_data['outroduction'].get_clip()])

    def write(self):

        self.output_clip.write_videofile(self.file_paths_dictionary['output'], fps=30, threads=4, codec="libx264")

    def set_font_size(self, value):

        self.font_size = value


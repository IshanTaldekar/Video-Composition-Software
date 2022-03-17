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
        self.word_visibility_duration = 2
        self.font_size = 18
        self.start_time = 0

    def run(self):

        self.load()
        self.process_background()
        self.build()
        self.write()

    def load(self):

        for file_type in self.media_data.keys():

            if self.file_paths_dictionary[file_type] is not None:

                self.media_data[file_type].set_file_path(self.file_paths_dictionary[file_type])
                self.media_data[file_type].read()

        return self.media_data['audio'].get_duration()

    def set_word_list(self, word_list):

        self.word_list = word_list

    def process_background(self):

        self.media_data['background'].loop(self.media_data['audio'].get_duration())
        self.media_data['background'].set_clip(self.media_data['background'].get_clip().set_audio(self.media_data['audio'].get_clip()))

        start_time = 0

        for word in word_list:

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

        self.output_clip.write_videofile(self.file_paths_dictionary['output'])


file_dict = {

    'introduction': r'/home/wasp/Pictures/giphy.gif',
    'background': r'/home/wasp/Pictures/giphy.gif',
    'transition': r'/home/wasp/Pictures/giphy.gif',
    'outroduction': r'/home/wasp/Pictures/giphy.gif',
    'audio': r'/home/wasp/Music/sample-9s.mp3',
    'output': r'/home/wasp/Code/Video-Composition-Software/output.mp4'
}

processor = AVBuilder(file_dict)
word_list = ['Word', 'List', 'Here']
processor.set_word_list(word_list)
processor.run()

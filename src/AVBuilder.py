from moviepy.editor import *
from AudioData import *
from VideoData import *
import os
from threading import Thread, Event


class AVBuilder (Thread):

    def __init__(self, file_paths_dictionary):

        super(AVBuilder, self).__init__()

        # self.setDaemon(True)
        # self._thread_stopper = Event()

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

        self.output_clip = VideoData()
        self.word_list = []

        self.font_color = 'white'
        self.word_visibility_duration = 10
        self.font_size = 90

        self.run_order = [self.process_background, self.build, self.write]

    # def stop(self):
    #
    #     return self._thread_stopper.set()
    #
    # def is_stopped(self):
    #
    #     return self._thread_stopper.isSet()

    def run(self):

        for f in self.run_order:

            # if self.is_stopped():
            #
            #     break

            f()

        self.cleanup()

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

        self.media_data['background'].write_text(self.word_list, duration=self.word_visibility_duration,
                                                 text_color=self.font_color, font_size=self.font_size,
                                                 start_time=start_time)

    def build(self):

        self.output_clip.set_file_path(self.file_paths_dictionary['output'])

        self.output_clip.set_clip(concatenate_videoclips([self.media_data['introduction'].get_clip(),
                                                          self.media_data['transition'].get_clip(),
                                                          self.media_data['background'].get_clip(),
                                                          self.media_data['transition'].get_clip(),
                                                          self.media_data['outroduction'].get_clip()],
                                                         method='compose'))

    def write(self):

        self.output_clip.write()

    def set_font_size(self, value):

        self.font_size = value

    def cleanup(self):

        for key, component in self.media_data.items():

            component.close()





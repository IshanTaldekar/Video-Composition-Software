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
        self.delay_audio_start_duration = 0
        self.words_list = []

    def run(self):

        self.load()
        self.process_background()
        self.build()
        self.write()

    def load(self):

        self.delay_audio_start_duration = 0

        for file_type in self.media_data.keys():

            if self.file_paths_dictionary[file_type] is not None:

                self.media_data[file_type].set_file_path(self.file_paths_dictionary[file_type])
                self.media_data[file_type].read()

                if file_type == 'introduction' or file_type == 'transition':
                    self.delay_audio_start_duration += self.media_data[file_type].get_duration()

        print('duration = ', self.delay_audio_start_duration)

    def process_background(self):

        self.media_data['background'].loop(self.media_data['audio'].get_duration())
        self.media_data['background'].write_text("Hello", duration=5, font_size=20)
        self.media_data['background'].set_clip(self.media_data['background'].get_clip().set_audio(self.media_data['audio'].get_clip()))

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
processor.run()

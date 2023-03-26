from moviepy.editor import concatenate_videoclips, CompositeAudioClip
from AudioData import AudioData
from VideoData import VideoData
import os
from threading import Thread, Event


class AVBuilder (Thread):

    def __init__(self, file_paths_dictionary, file_keep_audio_status, play_beat_at_video_start_flag,
                 use_phone_aspect_ratio_flag, generate_introduction_flag, introduction_length):

        super(AVBuilder, self).__init__()

        self.setDaemon(True)
        self._thread_stopper = Event()

        self.file_paths_dictionary = file_paths_dictionary
        self.file_keep_audio_status = file_keep_audio_status

        self.play_beat_at_video_start_flag = play_beat_at_video_start_flag
        self.use_phone_aspect_ratio_flag = use_phone_aspect_ratio_flag
        self.generate_introduction_flag = generate_introduction_flag
        self.introduction_length = introduction_length

        if self.file_paths_dictionary['background'] == '' or self.file_paths_dictionary['audio'] == '':
            print('[AVBuilder ERROR] background or audio file were not specified.')

        if self.file_paths_dictionary['output'] == '':
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

        self.run_order = [self.generate_introduction, self.process_background, self.build, self.write]

    def stop(self):

        return self._thread_stopper.set()

    def is_stopped(self):

        return self._thread_stopper.isSet()

    def run(self):

        for f in self.run_order:

            if self.is_stopped():

                break

            f()

        self.cleanup()

    def load(self):

        for file_type in self.media_data.keys():

            if self.file_paths_dictionary[file_type] != '':

                self.media_data[file_type].set_file_path(self.file_paths_dictionary[file_type])

                if file_type != 'audio':

                    self.media_data[file_type].read(self.file_keep_audio_status[file_type],
                                                    self.use_phone_aspect_ratio_flag)

                else:

                    self.media_data[file_type].read()

        return self.media_data['audio'].get_duration()

    def set_word_visibility_duration(self, duration):

        self.word_visibility_duration = duration

    def set_word_list(self, word_list):

        self.word_list = word_list

    def generate_introduction(self):

        if not self.generate_introduction_flag:

            return

        loop_duration = self.introduction_length

        if self.file_paths_dictionary['transition'] != '':

            loop_duration -= self.media_data['transition'].get_duration()

        self.media_data['introduction'].loop(loop_duration)

        call_to_action_duration = (loop_duration - 3) / 2

        self.media_data['introduction'].add_text(['FREESTYLE RAP IMPROV PRACTICE', 'USE ALL WORDS ON SCREEN'],
                                                 duration=call_to_action_duration, text_color=self.font_color,
                                                 font_size=self.font_size, change_end=False)

        self.media_data['introduction'].add_text(['BEAT DROPS IN 3', 'BEAT DROPS IN 2', 'BEAT DROPS IN 1'],
                                                 duration=1, text_color=self.font_color, font_size=self.font_size,
                                                 start_time=loop_duration-3)

    def process_background(self):

        loop_duration = self.media_data['audio'].get_duration()

        if self.play_beat_at_video_start_flag:

            loop_duration -= self.introduction_length

        self.media_data['background'].loop(loop_duration)

        if not self.play_beat_at_video_start_flag:

            self.media_data['background'].add_audio(self.media_data['audio'].get_clip())

        start_time = 0

        self.media_data['background'].add_text(self.word_list, duration=self.word_visibility_duration,
                                                 text_color=self.font_color, font_size=self.font_size,
                                                 start_time=start_time)

    def build(self):

        self.output_clip.set_file_path(self.file_paths_dictionary['output'])

        final_video_clips = []

        for file_type in ['introduction', 'transition', 'background', 'transition', 'outroduction']:

            if self.file_paths_dictionary[file_type] != '':

                final_video_clips.append(self.media_data[file_type].get_clip())

        self.output_clip.set_clip(concatenate_videoclips(final_video_clips, method='compose'))

        if self.play_beat_at_video_start_flag:

            self.output_clip.add_audio(self.media_data['audio'].get_clip())

    def write(self):

        self.output_clip.write()
        self.output_clip.close()

    def set_font_size(self, value):

        self.font_size = value

    def cleanup(self):

        for key, component in self.media_data.items():

            if component.is_open():

                component.close()

    def set_output_file(self, url):

        self.file_paths_dictionary['output'] = url

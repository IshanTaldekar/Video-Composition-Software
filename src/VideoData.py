from moviepy.editor import *


class VideoData:

    def __init__(self, file_path=None):

        self.file_path = file_path
        self.clip = None

    def set_file_path(self, file_path):

        if type(file_path) != str:
            print('[VideoData ERROR] file path must be a string type.')
            self.file_path = None
            return

        self.file_path = file_path

    def read(self, no_audio_flag=False):

        if self.file_path is None:
            print('[VideoData ERROR] file path not or incorrectly specified.')
            return

        if no_audio_flag:
            self.clip = VideoFileClip(self.file_path, target_resolution=(1080, 1920)).without_audio()
        else:
            self.clip = VideoFileClip(self.file_path, target_resolution=(1080, 1920))

        if self.clip is None:
            print('[VideoData ERROR] clip could not be read.')

    def loop(self, loop_duration):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return

        if loop_duration < 0:
            print('[VideoData ERROR] Cannot loop for a negative duration.')
            return

        self.clip = self.clip.loop(duration=loop_duration)

    def set_clip(self, new_clip):

        self.clip = new_clip

    def get_duration(self):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return -1

        if self.clip.duration is None:
            self.clip = self.clip.subclip(0)

        return self.clip.duration

    def get_clip(self):

        if self.clip is None:
            print('[WARNING] clip not read.')

        return self.clip

    def add_text(self, text_list, position="center", duration=10, text_color="white", start_time=0, font_size=12):

        if self.clip is None:
            print('[WARNING] clip not read.')

        clips_list = [self.clip]

        for word in text_list:

            word_duration = duration

            if word == text_list[-1]:

                word_duration = self.clip.duration - start_time

            clips_list.append(TextClip(word.upper(), fontsize=font_size, font='DejaVu-Sans', color=text_color)
                              .set_position(position)
                              .set_duration(word_duration)
                              .set_start('00:%02d:%02d.%05d' % (int(start_time/60.0), int((start_time % 60.0)/1),
                                                                ((start_time % 60) % 1) * 100000), change_end=True))

            start_time += duration

        self.clip = CompositeVideoClip(clips_list)

    def write(self):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return

        self.clip.write_videofile(self.file_path, fps=30, threads=16, codec="mpeg4",  bitrate='50000k', verbose=False,
                                  logger=None)

    def close(self):

        self.clip.close()
        self.clip = None

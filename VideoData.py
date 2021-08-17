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

    def read(self, no_audio_flag=True):

        if self.file_path is None:
            print('[VideoData ERROR] file path not or incorrectly specified.')
            return

        if no_audio_flag:
            self.clip = VideoFileClip(self.file_path).without_audio()
        else:
            self.clip = VideoFileClip(self.file_path)

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

    def write(self, clip_name='VideoDataOutput.mp4'):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return

        self.clip.write_videofile(clip_name)

    def close(self):

        self.clip.close()
        self.clip = None

from moviepy.editor import AudioFileClip


class AudioData:

    def __init__(self):

        self.file_path = None
        self.clip = None

    def set_file_path(self, file_path):

        if file_path is None or type(file_path) != str:
            print('[AudioData ERROR] file path must be a string type.')
            return

        self.file_path = file_path

    def read(self, no_audio_flag=False):

        if self.file_path is None:
            print('[AudioData ERROR] file path not specified.')
            return

        self.clip = AudioFileClip(self.file_path)

        if self.clip is None:
            print('[AudioData ERROR] audio file could not be read.')

    def get_clip(self):

        if self.clip is None:
            print('[AudioData WARNING] audio clip is empty.')

        return self.clip

    def get_duration(self):

        if self.clip is None or self.clip.duration is None:
            print('[AudioData ERROR] audio clip is empty or duration is not available.')
            return -1

        return self.clip.duration

    def delay_start(self, delay_duration):

        if self.clip is None:
            print('[AudioData ERROR] audio clip is empty.')
            return

        self.clip = self.clip.set_start(delay_duration, True)

    def write(self, clip_name='AudioDataOutput.mp3'):

        if self.clip is None:
            print('[AudioData ERROR] audio clip is empty and cannot be written.')
            return

        self.clip.write_audiofile(clip_name)

    def close(self):

        self.clip.close()
        self.clip = None

    def is_open(self):

        return self.clip is not None
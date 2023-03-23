from moviepy.editor import *
from moviepy.video.fx.all import crop


class VideoData:

    def __init__(self, file_path=None):

        self.file_path = file_path
        self.all_clips = []
        self.clip = None

    def set_file_path(self, file_path):

        if type(file_path) != str:
            print('[VideoData ERROR] file path must be a string type.')
            self.file_path = None
            return

        self.file_path = file_path

    def read(self, keep_audio_flag=False, crop_to_phone_aspect_ratio=True):

        if self.file_path is None:
            print('[VideoData ERROR] file path not or incorrectly specified.')
            return

        if not keep_audio_flag:
            self.clip = VideoFileClip(self.file_path, target_resolution=(1080, 1920)).without_audio()
        else:
            self.clip = VideoFileClip(self.file_path, target_resolution=(1080, 1920))

        if crop_to_phone_aspect_ratio:

            (clip_width, clip_height) = self.clip.size

            crop_width = clip_height * (9 / 16)

            x1 = (clip_width - crop_width) // 2
            x2 = (clip_width + crop_width) // 2

            self.all_clips.append(self.clip)
            self.clip = crop(self.clip, x1=x1, y1=0, x2=x2, y2=clip_height)

        if self.clip is None:
            print('[VideoData ERROR] clip could not be read.')

    def loop(self, loop_duration):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return

        if loop_duration < 0:
            print('[VideoData ERROR] Cannot loop for a negative duration.')
            return

        self.all_clips.append(self.clip)
        self.clip = self.clip.loop(duration=loop_duration)

    def set_clip(self, new_clip):

        self.all_clips.append(self.clip)
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

    def add_text(self, text_list, position="center", duration=10, text_color="white", start_time=0, font_size=12,
                 change_end=True):

        if self.clip is None:
            print('[WARNING] clip not read.')

        clips_list = [self.clip]

        for word in text_list:

            word_duration = duration

            if change_end and word == text_list[-1]:

                word_duration = self.clip.duration - start_time

            clips_list.append(TextClip(word.upper(), fontsize=font_size, font='DejaVu-Sans',
                                       color=text_color, method='caption', stroke_width=10)
                              .set_position(position)
                              .set_duration(word_duration)
                              .set_start('00:%02d:%02d.%05d' % (int(start_time/60.0), int((start_time % 60.0)/1),
                                                                ((start_time % 60) % 1) * 100000), change_end=True))

            start_time += duration

        self.clip = CompositeVideoClip(clips_list)
        self.all_clips.append(clips_list)

    def write(self):

        if self.clip is None:
            print('[VideoData ERROR] No clip available.')
            return

        self.clip.write_videofile(self.file_path, fps=30, threads=8, codec='mpeg4',  bitrate='500000k', verbose=False,
                                  logger=None)

    def close(self):

        self.clip.close()

        while len(self.all_clips) > 0:

            if self.all_clips[-1] is not None:

                self.all_clips[-1].close()

            self.all_clips.pop()

        self.clip = None

    def is_open(self):

        return self.clip is not None and len(self.all_clips) == 0

    def add_audio(self, audio_clip):

        self.all_clips.append(self.clip)

        self.clip = self.clip.set_audio(audio_clip)

from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.fx.loop import loop
from pathlib import Path
from datetime import datetime

"""
Module to concatenate audio and video into a single file.
"""


class MoviePyException(Exception):
    pass


class VideoAudioMultiplexer:
    def __init__(self, video_path, audio_path, output_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path

    def multiplex(self):
        try:
            video_clip = VideoFileClip(
                self.video_path,
                target_resolution=(720, 1280),
                resize_algorithm='fast_bilinear'
            )
            audio_clip = AudioFileClip(self.audio_path)

            # Loop the video clip to match the audio duration
            video_clip = video_clip.fx(loop, duration=audio_clip.duration)

            # Set the audio of the video clip
            final_clip = video_clip.set_audio(audio_clip)
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

            final_clip_name = f'ConcatenatedVideoAudio_{current_datetime}.mp4'

            final_clip_path = Path.joinpath(
                Path(self.output_path),
                final_clip_name,
            )

            # Write the result to the output file
            final_clip.write_videofile(
                final_clip_path.absolute().as_posix(),
                codec='libx264',
                fps=25,
                audio_codec='aac',
                threads=16
            )

            # Cleaning up
            video_clip.close()
            audio_clip.close()
        except Exception as e:
            raise MoviePyException(f'Error in multiplexing audio and video files.\n{e}')

if __name__ == '__main__':
    pass

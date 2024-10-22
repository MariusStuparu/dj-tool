from moviepy.editor import VideoFileClip, AudioFileClip

class VideoAudioMultiplexer:
    def __init__(self, video_path, audio_path, output_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path

    def multiplex(self):
        try:
            video_clip = VideoFileClip(self.video_path)
            audio_clip = AudioFileClip(self.audio_path)

            # Set the audio of the video clip
            final_clip = video_clip.set_audio(audio_clip)

            # Write the result to the output file
            final_clip.write_videofile(self.output_path, codec='libx264', audio_codec='aac')
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    pass
    # video_path = 'path/to/video.mp4'
    # audio_path = 'path/to/audio.mp3'
    # output_path = 'path/to/output.mp4'
    #
    # multiplexer = VideoAudioMultiplexer(video_path, audio_path, output_path)
    # multiplexer.multiplex()
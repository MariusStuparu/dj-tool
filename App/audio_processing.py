from pydub import AudioSegment

"""
Module to extract a given portion of an audio file.
"""


class AudioProcessingError(Exception):
    pass


class AudioFileProcessing:
    START_FROM_PERCENT = 0.2
    SEGMENT_LENGTH_PERCENT = 0.25

    def __init__(self, file_path, working_dir):
        self.file_path = file_path
        self.working_dir = working_dir

    def process_track(self):
        extension = self.file_path.split('.')[-1]
        file_name_from_path = self.file_path.split('/')[-1]

        try:
            with open(file=self.file_path, mode='rb') as audio_file:
                track = AudioSegment.from_file(file=audio_file, format=extension)
                track_duration_ms = len(track)

                """ Start from 20% of the track and extract a segment of 25% of the track"""
                start_from = int(track_duration_ms * self.START_FROM_PERCENT)
                end_at = start_from + int(track_duration_ms * self.SEGMENT_LENGTH_PERCENT)
                extract_segment = track[start_from:end_at]
        except IOError as io_err:
            raise AudioProcessingError(f'Audio Processing Error: Unable to read the audio file {self.file_path}.\n{io_err}')


if __name__ == '__main__':
    pass

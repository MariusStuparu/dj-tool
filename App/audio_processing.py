from pydub import AudioSegment
from pathlib import Path
from queue import Queue

from main import MAX_QUEUE_SIZE


"""
Module to extract a given portion of an audio file.
"""

segments_queue = Queue(MAX_QUEUE_SIZE)


class AudioProcessingError(Exception):
    pass


"""
Extract audio segments from the playlist
"""
class AudioFileProcessing:
    START_FROM_PERCENT = 0.2
    SEGMENT_LENGTH_PERCENT = 0.25
    SUBFOLDER = 'segments'

    def __init__(self, file_path, working_dir):
        self.file_path = file_path
        self.working_dir = working_dir

    def process_track(self):
        extension = self.file_path.split('.')[-1]
        file_name_from_path = self.file_path.split('/')[-1]
        increment = None

        try:
            with (open(file=self.file_path, mode='rb') as audio_file):
                track = AudioSegment.from_file(file=audio_file, format=extension)
                track_duration_ms = len(track)

                """ Start from 20% of the track and extract a segment of 25% of the track"""
                start_from = int(track_duration_ms * self.START_FROM_PERCENT)
                end_at = start_from + int(track_duration_ms * self.SEGMENT_LENGTH_PERCENT)
                extract_segment = track[start_from:end_at]

                """ Check if the file already exists """
                check_file_exists = True
                while check_file_exists:
                    extract_segment_filename = Path.joinpath(
                        self.working_dir,
                        self.SUBFOLDER,
                        f'Segment{increment} {file_name_from_path}')
                    if Path.exists(extract_segment_filename):
                        increment += 1
                    else:
                        check_file_exists = False

                """ Write the segment to the working directory """
                with (open(file=extract_segment_filename, mode='wb')) as e_s:
                    extract_segment.export(e_s, format='mp3')
                    segments_queue.put(extract_segment_filename)
        except IOError as io_err:
            raise AudioProcessingError(f'Audio Processing Error: Unable to read the audio file {self.file_path}.\n{io_err}')


"""
Join extracted audio segments into a single audio file
"""
class AudioSegmentsProcessing:
    def __init__(self, working_dir):
        self.working_dir = working_dir


if __name__ == '__main__':
    pass

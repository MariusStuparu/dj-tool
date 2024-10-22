import unittest
from unittest.mock import patch, mock_open, MagicMock
from App.audio_processing import AudioFileProcessing, AudioProcessingError, segments_queue, AudioSegmentsProcessing
from pydub import AudioSegment
from pathlib import Path


class TestAudioFileProcessing(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=b'audio data')
    @patch('App.audio_processing.AudioSegment.from_file')
    @patch('App.audio_processing.Path.exists')
    @patch('App.audio_processing.Path.joinpath')
    def test_process_track(self, mock_joinpath, mock_exists, mock_from_file, mock_open):
        # Setup
        mock_exists.side_effect = [True, False]  # First check returns True, second returns False
        mock_from_file.return_value = AudioSegment.silent(duration=10000)  # 10 seconds silent audio
        mock_joinpath.return_value = Path('/fake/path/SegmentNone test.mp3')

        afp = AudioFileProcessing(file_path='/fake/path/test.mp3', working_dir='/fake/path')

        # Execute
        afp.process_track()

        # Verify
        self.assertEqual(segments_queue.qsize(), 1)
        self.assertEqual(segments_queue.get(), Path('/fake/path/SegmentNone test.mp3'))
        mock_open.assert_called_with(file='/fake/path/test.mp3', mode='rb')
        mock_from_file.assert_called_once()
        mock_joinpath.assert_called()
        mock_exists.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    def test_process_track_io_error(self, mock_open):
        # Setup
        mock_open.side_effect = IOError("Unable to read the audio file")

        afp = AudioFileProcessing(file_path='/fake/path/test.mp3', working_dir='/fake/path')

        # Execute & Verify
        with self.assertRaises(AudioProcessingError) as context:
            afp.process_track()

        self.assertIn('Audio Processing Error: Unable to read the audio file', str(context.exception))


class TestAudioSegmentsProcessing(unittest.TestCase):
    def test_initialization(self):
        asp = AudioSegmentsProcessing(working_dir='/fake/path')
        self.assertEqual(asp.working_dir, '/fake/path')


if __name__ == '__main__':
    unittest.main()
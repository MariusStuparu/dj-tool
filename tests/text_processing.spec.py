import unittest
from unittest.mock import patch, mock_open
from App.text_processing import PlaylistFileProcessing, TextProcessingException

class TestPlaylistFileProcessing(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='#EXTVDJ:track1\nfile1.mp3\n#EXTINF:123,track2\nfile2.mp3\n')
    def test_read_file(self, mock_open):
        pfp = PlaylistFileProcessing(file_path='/fake/path/playlist.m3u8')
        pfp.read_file()
        self.assertEqual(len(pfp.tracks), 2)
        self.assertEqual(pfp.tracks[0]['track_name'], 'track1')
        self.assertEqual(pfp.tracks[0]['track_file'], 'file1.mp3')
        self.assertEqual(pfp.tracks[1]['track_name'], 'track2')
        self.assertEqual(pfp.tracks[1]['track_file'], 'file2.mp3')

    @patch('builtins.open', new_callable=mock_open, read_data='#EXTVDJ:track1\nfile1.mp3\n#EXTINF:123,track2\n')
    def test_read_file_index_error(self, mock_open):
        pfp = PlaylistFileProcessing(file_path='/fake/path/playlist.m3u8')
        with self.assertRaises(TextProcessingException) as context:
            pfp.read_file()
        self.assertIn('IndexError: The playlist file is not formatted correctly.', str(context.exception))

    def test_extract_xml_data(self):
        data = PlaylistFileProcessing.extract_xml_data('<track><name>track1</name></track>')
        self.assertEqual(data, {})

    def test_extract_track_data(self):
        data = PlaylistFileProcessing.extract_track_data('123,track1')
        self.assertEqual(data['track_name'], 'track1')

if __name__ == '__main__':
    unittest.main()
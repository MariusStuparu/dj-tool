import unittest
from unittest.mock import patch, MagicMock, mock_open
from App.main import DJRegulatoryTrackChecker, MAX_QUEUE_SIZE
from tkinter import Tk
from queue import Queue

class TestDJRegulatoryTrackChecker(unittest.TestCase):

    @patch('App.main.askdirectory')
    def test_on_browse_outdir(self, mock_askdirectory):
        mock_askdirectory.return_value = '/fake/path'
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.on_browse_outdir()
        self.assertEqual(app.work_dir.get(), '/fake/path')

    @patch('App.main.askopenfilename')
    def test_on_browse_sourcefile(self, mock_askopenfilename):
        mock_askopenfilename.return_value = '/fake/path/playlist.m3u8'
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.on_browse_sourcefile()
        self.assertEqual(app.track_list.get(), '/fake/path/playlist.m3u8')

    @patch('App.main.askopenfilename')
    def test_on_browse_videofile(self, mock_askopenfilename):
        mock_askopenfilename.return_value = '/fake/path/video.mp4'
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.on_browse_videofile()
        self.assertEqual(app.dummy_video.get(), '/fake/path/video.mp4')

    @patch('builtins.open', new_callable=mock_open, read_data="work_dir='/fake/path'\ntrack_list='/fake/path/playlist.m3u8'\ndummy_video='/fake/path/video.mp4'")
    def test_load_settings(self, mock_open):
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        self.assertEqual(app.work_dir.get(), '/fake/path')
        self.assertEqual(app.track_list.get(), '/fake/path/playlist.m3u8')
        self.assertEqual(app.dummy_video.get(), '/fake/path/video.mp4')

    @patch('builtins.open', new_callable=mock_open)
    def test_on_start(self, mock_open):
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.on_start()
        mock_open.assert_called_with(file=app.settings_file, mode='w+')

    def test_interaction_onoff(self):
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.processing = True
        app.interaction_onoff()
        self.assertEqual(app.workdir_entry['state'], 'disabled')
        self.assertEqual(app.source_entry['state'], 'disabled')
        self.assertEqual(app.dummy_entry['state'], 'disabled')
        self.assertEqual(app.start_btn['state'], 'disabled')
        self.assertEqual(app.cancel_btn['state'], 'normal')

    def test_insert_text_log(self):
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.insert_text_log("Test log")
        self.assertIn("Test log", app.outlog_text.get('1.0', 'end'))

    @patch('App.main.PFP')
    @patch('App.main.Thread')
    def test_read_playlist(self, mock_thread, mock_pfp):
        mock_pfp.return_value.read_file.return_value = None
        mock_pfp.return_value.tracks = [{'track_file': '/fake/path/track1.mp3'}, {'track_file': '/fake/path/track2.mp3'}]
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.track_list.set('/fake/path/playlist.m3u8')
        app.read_playlist()
        self.assertEqual(app.tracks_count, 2)
        self.assertEqual(app.queue.qsize(), 2)

    @patch('App.main.AFP')
    @patch('App.main.Thread')
    def test_process_playlist(self, mock_thread, mock_afp):
        mock_afp.return_value.process_track.return_value = None
        root = Tk()
        app = DJRegulatoryTrackChecker(root)
        app.queue = Queue(maxsize=MAX_QUEUE_SIZE)
        app.queue.put({'track_file': '/fake/path/track1.mp3'})
        app.queue.put({'track_file': '/fake/path/track2.mp3'})
        app.processing = True
        app.process_playlist()
        self.assertTrue(mock_afp.called)

if __name__ == '__main__':
    unittest.main()
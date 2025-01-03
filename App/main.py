from pathlib import Path
from queue import Queue
from threading import Thread
import os
from platform import system as System
from subprocess import Popen
from tkinter import Tk

from tkinter.filedialog import askdirectory, askopenfilename
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from text_processing import PlaylistFileProcessing, TextProcessingException
from audio_processing import AudioFileProcessing, AudioSegmentsProcessing, AudioProcessingError
from video_processing import VideoAudioMultiplexer, MoviePyException

"""
This is a simple GUI application that checks if a list of tracks are in compliance with the DJ regulatory standards.
"""

MAX_QUEUE_SIZE = 100

PROCESS_PERCENT_READ_PLAYLIST = 5
PROCESS_PERCENT_PROCESS_PLAYLIST = 75
PROCESS_PERCENT_CONCATENATE_SEGMENTS = 85
PROCESS_PERCENT_GENERATE_VIDEO = 100

class DJRegulatoryTrackChecker(ttk.Frame):
    processing = False
    settings_path = Path().home().joinpath('.djregulatorytrackchecker')
    settings_file = settings_path.joinpath('settings.txt')

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        self.progress = 0
        self.tracks_count = 0
        self.queue = Queue(maxsize=MAX_QUEUE_SIZE)

        """ UI elements """
        self.progress_bar = None
        self.start_btn = None
        self.cancel_btn = None
        self.workdir_entry = None
        self.source_entry = None
        self.dummy_entry = None
        self.outlog_text = None

        """ Application specific variables """
        self._path = Path().absolute().as_posix()
        self.work_dir = ttk.StringVar(value=self._path)
        self.track_list = ttk.StringVar()
        self.dummy_video = ttk.StringVar()
        self.playlist = None
        self.concatenated_audio_filename = None

        """ Runtime flags """
        self.playlist_read = False
        self.playlist_processed = False

        if not self.settings_path.exists():
            self.settings_path.mkdir()

        if not self.settings_file.exists():
            with open(file=self.settings_file, mode='w+') as s_f:
                s_f.write(f"")

        """ Load settings """
        with open(file=self.settings_file, mode='r+') as s_f:
            settings_raw = s_f.readlines()
            settings = {}

            if settings_raw:
                for row in settings_raw:
                    key, value = row.split('=')
                    settings[key] = value.strip().replace("'", "")

            self.work_dir.set(settings.get('work_dir'))
            self.track_list.set(settings.get('track_list'))
            self.dummy_video.set(settings.get('dummy_video'))

        """ Display UI elements """
        self.create_output_row()
        self.create_source_row()
        self.create_video_row()
        self.create_action_row()
        self.create_outlog_row()
        self.create_progress_row()

    """
    GUI creation methods
    """

    """ Output directory row """
    def create_output_row(self):
        wd_text = "Output directory"
        wd_lf = ttk.Labelframe(self, text=wd_text, padding=15)
        wd_lf.pack(fill=X, expand=YES, anchor=N)

        workdir_row = ttk.Frame(wd_lf)
        workdir_row.pack(fill='x', expand=True, anchor=N)

        workdir_lbl = ttk.Label(master=workdir_row, text="Path", width=8)
        workdir_lbl.pack(side='left', padx=(15, 0))

        self.workdir_entry = ttk.Entry(master=workdir_row, textvariable=self.work_dir)
        self.workdir_entry.pack(side='left', fill=X, expand=True, padx=5)

        browse_btn = ttk.Button(
            master=workdir_row,
            text="Browse",
            command=self.on_browse_outdir,
            width=8,
            bootstyle='secondary'
        )
        browse_btn.pack(side='right', padx=5)

    """ Playlist file row """
    def create_source_row(self):
        src_text = "Track list file"
        src_lf = ttk.Labelframe(self, text=src_text, padding=15)
        src_lf.pack(fill=X, expand=YES, anchor=N, pady=(15, 0))

        source_row = ttk.Frame(src_lf)
        source_row.pack(fill='x', expand=True, anchor=N)

        source_lbl = ttk.Label(master=source_row, text="Playlist File", width=8)
        source_lbl.pack(side='left', padx=(15, 0))

        self.source_entry = ttk.Entry(source_row, textvariable=self.track_list)
        self.source_entry.pack(side='left', fill=X, expand=True, padx=5)

        browse_btn = ttk.Button(
            master=source_row,
            text="Browse",
            command=self.on_browse_sourcefile,
            width=8,
            bootstyle='secondary'
        )
        browse_btn.pack(side='right', padx=5)

    """ Dummy video row """
    def create_video_row(self):
        dummy_text = "Dummy video file"
        dummy_lf = ttk.Labelframe(self, text=dummy_text, padding=15)
        dummy_lf.pack(fill=X, expand=YES, anchor=N, pady=(15, 0))

        dummy_row = ttk.Frame(dummy_lf)
        dummy_row.pack(fill='x', expand=True)

        dummy_lbl = ttk.Label(master=dummy_row, text="Video File", width=8)
        dummy_lbl.pack(side='left', padx=(15, 0))

        self.dummy_entry = ttk.Entry(dummy_row, textvariable=self.dummy_video)
        self.dummy_entry.pack(side='left', fill=X, expand=True, padx=5)

        browse_btn = ttk.Button(
            master=dummy_row,
            text="Browse",
            command=self.on_browse_videofile,
            width=8,
            bootstyle='secondary'
        )
        browse_btn.pack(side='right', padx=5)

    """ Output log row """
    def create_outlog_row(self):
        log_text = "Progress log"
        log_lf = ttk.Labelframe(self, text=log_text, padding=15)
        log_lf.pack(fill=X, expand=YES, anchor=N, pady=(15, 0))

        log_row = ttk.Frame(log_lf)
        log_row.pack(fill='x', expand=True)

        self.outlog_text = ttk.ScrolledText(master=log_row, wrap=WORD, height=20)
        self.outlog_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        default_text = "First select the output directory, the playlist and the dummy video file.\n"
        self.outlog_text.insert(END, default_text)
        self.outlog_text['state'] = DISABLED

    """ Action Buttons row """
    def create_action_row(self):
        action_row = ttk.Frame()
        action_row.pack(fill='x', expand=True, padx=15, pady=(10, 10), anchor=N)
        center_buttons = ttk.Frame(action_row)
        center_buttons.pack()

        self.cancel_btn = ttk.Button(
            master=center_buttons,
            text="Cancel",
            command=self.on_cancel,
            width=12,
            state='disabled',
            bootstyle='danger'
        )
        self.cancel_btn.pack(side='left', padx=5)

        self.start_btn = ttk.Button(
            master=center_buttons,
            text="Start processing",
            command=self.on_start,
            width=12,
            bootstyle='primary'
        )
        self.start_btn.pack(side='right', padx=5)

    """ Progress bar row """
    def create_progress_row(self):
        progress_row = ttk.Frame()
        progress_row.pack(fill='x', expand=True, padx=0, pady=(10, 0), anchor=S)
        self.progress_bar = ttk.Progressbar(
            master=progress_row,
            mode=DETERMINATE,
            bootstyle=(STRIPED, SUCCESS),
            value=0,
            maximum=100,
        )
        self.progress_bar.pack(fill='x', expand=True)

    """ Enable or disable UI elements based on state """
    def interaction_onoff(self):
        self.workdir_entry['state'] = DISABLED if self.processing else NORMAL
        self.source_entry['state'] = DISABLED if self.processing else NORMAL
        self.dummy_entry['state'] = DISABLED if self.processing else NORMAL
        self.start_btn['state'] = DISABLED if self.processing else NORMAL

        self.cancel_btn['state'] = NORMAL if self.processing else DISABLED

    """ Insert text into the output log """
    def insert_text_log(self, text, clear=False):
        self.outlog_text['state'] = NORMAL
        self.outlog_text.delete('1.0', END) if clear else None
        self.outlog_text.insert(END, text)
        self.outlog_text.see(END)
        self.outlog_text['state'] = DISABLED
        Tk.update(self)

    """
    Event handlers
    """

    """ Clicked browse output directory """
    def on_browse_outdir(self):
        path = askdirectory(
            title='Select output directory',
            mustexist=True,
            initialdir=self.work_dir.get() if self.work_dir.get() else self._path
        )
        if path:
            self.work_dir.set(path)

    """ Clicked browse playlist file """
    def on_browse_sourcefile(self):
        path = askopenfilename(
            title='Select track list file',
            filetypes=[('Playlist file (UTF)', '.m3u8'), ('Playlist file', '.m3u')],
            initialdir=self.work_dir.get() if self.work_dir.get() else self._path
        )
        if path:
            self.track_list.set(path)

    """ Clicked browse dummy video file """
    def on_browse_videofile(self):
        path = askopenfilename(
            title='Select dummy video file',
            filetypes=[('MPEG video', '.mp4')],
            initialdir=self.work_dir.get() if self.work_dir.get() else self._path
        )
        if path:
            self.dummy_video.set(path)

    """ Clicked Start button """
    def on_start(self):
        self.processing = True
        self.interaction_onoff()

        with open(file=self.settings_file, mode='w+') as s_f:
            s_f.write(f"work_dir='{self.work_dir.get()}'\n")
            s_f.write(f"track_list='{self.track_list.get()}'\n")
            s_f.write(f"dummy_video='{self.dummy_video.get()}'\n")

        self.read_playlist()
        if self.playlist_read:
            self.process_playlist()
        if self.playlist_processed:
            self.insert_text_log("Joining all audio segments...\n")
            self.concatenate_segments()
        if self.concatenated_audio_filename and self.dummy_video.get():
            self.generate_video()

    """ Clicked Cancel button """
    def on_cancel(self):
        self.processing = False
        self.interaction_onoff()

    """
    Main functions
    """

    """ Read the text playlist file """
    def read_playlist(self):
        try:
            self.playlist = PlaylistFileProcessing(self.track_list.get())

            read_thread = Thread(
                target=self.playlist.read_file(),
                daemon=True
            )
            read_thread.start()
            read_thread.join()

            self.tracks_count = len(self.playlist.tracks)

            if self.tracks_count > MAX_QUEUE_SIZE:
                error_text = f"Playlist too large: {self.tracks_count} tracks." \
                             f"Please limit to {MAX_QUEUE_SIZE} tracks."
                self.insert_text_log(text=error_text)
                raise TextProcessingException(error_text)
            else:
                for item in self.playlist.tracks:
                    self.queue.put(item)

            self.insert_text_log(text=f"Playlist loaded with {self.tracks_count} tracks\n", clear=True)
            self.progress_bar['value'] = PROCESS_PERCENT_READ_PLAYLIST
        except TextProcessingException as txt_err:
            self.insert_text_log(f"ERROR: {txt_err}\n")

        self.playlist_read = True

    """ Process the playlist """
    def process_playlist(self):
        queue_length = self.queue.qsize()
        progress_increment = (PROCESS_PERCENT_PROCESS_PLAYLIST - PROCESS_PERCENT_READ_PLAYLIST) / queue_length

        while self.processing and not self.queue.empty():
            track_details = self.queue.get()
            track = AudioFileProcessing(file_path=track_details['track_file'], working_dir=self.work_dir.get())
            self.insert_text_log(f"Processing track: {track_details['track_file']}\n")
            self.progress_bar['value'] += progress_increment
            Tk.update(self)

            try:
                track.process_track()
            except AudioProcessingError as audio_err:
                self.insert_text_log(f"ERROR: {audio_err}")

        self.playlist_processed = True


    """ Join the generated segments into a single mp3 track """
    def concatenate_segments(self):
        try:
            result_queue = Queue()
            concat_audio = AudioSegmentsProcessing(self.work_dir.get())
            self.progress_bar['value'] = PROCESS_PERCENT_CONCATENATE_SEGMENTS
            Tk.update(self)
            concat_audio.concatenate_queue(result_queue)

            if not result_queue.empty():
                self.concatenated_audio_filename = result_queue.get()
        except AudioProcessingError as concat_err:
            self.insert_text_log(f"ERROR: {concat_err}")

    """ Generate the video file """
    def generate_video(self):
        self.insert_text_log("Generating video. Please be patient, it might take a while (depending on your CPU and playlist size...\n")
        try:
            mux = VideoAudioMultiplexer(
                video_path=self.dummy_video.get(),
                audio_path=self.concatenated_audio_filename,
                output_path=self.work_dir.get()
            )

            mux_thread = Thread(
                target=mux.multiplex(),
                daemon=True
            )

            mux_thread.start()
            mux_thread.join()
            self.progress_bar['value'] = PROCESS_PERCENT_GENERATE_VIDEO
            Tk.update(self)
            self.process_finished()
        except MoviePyException as mux_err:
            self.insert_text_log(f"ERROR: {mux_err}\n")
        finally:
            self.processing = False
            self.interaction_onoff()

    def process_finished(self):
        self.interaction_onoff()
        self.insert_text_log(f"All done. Opening output location...\n{self.work_dir.get()}")

        # Cross-platform open output directory
        if System() == "Windows":
            os.startfile(self.work_dir.get())
        elif System() == "Darwin":
            Popen(["open", self.work_dir.get()])
        else:
            Popen(["xdg-open", self.work_dir.get()])


""" Main loop """
if __name__ == '__main__':
    app = ttk.Window(
        title="DJ Regulatory Track Checker",
        themename="superhero",
        minsize=(800, 800),
        iconphoto="icon_512.ico"
    )
    app.place_window_center()
    DJRegulatoryTrackChecker(app)
    app.mainloop()

"""
Cassette Player main application window.

A minimal, sleek cassette player-themed UI for the audio effects application.
"""

import logging
import tkinter as tk
import threading
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING

import config
from models.transport import TransportState
from .theme import COLORS, FONTS, DIMENSIONS
from .knob_widget import create_knob
from .transport_bar import TransportBar, UtilityBar

if TYPE_CHECKING:
    from app import App

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Cassette player-themed main application window.

    Features:
    - Animated cassette tape display
    - Rotary knob controls for all parameters
    - Transport controls (play/pause/stop/loop)
    - File loading and export
    """

    def __init__(self, root: tk.Tk, app: "App"):
        """
        Initialize main window.

        Args:
            root: Tkinter root window
            app: Application instance for callbacks
        """
        self.root = root
        self.app = app

        # Window setup
        self.root.title("Cassette Player")
        self.root.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.root.minsize(550, 480)
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(True, True)

        # Build UI
        self._build_ui()

        # Start UI update timer
        self._update_interval = 100  # ms
        self._schedule_update()

        logger.info("Cassette player window initialized")

    def _build_ui(self):
        """Build the complete UI."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        self.main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # === Section 1: Track List ===
        self._create_tracks_section()

        # === Section 2: Knob Controls ===
        self._create_knobs_section()

        # === Section 3: Transport Controls ===
        self._create_transport_section()

        # === Section 4: Utility Bar ===
        self._create_utility_section()

    def _create_tracks_section(self):
        """Create the track list section."""
        self.tracks_frame = tk.Frame(self.main_frame, bg=COLORS['bg_dark'])
        self.tracks_frame.pack(fill='x', pady=(0, 10))

        # Track listbox
        self.track_listbox = tk.Listbox(
            self.tracks_frame,
            height=4,
            bg=COLORS['bg_panel'],
            fg=COLORS['text_primary'],
            selectmode=tk.MULTIPLE,
            font=FONTS['value']
        )
        self.track_listbox.pack(fill='x', padx=5, pady=5)

        # Bind selection change
        self.track_listbox.bind('<<ListboxSelect>>', self._on_track_selection_change)

        # Buttons frame
        buttons_frame = tk.Frame(self.tracks_frame, bg=COLORS['bg_dark'])
        buttons_frame.pack(fill='x')

        # Select all button
        self.select_all_btn = tk.Button(
            buttons_frame,
            text="Select All",
            command=self._on_select_all,
            bg=COLORS['button_bg'],
            fg=COLORS['button_text'],
            font=FONTS['label_small']
        )
        self.select_all_btn.pack(side='left', padx=5, pady=5)

        # Deselect all button
        self.deselect_all_btn = tk.Button(
            buttons_frame,
            text="Deselect All",
            command=self._on_deselect_all,
            bg=COLORS['button_bg'],
            fg=COLORS['button_text'],
            font=FONTS['label_small']
        )
        self.deselect_all_btn.pack(side='left', padx=5, pady=5)

        # Remove selected button
        self.remove_btn = tk.Button(
            buttons_frame,
            text="Remove Selected",
            command=self._on_remove_selected,
            bg=COLORS['button_bg'],
            fg=COLORS['button_text'],
            font=FONTS['label_small']
        )
        self.remove_btn.pack(side='left', padx=5, pady=5)

    def _on_track_selection_change(self, event):
        """Handle track listbox selection change."""
        selected_indices = self.track_listbox.curselection()
        files = self.app.get_audio_files()
        
        # Deselect all first
        self.app.deselect_all_files()
        
        # Select the chosen ones
        for index in selected_indices:
            file_id = files[index].id
            self.app.select_file(file_id)

    def _update_track_list(self):
        """Update the track list display."""
        self.track_listbox.delete(0, tk.END)
        files = self.app.get_audio_files()
        selected = self.app.get_selected_files()
        
        for i, audio_file in enumerate(files):
            display_text = f"{audio_file.filename} ({audio_file.get_metadata_string()})"
            self.track_listbox.insert(tk.END, display_text)
            
            # Select in listbox if selected in app
            if audio_file.id in selected:
                self.track_listbox.selection_set(i)

    def _on_select_all(self):
        """Select all tracks."""
        self.app.select_all_files()
        self._update_track_list()

    def _on_deselect_all(self):
        """Deselect all tracks."""
        self.app.deselect_all_files()
        self._update_track_list()

    def _on_remove_selected(self):
        """Remove selected tracks."""
        selected_indices = self.track_listbox.curselection()
        files = self.app.get_audio_files()
        
        for index in reversed(selected_indices):
            file_id = files[index].id
            self.app.remove_file(file_id)
        
        self._update_track_list()

    def _create_knobs_section(self):
        """Create the knob controls section."""
        # Panel background
        self.knobs_panel = tk.Frame(
            self.main_frame,
            bg=COLORS['bg_panel'],
            padx=20,
            pady=15,
        )
        self.knobs_panel.pack(fill='x', pady=10)

        # Row 1: Speed (large, centered)
        speed_row = tk.Frame(self.knobs_panel, bg=COLORS['bg_panel'])
        speed_row.pack(fill='x', pady=(0, 10))

        self.speed_knob = create_knob(
            speed_row,
            label="SPEED",
            min_val=config.SPEED_MIN,
            max_val=config.SPEED_MAX,
            initial_val=config.DEFAULT_SPEED,
            callback=self._on_speed_change,
            unit="x",
            size=DIMENSIONS['knob_size_large'],
            decimals=2,
        )
        self.speed_knob.pack(anchor='center')

        # Divider
        tk.Frame(
            self.knobs_panel,
            height=1,
            bg=COLORS['border_subtle'],
        ).pack(fill='x', pady=10)

        # Row 2: Echo controls
        echo_row = tk.Frame(self.knobs_panel, bg=COLORS['bg_panel'])
        echo_row.pack(fill='x', pady=5)

        # Echo label
        tk.Label(
            echo_row,
            text="ECHO",
            font=FONTS['label_small'],
            fg=COLORS['text_muted'],
            bg=COLORS['bg_panel'],
        ).pack(anchor='center', pady=(0, 5))

        # Echo knobs container
        echo_knobs = tk.Frame(echo_row, bg=COLORS['bg_panel'])
        echo_knobs.pack(anchor='center')

        self.echo_mix_knob = create_knob(
            echo_knobs,
            label="MIX",
            min_val=0.0,
            max_val=1.0,
            initial_val=config.DEFAULT_ECHO_MIX,
            callback=self._on_echo_mix_change,
            unit="%",
            size=DIMENSIONS['knob_size_small'],
            decimals=0,
        )
        self.echo_mix_knob.pack(side='left', padx=15)
        # Override formatter for percentage
        self.echo_mix_knob.formatter = lambda v: f"{int(v * 100)}%"
        self.echo_mix_knob._update_display()

        self.echo_delay_knob = create_knob(
            echo_knobs,
            label="DELAY",
            min_val=config.ECHO_DELAY_MIN_MS,
            max_val=config.ECHO_DELAY_MAX_MS,
            initial_val=config.DEFAULT_ECHO_DELAY_MS,
            callback=self._on_echo_delay_change,
            unit="ms",
            size=DIMENSIONS['knob_size_small'],
            decimals=0,
        )
        self.echo_delay_knob.pack(side='left', padx=15)

        self.echo_feedback_knob = create_knob(
            echo_knobs,
            label="FEEDBACK",
            min_val=0.0,
            max_val=config.ECHO_FEEDBACK_MAX,
            initial_val=config.DEFAULT_ECHO_FEEDBACK,
            callback=self._on_echo_feedback_change,
            unit="%",
            size=DIMENSIONS['knob_size_small'],
            decimals=0,
        )
        self.echo_feedback_knob.pack(side='left', padx=15)
        # Override formatter for percentage
        self.echo_feedback_knob.formatter = lambda v: f"{int(v * 100)}%"
        self.echo_feedback_knob._update_display()

        # Divider
        tk.Frame(
            self.knobs_panel,
            height=1,
            bg=COLORS['border_subtle'],
        ).pack(fill='x', pady=10)

        # Row 3: Output gain
        gain_row = tk.Frame(self.knobs_panel, bg=COLORS['bg_panel'])
        gain_row.pack(fill='x', pady=5)

        self.gain_knob = create_knob(
            gain_row,
            label="OUTPUT",
            min_val=config.OUTPUT_GAIN_MIN_DB,
            max_val=config.OUTPUT_GAIN_MAX_DB,
            initial_val=config.DEFAULT_OUTPUT_GAIN_DB,
            callback=self._on_gain_change,
            unit=" dB",
            size=DIMENSIONS['knob_size_medium'],
            decimals=1,
        )
        self.gain_knob.pack(anchor='center')

    def _create_transport_section(self):
        """Create the transport controls section."""
        self.transport_bar = TransportBar(
            self.main_frame,
            on_play=self._on_play,
            on_pause=self._on_pause,
            on_stop=self._on_stop,
            on_loop_toggle=self._on_loop_toggle,
        )
        self.transport_bar.pack(fill='x', pady=5)

    def _create_utility_section(self):
        """Create the utility bar section."""
        self.utility_bar = UtilityBar(
            self.main_frame,
            on_load=self._on_open_file,
            on_export=self._on_export,
            on_separate_stems=self._on_separate_stems,
            on_load_stems=self._on_load_stems,
            on_load_existing_stems=self._on_load_existing_stems,
        )
        self.utility_bar.pack(fill='x', pady=(5, 0))
        
        #Ginnie

        self.status_label = tk.Label(
            self.main_frame,
            text="",
            font=FONTS['label'],
            fg=COLORS['text_muted'],
            bg=COLORS['bg_dark'],
        )
        self.status_label.pack(pady=5)

    # === Event Handlers ===

    def _on_open_file(self):
        """Handle file open."""
        filetypes = [
            ("Audio Files", "*.wav *.flac *.ogg *.mp3 *.aiff *.aif"),
            ("WAV Files", "*.wav"),
            ("FLAC Files", "*.flac"),
            ("All Files", "*.*"),
        ]
        paths = filedialog.askopenfilenames(
            title="Load Audio Files",
            filetypes=filetypes
        )
        if paths:
            for path in paths:
                try:
                    self.app.load_file(path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load file {path}:\n{e}")
            self._update_track_list()

    def _on_play(self):
        """Handle play button."""
        self.app.play()

    def _on_pause(self):
        """Handle pause button."""
        self.app.pause()

    def _on_stop(self):
        """Handle stop button."""
        self.app.stop()

    def _on_loop_toggle(self):
        """Handle loop toggle."""
        transport = self.app.get_transport_info()
        self.app.set_loop(not transport.loop_enabled)

    def _on_speed_change(self, value: float):
        """Handle speed knob change."""
        self.app.set_parameter("speed", value)

    def _on_echo_mix_change(self, value: float):
        """Handle echo mix knob change."""
        self.app.set_parameter("echo_mix", value)

    def _on_echo_delay_change(self, value: float):
        """Handle echo delay knob change."""
        self.app.set_parameter("echo_delay_ms", value)

    def _on_echo_feedback_change(self, value: float):
        """Handle echo feedback knob change."""
        self.app.set_parameter("echo_feedback", value)

    def _on_gain_change(self, value: float):
        """Handle output gain knob change."""
        self.app.set_parameter("output_gain_db", value)

    def _on_export(self):
        """Handle export button."""
        if not self.app.has_audio_loaded():
            messagebox.showwarning("Warning", "No audio file loaded")
            return

        path = filedialog.asksaveasfilename(
            title="Export Processed Audio",
            defaultextension=".wav",
            filetypes=[("WAV Files", "*.wav")],
        )
        if not path:
            return

        try:
            self.app.export(path)
            messagebox.showinfo("Success", f"Audio exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    #Ginnie
    def _on_separate_stems(self):
        """Handle separate stems button."""
        if not self.app.has_audio_loaded():
            messagebox.showwarning("Warning", "No audio file loaded")
            return

        def run_separation():
            try:
                stems = self.app.separate_stems()
                self.root.after(0, lambda: self.status_label.config(text="✅ Stems separated!"))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Stem Separation Complete", 
                    f"Stems created:\n{chr(10).join(stems.keys())}\n\nClick 'Load Stems' to add them as tracks."
                ))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text="❌ Separation failed"))
                error_msg = str(e)
                if "FFmpeg" in error_msg or "torchcodec" in error_msg:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Stem Separation Error", 
                        f"Stem separation requires FFmpeg to be installed.\n\n"
                        f"Please download FFmpeg from: https://ffmpeg.org/download.html\n\n"
                        f"Download the 'ffmpeg-release-essentials.zip', extract it, "
                        f"and add the 'bin' folder to your system PATH.\n\n"
                        f"Alternatively, you can use online stem separation services:\n"
                        f"• Moises.ai\n"
                        f"• SplitSong.com\n"
                        f"• Lalal.ai\n\n"
                        f"Error details: {error_msg}"
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error", f"Separation failed:\n{e}"
                    ))

        self.status_label.config(text="⏳ Separating stems, please wait...")
        thread = threading.Thread(target=run_separation, daemon=True)
        thread.start()

    def _on_load_stems(self):
        """Handle load stems button."""
        try:
            self.app.load_stems_as_tracks()
            self._update_track_list()
            self.status_label.config(text="Stems loaded as individual tracks")
            messagebox.showinfo("Stems Loaded", "Separated stems have been loaded as individual tracks.")
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Load Stems Error", f"Failed to load stems:\n{e}")
    def _on_load_existing_stems(self):
        """Handle load existing stems button."""
        directory = filedialog.askdirectory(
            title="Select Separated Stem Directory"
        )
        if not directory:
            return

        try:
            self.app.load_stems_from_directory(directory)
            self._update_track_list()
            self.status_label.config(text="Existing stems loaded as tracks")
            messagebox.showinfo("Stems Loaded", "Existing separated stems have been loaded as individual tracks.")
        except Exception as e:
            self.status_label.config(text="")
            messagebox.showerror("Load Stems Error", f"Failed to load stems:\n{e}")
    def _reset_knobs(self):
        """Reset all knobs to default values."""
        self.speed_knob.set_value(config.DEFAULT_SPEED)
        self.echo_mix_knob.set_value(config.DEFAULT_ECHO_MIX)
        self.echo_delay_knob.set_value(config.DEFAULT_ECHO_DELAY_MS)
        self.echo_feedback_knob.set_value(config.DEFAULT_ECHO_FEEDBACK)
        self.gain_knob.set_value(config.DEFAULT_OUTPUT_GAIN_DB)

    # === UI Update Loop ===

    def _schedule_update(self):
        """Schedule periodic UI update."""
        self._update_ui()
        self.root.after(self._update_interval, self._schedule_update)

    def _update_ui(self):
        """Update UI with current playback state."""
        transport = self.app.get_transport_info()

        # Update track list (in case selection changed externally)
        self._update_track_list()

        # Update transport button states
        self.transport_bar.set_state(
            playing=(transport.state == TransportState.PLAYING),
            paused=(transport.state == TransportState.PAUSED),
            loop_enabled=transport.loop_enabled,
        )

        # Check for callback errors
        error = self.app.get_engine_error()
        if error:
            messagebox.showerror("Audio Error", f"Audio engine error:\n{error}")

    def run(self):
        """Start the main event loop."""
        self.root.mainloop()

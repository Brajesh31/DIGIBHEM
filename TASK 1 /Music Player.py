from tkinter import filedialog
from tkinter import *
from tkinter import ttk
import pygame
import os
import random
from mutagen.mp3 import MP3  # Import Mutagen for MP3 metadata

class MusicPlayer:
    def __init__(self, window):
        self.window = window
        self.window.title("Music Player")
        self.window.geometry('400x600')  # Adjusted window size for better visibility

        # Initialize Pygame mixer
        pygame.mixer.init()

        # Initialize variables
        self.directory = ""
        self.current_song = ""
        self.paused = False
        self.playlist = []  # To store loaded songs
        self.current_index = -1  # Index of currently playing song

        # Load external images from specified folder
        images_folder = r"C:\Users\bk117\OneDrive\Desktop\images"  # Replace with your actual path

        # Create PhotoImage objects and store references
        self.play_img = PhotoImage(file=os.path.join(images_folder, "play.png"))
        self.stop_img = PhotoImage(file=os.path.join(images_folder, "stop.png"))
        self.back_img = PhotoImage(file=os.path.join(images_folder, "back.png"))
        self.next_img = PhotoImage(file=os.path.join(images_folder, "next.png"))
        self.shuffle_img = PhotoImage(file=os.path.join(images_folder, "shuffle.png"))

        # List of colors for the heartbeat line
        self.colors = ['blue', 'red', 'green', 'yellow', 'orange', 'purple', 'cyan', 'magenta',
                       'brown', 'pink', 'light blue', 'light green', 'yellow2', 'pink2',
                       'light cyan', 'gray75', 'dark blue', 'red4', 'dark green', 'purple4']

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Menu bar
        menubar = Menu(self.window)
        self.window.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open', command=self.load_music)
        menubar.add_cascade(label="File", menu=file_menu)

        # Control frame
        control_frame = Frame(self.window)
        control_frame.pack(pady=20)

        # Define styles for themed buttons
        style = ttk.Style()
        style.configure('LightBlue.TButton', background='light blue', foreground='black')

        # Buttons
        self.play_btn = ttk.Button(control_frame, image=self.play_img, style='LightBlue.TButton', command=self.play_music)
        self.stop_btn = ttk.Button(control_frame, image=self.stop_img, style='LightBlue.TButton', command=self.stop_music, state=DISABLED)
        self.back_btn = ttk.Button(control_frame, image=self.back_img, style='LightBlue.TButton', command=self.play_previous, state=DISABLED)
        self.next_btn = ttk.Button(control_frame, image=self.next_img, style='LightBlue.TButton', command=self.play_next, state=DISABLED)
        self.shuffle_btn = ttk.Button(control_frame, image=self.shuffle_img, style='LightBlue.TButton', command=self.shuffle_music)

        self.play_btn.grid(row=0, column=0, padx=10)
        self.stop_btn.grid(row=0, column=1, padx=10)
        self.back_btn.grid(row=0, column=2, padx=10)
        self.next_btn.grid(row=0, column=3, padx=10)
        self.shuffle_btn.grid(row=0, column=4, padx=10)

        # Song listbox
        self.songlist = Listbox(self.window, bg="black", fg="white", width=60, height=15)
        self.songlist.pack(padx=20, pady=(0, 10))

        # Label to display current song
        self.current_song_label = Label(self.window, text="", font=('Helvetica', 12), bg='white', fg='black')
        self.current_song_label.pack(pady=(10, 0))

        # Canvas for heartbeat line (same width as control elements and 4 times longer in height)
        canvas_width = 400  # Adjusted width to match other large boxes
        canvas_height = 600  # Adjusted height to match other large boxes
        self.canvas = Canvas(self.window, width=canvas_width, height=canvas_height, bg='white')
        self.canvas.pack(pady=(10, 20))

        # Initialize heartbeat line (increased width by 5 times)
        line_width = 10  # Adjusted line width to be more visible
        self.heartbeat_line = self.canvas.create_line(0, 0, 0, canvas_height, fill='blue', width=line_width)

    def load_music(self):
        song = filedialog.askopenfilename(initialdir="/", title="Select Music", filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*")))
        if song:
            self.playlist.append(song)
            self.songlist.insert(END, os.path.basename(song))
            self.play_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            self.back_btn.config(state=DISABLED)
            self.next_btn.config(state=DISABLED)
            self.shuffle_btn.config(state=NORMAL)

    def play_music(self):
        if self.playlist:
            self.current_index = 0
            self.play_current_song()

    def play_next(self):
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_current_song()

    def play_previous(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.play_current_song()

    def play_current_song(self):
        pygame.mixer.music.load(self.playlist[self.current_index])
        pygame.mixer.music.play()
        self.current_song = os.path.basename(self.playlist[self.current_index])
        self.current_song_label.config(text=self.current_song)  # Update current song label
        self.window.title("Music Player - " + self.current_song)
        self.play_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.back_btn.config(state=NORMAL)
        self.next_btn.config(state=NORMAL)

        # Update button states based on current index
        if self.current_index == 0:
            self.back_btn.config(state=DISABLED)
        if self.current_index == len(self.playlist) - 1:
            self.next_btn.config(state=DISABLED)

        # Start heartbeat line animation
        self.animate_heartbeat()

    def animate_heartbeat(self):
        # Use Mutagen to get song length (in seconds)
        try:
            audio = MP3(self.playlist[self.current_index])
            song_length = audio.info.length
        except Exception as e:
            print(f"Error retrieving song length: {e}")
            return

        self.canvas.coords(self.heartbeat_line, 0, 0, 0, self.canvas.winfo_height())  # Reset line position

        def update_line_position():
            if pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos() / 1000  # Get current playback time in seconds
                progress_ratio = current_time / song_length
                line_y = int(progress_ratio * self.canvas.winfo_height())  # Calculate y-coordinate based on progress
                self.canvas.coords(self.heartbeat_line, 0, 0, self.canvas.winfo_width(), line_y)

                # Change line color based on current time
                color_index = int(current_time * 20) % len(self.colors)  # Cycle through colors
                new_color = self.colors[color_index]
                self.canvas.itemconfig(self.heartbeat_line, fill=new_color)

                self.canvas.after(1, update_line_position)  # Update every 1 millisecond for faster animation
            else:
                self.canvas.coords(self.heartbeat_line, 0, 0, 0, self.canvas.winfo_height())  # Reset line position after song ends

        update_line_position()

    def pause_music(self):
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_btn.config(state=NORMAL)
        else:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_btn.config(state=DISABLED)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.play_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.window.title("Music Player")

        # Enable back and next buttons if there are songs in the playlist
        if self.playlist:
            self.back_btn.config(state=NORMAL)
            self.next_btn.config(state=NORMAL)

        # Reset heartbeat line position
        self.canvas.coords(self.heartbeat_line, 0, 0, 0, self.canvas.winfo_height())

    def shuffle_music(self):
        random.shuffle(self.playlist)
        self.songlist.delete(0, END)
        for song in self.playlist:
            self.songlist.insert(END, os.path.basename(song))

    def clear_playlist(self):
        self.playlist = []
        self.songlist.delete(0, END)
        self.current_index = -1
        self.stop_music()
        self.shuffle_btn.config(state=DISABLED)

if __name__ == "__main__":
    window = Tk()
    music_player = MusicPlayer(window)
    window.mainloop()

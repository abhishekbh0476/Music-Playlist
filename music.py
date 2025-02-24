import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os

class Song:
    def __init__(self, title, file_path):
        self.title = title
        self.file_path = file_path
        self.prev = None
        self.next = None

class Playlist:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.history = []

    def add_song(self, title, file_path):
        if not os.path.exists(file_path):
            return False
        new_song = Song(title, file_path)
        if not self.head:
            self.head = self.tail = self.current = new_song
        else:
            self.tail.next = new_song
            new_song.prev = self.tail
            self.tail = new_song
        return True

    def delete_song(self, title):
        temp = self.head
        while temp:
            if temp.title == title:
                if temp == self.head:
                    self.head = self.head.next
                    if self.head:
                        self.head.prev = None
                if temp == self.tail:
                    self.tail = self.tail.prev
                    if self.tail:
                        self.tail.next = None
                if temp.prev:
                    temp.prev.next = temp.next
                if temp.next:
                    temp.next.prev = temp.prev
                if self.current == temp:
                    self.current = self.head if self.head else None
                del temp
                return True
            temp = temp.next
        return False

    def play_next(self):
        if self.current:
            self.history.append(self.current.title)
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.file_path
        return None

    def play_prev(self):
        if self.current:
            self.history.append(self.current.title)
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current.file_path
        return None

    def get_songs(self):
        temp = self.head
        songs = []
        while temp:
            songs.append(temp.title)
            temp = temp.next
        return songs

    def get_history(self):
        return self.history

class MusicPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Playlist")
        self.root.geometry("400x500")
        self.playlist = Playlist()
        pygame.mixer.init()

        self.song_listbox = tk.Listbox(root, width=50)
        self.song_listbox.pack(pady=10)

        self.entry_song = tk.Entry(root, width=40)
        self.entry_song.pack()

        self.entry_path = tk.Entry(root, width=40, state="readonly")
        self.entry_path.pack()

        self.browse_btn = tk.Button(root, text="Browse File", command=self.browse_file)
        self.browse_btn.pack(pady=5)

        self.add_btn = tk.Button(root, text="Add Song", command=self.add_song)
        self.add_btn.pack(pady=5)

        self.delete_btn = tk.Button(root, text="Delete Song", command=self.delete_song)
        self.delete_btn.pack(pady=5)

        # FRAME for Play, Stop, and Next in One Line
        control_frame = tk.Frame(root)
        control_frame.pack(pady=5)

        self.play_btn = tk.Button(control_frame, text="Play", command=self.play_song, width=10)
        self.play_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(control_frame, text="Stop", command=self.stop_song, width=10)
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.next_btn = tk.Button(control_frame, text="Next", command=self.play_next, width=10)
        self.next_btn.grid(row=0, column=2, padx=5)

        self.prev_btn = tk.Button(root, text="Previous", command=self.play_prev)
        self.prev_btn.pack(pady=5)

        self.history_btn = tk.Button(root, text="Show History", command=self.show_history)
        self.history_btn.pack(pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.entry_path.config(state="normal")
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, file_path)
            self.entry_path.config(state="readonly")

    def add_song(self):
        title = self.entry_song.get()
        file_path = self.entry_path.get()
        if title and file_path:
            if self.playlist.add_song(title, file_path):
                self.song_listbox.insert(tk.END, title)
                self.entry_song.delete(0, tk.END)
                self.entry_path.config(state="normal")
                self.entry_path.delete(0, tk.END)
                self.entry_path.config(state="readonly")
            else:
                messagebox.showerror("Error", "File not found. Check the path.")

    def delete_song(self):
        selected = self.song_listbox.curselection()
        if selected:
            title = self.song_listbox.get(selected[0])
            if self.playlist.delete_song(title):
                self.song_listbox.delete(selected[0])
        else:
            messagebox.showwarning("Warning", "No song selected")

    def play_song(self):
        if self.playlist.current:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.playlist.current.file_path)
                pygame.mixer.music.play()
                self.highlight_current_song()
                messagebox.showinfo("Playing", f"Now playing: {self.playlist.current.title}")
            except pygame.error:
                messagebox.showerror("Error", "Cannot play this file.")

    def stop_song(self):
        pygame.mixer.music.stop()

    def play_next(self):
        next_song = self.playlist.play_next()
        if next_song:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(next_song)
                pygame.mixer.music.play()
                self.highlight_current_song()
                messagebox.showinfo("Next Song", f"Now playing: {self.playlist.current.title}")
            except pygame.error:
                messagebox.showerror("Error", "Cannot play this file.")

    def play_prev(self):
        prev_song = self.playlist.play_prev()
        if prev_song:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(prev_song)
                pygame.mixer.music.play()
                self.highlight_current_song()
                messagebox.showinfo("Previous Song", f"Now playing: {self.playlist.current.title}")
            except pygame.error:
                messagebox.showerror("Error", "Cannot play this file.")

    def show_history(self):
        history = self.playlist.get_history()
        if history:
            messagebox.showinfo("History", "\n".join(history))
        else:
            messagebox.showinfo("History", "No songs have been played yet.")

    def highlight_current_song(self):
        self.song_listbox.selection_clear(0, tk.END)
        for i, song in enumerate(self.playlist.get_songs()):
            if song == self.playlist.current.title:
                self.song_listbox.selection_set(i)
                break

root = tk.Tk()
app = MusicPlayerGUI(root)
root.mainloop()



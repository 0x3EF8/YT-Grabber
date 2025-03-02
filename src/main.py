import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import subprocess
import platform
from PIL import Image, ImageTk
import pystray

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to the resource, whether running as a script
    or as a bundled EXE created by PyInstaller (which uses sys._MEIPASS).
    """
    try:
        # If running as a PyInstaller bundle
        base_path = sys._MEIPASS
    except AttributeError:
        # If running in a normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Point to the ICO file inside the assets folder
ICON_PATH = resource_path("assets/logo.ico")

def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

def install_ffmpeg():
    try:
        messagebox.showinfo("Installing FFmpeg", "Attempting to install FFmpeg using winget...")
        subprocess.run(["winget", "install", "-e", "--id=Gyan.FFmpeg"], check=True)
    except Exception as e:
        messagebox.showerror("Installation Failed",
                             f"Automatic installation of FFmpeg failed.\nError: {str(e)}\n\n"
                             "Please install FFmpeg manually.")

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=80, height=25, corner_radius=10, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg='#2C2C2C', **kwargs)
        self.command = command
        self.text = text
        self.corner_radius = corner_radius
        self.width = width
        self.height = height
        self.normal_color = '#E31937'
        self.hover_color = '#B8152C'
        self.current_color = self.normal_color
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        self.draw()

    def draw(self):
        self.delete('all')
        self.create_rounded_rect(0, 0, self.width, self.height, self.corner_radius, self.current_color)
        self.create_text(self.width/2, self.height/2, text=self.text, fill='white', font=('Arial', 8, 'bold'))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1
        ]
        self.create_polygon(points, smooth=True, fill=color)

    def on_enter(self, event=None):
        self.current_color = self.hover_color
        self.draw()

    def on_leave(self, event=None):
        self.current_color = self.normal_color
        self.draw()

    def on_click(self, event=None):
        if self.command:
            self.command()

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        # Attempt to load the ICO file as an image for the window icon
        try:
            pil_image = Image.open(ICON_PATH).resize((20, 20), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(pil_image)
            self.root.iconphoto(True, self.logo_image)
        except Exception as e:
            messagebox.showerror("Asset Error", f"Could not load icon from {ICON_PATH}\n{e}")
            self.logo_image = None

        self.root.overrideredirect(True)
        self.root.config(bg='#2C2C2C')
        self._offset_x = 0
        self._offset_y = 0
        
        # Title bar
        self.title_bar = tk.Frame(root, bg='#2C2C2C', height=25, relief='flat')
        self.title_bar.pack(fill='x', side='top')

        if self.logo_image:
            self.logo_label = tk.Label(self.title_bar, image=self.logo_image, bg='#2C2C2C')
            self.logo_label.pack(side='left', padx=(5, 0))
            self.logo_label.bind('<Button-1>', self.click_title_bar)
            self.logo_label.bind('<B1-Motion>', self.drag_window)
        
        self.title_label = tk.Label(self.title_bar, text="YT Grabber (0x3EF8)", bg='#2C2C2C', fg='white', font=('Arial', 10, 'bold'))
        self.title_label.pack(side='left', padx=0)

        self.close_btn = tk.Button(self.title_bar, text='X', command=self.exit_app,
                                   bg='#2C2C2C', fg='white', bd=0, font=('Arial', 10, 'bold'),
                                   activebackground='#B8152C', activeforeground='white')
        self.close_btn.pack(side='right', padx=5)

        self.minimize_btn = tk.Button(self.title_bar, text='─', command=self.minimize_to_tray,
                                      bg='#2C2C2C', fg='white', bd=0, font=('Arial', 10, 'bold'),
                                      activebackground='#444', activeforeground='white')
        self.minimize_btn.pack(side='right', padx=5)

        self.title_bar.bind('<Button-1>', self.click_title_bar)
        self.title_bar.bind('<B1-Motion>', self.drag_window)
        self.title_label.bind('<Button-1>', self.click_title_bar)
        self.title_label.bind('<B1-Motion>', self.drag_window)
        self.root.bind("<Map>", lambda event: self.root.overrideredirect(True))

        # Main frame
        self.main_frame = ttk.Frame(root, padding=0, style='Modern.TFrame')
        self.main_frame.pack(fill='both', expand=True)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('Modern.TFrame', background='#2C2C2C')
        self.style.configure('Modern.TLabel', background='#2C2C2C', foreground='white', font=('Arial', 10, 'bold'))
        self.style.configure("Modern.Horizontal.TProgressbar",
                             troughcolor='#3D3D3D',
                             background='#E31937',
                             borderwidth=1,
                             bordercolor='#444',
                             relief='flat')
        self.style.configure("Dark.TCombobox",
                             foreground="white",
                             background="#2C2C2C",
                             fieldbackground="#2C2C2C",
                             bordercolor="#444",
                             lightcolor="#2C2C2C",
                             darkcolor="#2C2C2C",
                             insertcolor="white",
                             arrowcolor="white",
                             arrowsize=15,
                             borderwidth=1)
        self.style.map("Dark.TCombobox",
                       fieldbackground=[('readonly', '#2C2C2C')],
                       foreground=[('readonly', 'white')],
                       background=[('readonly', '#2C2C2C')],
                       bordercolor=[('focus', '#444'),
                                    ('active', '#444'),
                                    ('!focus', '#444')])
        
        self.root.option_add('*TCombobox*Listbox.background', '#2C2C2C')
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#444444')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.root.option_add('*TCombobox*Listbox.borderwidth', 0)

        # Video URL input
        ttk.Label(self.main_frame, text="Video URL:", style='Modern.TLabel').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.url_entry = tk.Entry(self.main_frame, width=30, bg='#3D3D3D', fg='white',
                                  insertbackground='white', relief='flat', font=('Arial', 10))
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Save location input
        ttk.Label(self.main_frame, text="Save to:", style='Modern.TLabel').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.save_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.location_entry = tk.Entry(self.main_frame, textvariable=self.save_path, width=25,
                                       bg='#3D3D3D', fg='white', font=('Arial', 10), relief='flat')
        self.location_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        browse_button = RoundedButton(self.main_frame, text="Browse", command=self.browse_location,
                                     width=80, height=25)
        browse_button.grid(row=1, column=2, padx=5, pady=5)
        
        # Format selection (Video or Audio)
        ttk.Label(self.main_frame, text="Format:", style='Modern.TLabel').grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.format_type = tk.StringVar(value="video")
        radio_style = {
            'bg': '#2C2C2C',
            'fg': 'white',
            'selectcolor': '#E31937',
            'font': ('Arial', 8, 'bold'),
            'activebackground': '#2C2C2C',
            'activeforeground': 'white'
        }
        video_radio = tk.Radiobutton(self.main_frame, text="Video (MP4)", variable=self.format_type,
                                     value="video", command=self.update_quality_options, **radio_style)
        audio_radio = tk.Radiobutton(self.main_frame, text="Audio (MP3)", variable=self.format_type,
                                     value="audio", command=self.update_quality_options, **radio_style)
        video_radio.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        audio_radio.grid(row=2, column=2, sticky='w', padx=5, pady=5)
        
        # Quality dropdown
        ttk.Label(self.main_frame, text="Quality:", style='Modern.TLabel').grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(self.main_frame, textvariable=self.quality_var,
                                          state='readonly', style='Dark.TCombobox', font=('Arial', 10), width=25)
        self.quality_combo.grid(row=3, column=1, columnspan=2, sticky='ew', padx=5, pady=5)
        self.update_quality_options()
        
        # Progress bar and download button
        control_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        control_frame.grid(row=4, column=0, columnspan=3, sticky='ew', padx=5, pady=0)
        control_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var,
                                            maximum=100, style="Modern.Horizontal.TProgressbar")
        self.progress_bar.grid(row=0, column=0, sticky='ew', padx=5, pady=2)
        
        self.download_button = RoundedButton(control_frame, text="Download",
                                             command=self.start_download, width=100, height=30)
        self.download_button.grid(row=0, column=1, padx=5, pady=2)
        
        self.status_label = ttk.Label(self.main_frame, text="Ready", style='Modern.TLabel',
                                      font=('Arial', 8, 'bold'))
        self.status_label.grid(row=5, column=0, columnspan=3, sticky='w', padx=5, pady=2)
        
        self.downloading = False
        self.stop_requested = False

    def minimize_to_tray(self):
        self.root.withdraw()
        try:
            tray_icon_image = Image.open(ICON_PATH)
        except Exception as e:
            messagebox.showerror("Tray Icon Error", f"Could not load tray icon.\n{e}")
            return
        menu = pystray.Menu(
            pystray.MenuItem('Restore', self.restore_from_tray),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.tray_icon = pystray.Icon("YT Grabber", tray_icon_image, "YT Grabber", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_from_tray(self, icon=None, item=None):
        if icon:
            icon.stop()
        self.root.deiconify()

    def click_title_bar(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def drag_window(self, event):
        x = self.root.winfo_x() + (event.x - self._offset_x)
        y = self.root.winfo_y() + (event.y - self._offset_y)
        self.root.geometry(f"+{x}+{y}")

    def exit_app(self, icon=None, item=None):
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        self.root.destroy()

    def update_quality_options(self):
        if self.format_type.get() == "video":
            qualities = [
                "2160p (4K)", "1440p (2K)", "1080p (Full HD)",
                "720p (HD)", "480p", "360p", "240p", "144p"
            ]
        else:
            qualities = [
                "320kbps (High Quality)", "256kbps (Good Quality)",
                "192kbps (Medium Quality)", "128kbps (Low Quality)"
            ]
        self.quality_combo['values'] = qualities
        default = qualities[2] if self.format_type.get() == "video" else qualities[0]
        self.quality_combo.set(default)

    def get_format_string(self):
        if self.format_type.get() == "video":
            resolution = self.quality_var.get().split()[0].replace('p', '')
            return f'bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        else:
            bitrate = self.quality_var.get().split()[0].replace('kbps', '')
            return f'bestaudio[abr<={bitrate}][ext=m4a]/bestaudio'

    def browse_location(self):
        directory = filedialog.askdirectory(initialdir=self.save_path.get())
        if directory:
            self.save_path.set(directory)

    def update_progress(self, d):
        if self.stop_requested:
            raise Exception("Download stopped by user")
        if d.get('status') == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded = d.get('downloaded_bytes', 0)
                progress = (downloaded / total) * 100 if total else 0

                title = d.get('info_dict', {}).get('title', 'Unknown')
                if len(title) > 50:
                    title = title[:50] + "..."
                
                playlist_index = d.get('playlist_index') or d.get('info_dict', {}).get('playlist_index')
                playlist_count = d.get('playlist_count') or d.get('info_dict', {}).get('playlist_count')
                
                status_text = f"{title}: {progress:.0f}%"
                if playlist_index is not None and playlist_count is not None and int(playlist_count) > 1:
                    status_text += f" ({playlist_index}/{playlist_count})"
                
                self.progress_var.set(progress)
                self.status_label.config(text=status_text)
                self.root.update_idletasks()
            except Exception as e:
                print(f"Progress update error: {e}")

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            self.reset_download_state()
            return

        if platform.system().lower() != "windows":
            messagebox.showerror("Windows Only",
                                 "This script only supports Windows.\n"
                                 "Please install FFmpeg manually if you are on another OS.")
            self.reset_download_state()
            return

        if not check_ffmpeg_installed():
            install_ffmpeg()
            if not check_ffmpeg_installed():
                messagebox.showerror("FFmpeg Required",
                                     "FFmpeg is not installed and could not be installed automatically.\n"
                                     "Please install FFmpeg manually and try again.")
                self.reset_download_state()
                return

        self.download_button.config(state='disabled')
        self.status_label.config(text="Hold tight! Your download is getting ready...")
        
        ydl_opts = {
            'format': self.get_format_string(),
            'outtmpl': os.path.join(self.save_path.get(), '%(title)s.%(ext)s'),
            'progress_hooks': [self.update_progress],
            'merge_output_format': 'mp4',
            'postprocessors': []
        }

        if self.format_type.get() == "video":
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            })
        else:
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality_var.get().split()[0]
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text="Download completed!")
            messagebox.showinfo("Success", "Download completed successfully!")
        except Exception as e:
            if str(e) == "Download stopped by user":
                self.status_label.config(text="Download stopped!")
            else:
                self.status_label.config(text="Download failed!")
                messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.reset_download_state()

    def reset_download_state(self):
        self.download_button.config(state='normal')
        self.progress_var.set(0)
        self.download_button.text = "Download"
        self.download_button.draw()
        self.downloading = False
        self.stop_requested = False

    def start_download(self):
        if not self.downloading:
            self.downloading = True
            self.stop_requested = False
            self.download_button.text = "Stop"
            self.download_button.draw()
            threading.Thread(target=self.download_video, daemon=True).start()
        else:
            self.stop_requested = True
            self.status_label.config(text="Stopping download...")

def main():
    root = tk.Tk()
    YouTubeDownloaderGUI(root)
    root.update_idletasks()
    req_width = root.winfo_reqwidth()
    req_height = root.winfo_reqheight()
    root.geometry(f"{req_width}x{req_height}+100+100")
    root.mainloop()

if __name__ == "__main__":
    main()

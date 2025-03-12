import os
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from pathlib import Path
import sys
import subprocess
import platform

# Add parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generator import generate_batch
from src.utils import get_video_files

class ScrambleClipGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scramble Clip 2")
        self.root.geometry("800x650")
        self.root.configure(bg="#e0e0ff")
        
        # Default paths
        self.input_video_path = tk.StringVar(value=os.path.abspath("../assets/input_videos"))
        self.input_audio_path = tk.StringVar(value=os.path.abspath("../assets/input_audio/audio.mp3"))
        self.output_path = tk.StringVar(value=os.path.abspath("../outputs"))
        self.num_videos = tk.IntVar(value=5)
        
        self.create_widgets()
        self.refresh_video_lists()
        
    def create_widgets(self):
        print("Creating widgets...")
        # Main frame with a more visible background color
        main_frame = tk.Frame(self.root, bg="#e0e0ff", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        print("Main frame created and packed")
        
        # Title with contrasting background
        title_label = tk.Label(main_frame, text="SCRAMBLE CLIP 2", font=("Arial", 20, "bold"), bg="#e0e0ff", fg="#000088")
        title_label.pack(pady=(0, 20))
        print("Title label created and packed")
        
        # Left frame for inputs
        left_frame = tk.Frame(main_frame, bg="#e0e0ff")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Input Video Directory
        input_video_frame = tk.Frame(left_frame, bg="#e0e0ff")
        input_video_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_video_frame, text="Input Videos Directory:", bg="#e0e0ff").pack(side=tk.LEFT)
        tk.Entry(input_video_frame, textvariable=self.input_video_path, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(input_video_frame, text="Browse", command=self.browse_input_videos).pack(side=tk.LEFT)
        
        # Input Audio File
        input_audio_frame = tk.Frame(left_frame, bg="#e0e0ff")
        input_audio_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_audio_frame, text="Input Audio File:", bg="#e0e0ff").pack(side=tk.LEFT)
        tk.Entry(input_audio_frame, textvariable=self.input_audio_path, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(input_audio_frame, text="Browse", command=self.browse_input_audio).pack(side=tk.LEFT)
        
        # Output Directory
        output_frame = tk.Frame(left_frame, bg="#e0e0ff")
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="Output Directory:", bg="#e0e0ff").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_path, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.LEFT)
        
        # Number of videos to generate
        num_videos_frame = tk.Frame(left_frame, bg="#e0e0ff")
        num_videos_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(num_videos_frame, text="Number of Videos to Generate:", bg="#e0e0ff").pack(side=tk.LEFT)
        tk.Spinbox(num_videos_frame, from_=1, to=100, textvariable=self.num_videos, width=5).pack(side=tk.LEFT, padx=5)
        
        # Generate button
        btn_frame = tk.Frame(left_frame, bg="#e0e0ff")
        btn_frame.pack(fill=tk.X, pady=10)
        
        generate_button = tk.Button(btn_frame, text="Generate Videos", command=self.start_generation)
        generate_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = tk.Button(btn_frame, text="Refresh Lists", command=self.refresh_video_lists)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Canvas(left_frame, width=300, height=20, bg="white")
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(left_frame, textvariable=self.status_var, bg="#e0e0ff")
        status_label.pack(pady=5)
        
        # Right frame for file lists
        right_frame = tk.Frame(main_frame, bg="#e0e0ff")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        # Input video list
        input_list_frame = tk.LabelFrame(right_frame, text="Input Videos", bg="#e0e0ff")
        input_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_video_list = tk.Listbox(input_list_frame, height=10, bg="#ffffff", selectbackground="#4040ff")
        self.input_video_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        play_input_btn = tk.Button(input_list_frame, text="Play Selected", command=lambda: self.play_video(self.input_video_list))
        play_input_btn.pack(pady=5)
        
        # Output video list
        output_list_frame = tk.LabelFrame(right_frame, text="Output Videos", bg="#e0e0ff")
        output_list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.output_video_list = tk.Listbox(output_list_frame, height=10, bg="#ffffff", selectbackground="#4040ff")
        self.output_video_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        output_btn_frame = tk.Frame(output_list_frame, bg="#e0e0ff")
        output_btn_frame.pack(fill=tk.X, pady=5)
        
        play_output_btn = tk.Button(output_btn_frame, text="Play Selected", command=lambda: self.play_video(self.output_video_list))
        play_output_btn.pack(side=tk.LEFT, padx=5)
        
        delete_output_btn = tk.Button(output_btn_frame, text="Delete Selected", command=self.delete_selected_output)
        delete_output_btn.pack(side=tk.LEFT, padx=5)
        
        # Credits
        credits_label = tk.Label(main_frame, text="Created by Daniel Dwyer", font=("Arial", 8), bg="#e0e0ff")
        credits_label.pack(side=tk.BOTTOM, pady=10)
        
        print("All widgets created successfully")
        
    def update_progress_bar(self, value):
        """Update the canvas progress bar with the current progress value"""
        self.progress_bar.delete("progress")
        width = int(self.progress_bar.winfo_width() * (value / 100))
        self.progress_bar.create_rectangle(0, 0, width, 20, fill="#4CAF50", tags="progress")
        
    def refresh_video_lists(self):
        print("Refreshing video lists...")
        # Clear lists
        self.input_video_list.delete(0, tk.END)
        self.output_video_list.delete(0, tk.END)
        
        # Fill input videos list
        if os.path.exists(self.input_video_path.get()):
            input_videos = get_video_files(self.input_video_path.get())
            for video in input_videos:
                self.input_video_list.insert(tk.END, os.path.basename(video))
        
        # Fill output videos list
        if os.path.exists(self.output_path.get()):
            output_videos = get_video_files(self.output_path.get())
            for video in output_videos:
                self.output_video_list.insert(tk.END, os.path.basename(video))
                
        # Update status
        input_count = self.input_video_list.size()
        output_count = self.output_video_list.size()
        self.status_var.set(f"Found {input_count} input videos, {output_count} output videos")
    
    def play_video(self, listbox):
        selected_idx = listbox.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a video to play")
            return
            
        selected_name = listbox.get(selected_idx[0])
        
        # Determine if it's an input or output video
        if listbox == self.input_video_list:
            video_path = os.path.join(self.input_video_path.get(), selected_name)
        else:
            video_path = os.path.join(self.output_path.get(), selected_name)
            
        # Open video with system default player
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', video_path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(video_path)
        else:  # Linux
            subprocess.call(('xdg-open', video_path))
    
    def delete_selected_output(self):
        selected_idx = self.output_video_list.curselection()
        if not selected_idx:
            messagebox.showinfo("Info", "Please select a video to delete")
            return
            
        selected_name = self.output_video_list.get(selected_idx[0])
        video_path = os.path.join(self.output_path.get(), selected_name)
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {selected_name}?")
        if confirm:
            try:
                os.remove(video_path)
                messagebox.showinfo("Success", f"Deleted {selected_name}")
                self.refresh_video_lists()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {str(e)}")
    
    def browse_input_videos(self):
        directory = filedialog.askdirectory(initialdir=self.input_video_path.get())
        if directory:
            self.input_video_path.set(directory)
            self.refresh_video_lists()
    
    def browse_input_audio(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.input_audio_path.get()),
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        if file_path:
            self.input_audio_path.set(file_path)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_path.get())
        if directory:
            self.output_path.set(directory)
            self.refresh_video_lists()
    
    def start_generation(self):
        # Validate inputs
        if not os.path.exists(self.input_video_path.get()):
            messagebox.showerror("Error", "Input videos directory does not exist!")
            return
            
        if not os.path.exists(self.input_audio_path.get()):
            messagebox.showerror("Error", "Input audio file does not exist!")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path.get(), exist_ok=True)
        
        # Disable UI elements during generation
        for widget in self.root.winfo_children():
            try:
                widget.configure(state="disabled")
            except:
                pass
            
        self.status_var.set("Generating videos...")
        self.update_progress_bar(0)
        
        # Start generation in a separate thread to keep UI responsive
        generation_thread = threading.Thread(target=self.generate_videos)
        generation_thread.daemon = True
        generation_thread.start()
    
    def generate_videos(self):
        try:
            # Define progress callback
            def update_progress(progress, status_message=None):
                self.root.after(0, lambda: self.update_progress_bar(progress))
                if status_message:
                    self.root.after(0, lambda: self.status_var.set(status_message))
            
            # Call the generate_batch function with user-selected paths
            generate_batch(
                num_videos=self.num_videos.get(),
                input_video_path=self.input_video_path.get(),
                input_audio_path=self.input_audio_path.get(),
                output_path=self.output_path.get(),
                progress_callback=update_progress
            )
            
            # Update UI
            self.root.after(0, self.enable_ui)
            self.root.after(0, self.refresh_video_lists)
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Successfully generated {self.num_videos.get()} videos!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, self.enable_ui)
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    
    def enable_ui(self):
        for widget in self.root.winfo_children():
            try:
                widget.configure(state="normal")
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ScrambleClipGUI(root)
    root.mainloop() 
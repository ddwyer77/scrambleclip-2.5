import os
import sys
import threading
import platform
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QFrame, QLineEdit, QSpinBox, QListWidget, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QLinearGradient, QBrush, QPainter, QGradient

# Add parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generator import generate_batch
from src.utils import get_video_files

# Define custom color palette for the app
COLORS = {
    'dark_bg': '#121212',  # Primary dark background
    'dark_panel': '#1E1E1E',  # Secondary dark background
    'green_accent': '#00E676',  # Primary green accent
    'light_green': '#69F0AE',  # Lighter green accent
    'green_gradient_start': '#00E676',  # Start of the green gradient
    'green_gradient_end': '#00B248',  # End of the green gradient
    'text_primary': '#FFFFFF',  # Primary text color
    'text_secondary': '#B3B3B3',  # Secondary text color
    'error_red': '#FF5252',  # Error color
}

class StyledButton(QPushButton):
    """Custom styled button with green gradient."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green_accent']};
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['light_green']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['green_gradient_end']};
            }}
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class StyledGroupBox(QGroupBox):
    """Custom styled group box for the dark theme."""
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['dark_panel']};
                color: {COLORS['text_primary']};
                border: 1px solid #333333;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {COLORS['green_accent']};
            }}
        """)

class ProgressSignals(QObject):
    """Signals for updating progress and status from worker threads."""
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    complete = pyqtSignal(int)  # Sends number of videos generated

class ScrambleClipGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Scramble Clip 2")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply the dark theme to the entire window
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit {{
                background-color: #2A2A2A;
                color: {COLORS['text_primary']};
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: {COLORS['green_accent']};
            }}
            QSpinBox {{
                background-color: #2A2A2A;
                color: {COLORS['text_primary']};
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                selection-background-color: {COLORS['green_accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {COLORS['dark_panel']};
                border: none;
                width: 16px;
                border-radius: 2px;
            }}
            QListWidget {{
                background-color: #2A2A2A;
                color: {COLORS['text_primary']};
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
                outline: none;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['green_accent']};
                color: black;
            }}
            QProgressBar {{
                border: 1px solid #444444;
                border-radius: 4px;
                text-align: center;
                background-color: #2A2A2A;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['green_accent']};
                border-radius: 3px;
            }}
        """)
        
        # Initialize UI variables
        self.input_video_path = os.path.abspath("../assets/input_videos")
        self.input_audio_path = os.path.abspath("../assets/input_audio/audio.mp3")
        self.output_path = os.path.abspath("../outputs")
        self.num_videos = 5
        
        # Create signals for thread communication
        self.signals = ProgressSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.error.connect(self.show_error)
        self.signals.complete.connect(self.generation_complete)
        
        # Setup the UI
        self.setup_ui()
        
        # Refresh video lists
        self.refresh_video_lists()
        
        print("PyQt GUI initialized")
    
    def setup_ui(self):
        print("Setting up PyQt UI...")
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with title and logo
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            background-color: {COLORS['dark_panel']};
            border-radius: 8px;
            padding: 10px;
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title with green gradient text
        title_label = QLabel("SCRAMBLE CLIP 2 by ClipmodeGo")
        title_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['green_accent']};
            padding: 5px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Professional Video Randomization Tool")
        subtitle_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # Content area with left and right panels
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)
        
        # Left panel for controls
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Input Video Directory
        input_video_group = StyledGroupBox("Input Videos Directory")
        input_video_layout = QHBoxLayout(input_video_group)
        
        self.input_video_path_field = QLineEdit(self.input_video_path)
        input_video_layout.addWidget(self.input_video_path_field)
        
        browse_video_btn = StyledButton("Browse")
        browse_video_btn.clicked.connect(self.browse_input_videos)
        input_video_layout.addWidget(browse_video_btn)
        
        left_layout.addWidget(input_video_group)
        
        # Input Audio File
        input_audio_group = StyledGroupBox("Input Audio File")
        input_audio_layout = QHBoxLayout(input_audio_group)
        
        self.input_audio_path_field = QLineEdit(self.input_audio_path)
        input_audio_layout.addWidget(self.input_audio_path_field)
        
        browse_audio_btn = StyledButton("Browse")
        browse_audio_btn.clicked.connect(self.browse_input_audio)
        input_audio_layout.addWidget(browse_audio_btn)
        
        left_layout.addWidget(input_audio_group)
        
        # Output Directory
        output_group = StyledGroupBox("Output Directory")
        output_layout = QHBoxLayout(output_group)
        
        self.output_path_field = QLineEdit(self.output_path)
        output_layout.addWidget(self.output_path_field)
        
        browse_output_btn = StyledButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_output_btn)
        
        left_layout.addWidget(output_group)
        
        # Number of Videos
        num_videos_group = StyledGroupBox("Number of Videos to Generate")
        num_videos_layout = QHBoxLayout(num_videos_group)
        
        self.num_videos_spinner = QSpinBox()
        self.num_videos_spinner.setMinimum(1)
        self.num_videos_spinner.setMaximum(100)
        self.num_videos_spinner.setValue(self.num_videos)
        num_videos_layout.addWidget(self.num_videos_spinner)
        
        left_layout.addWidget(num_videos_group)
        
        # Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setSpacing(15)
        
        generate_btn = StyledButton("Generate Videos")
        generate_btn.setMinimumHeight(50)
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['green_accent']};
                color: #000000;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['light_green']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['green_gradient_end']};
            }}
        """)
        generate_btn.clicked.connect(self.start_generation)
        buttons_layout.addWidget(generate_btn)
        
        refresh_btn = StyledButton("Refresh Lists")
        refresh_btn.clicked.connect(self.refresh_video_lists)
        buttons_layout.addWidget(refresh_btn)
        
        left_layout.addWidget(buttons_frame)
        
        # Progress section
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel("Generation Progress")
        progress_title.setStyleSheet(f"color: {COLORS['green_accent']}; font-weight: bold;")
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(30)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        status_frame = QFrame()
        status_frame.setStyleSheet(f"background-color: {COLORS['dark_panel']}; border-radius: 4px; padding: 5px;")
        status_layout = QHBoxLayout(status_frame)
        
        status_icon = QLabel("◉")
        status_icon.setStyleSheet(f"color: {COLORS['green_accent']}; font-size: 16px;")
        status_layout.addWidget(status_icon)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        progress_layout.addWidget(status_frame)
        left_layout.addWidget(progress_frame)
        
        left_layout.addStretch()
        
        # Right panel for file lists
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Input video list
        input_list_group = StyledGroupBox("Input Videos")
        input_list_layout = QVBoxLayout(input_list_group)
        
        self.input_video_list = QListWidget()
        input_list_layout.addWidget(self.input_video_list)
        
        play_input_btn = StyledButton("Play Selected")
        play_input_btn.clicked.connect(lambda: self.play_video(self.input_video_list))
        input_list_layout.addWidget(play_input_btn)
        
        right_layout.addWidget(input_list_group)
        
        # Output video list
        output_list_group = StyledGroupBox("Output Videos")
        output_list_layout = QVBoxLayout(output_list_group)
        
        self.output_video_list = QListWidget()
        output_list_layout.addWidget(self.output_video_list)
        
        output_buttons_frame = QFrame()
        output_buttons_layout = QHBoxLayout(output_buttons_frame)
        output_buttons_layout.setSpacing(10)
        
        play_output_btn = StyledButton("Play Selected")
        play_output_btn.clicked.connect(lambda: self.play_video(self.output_video_list))
        output_buttons_layout.addWidget(play_output_btn)
        
        delete_output_btn = StyledButton("Delete Selected")
        delete_output_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4A4A4A;
                color: {COLORS['text_primary']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error_red']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #C62828;
            }}
        """)
        delete_output_btn.clicked.connect(self.delete_selected_output)
        output_buttons_layout.addWidget(delete_output_btn)
        
        output_list_layout.addWidget(output_buttons_frame)
        
        right_layout.addWidget(output_list_group)
        
        # Add panels to content layout
        content_layout.addWidget(left_panel, 1)
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(content_frame)
        
        # Footer with branding
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)
        
        footer_layout.addStretch()
        
        footer_label = QLabel("A tool by ClipmodeGo")
        footer_label.setStyleSheet(f"""
            color: {COLORS['green_accent']};
            font-style: italic;
            font-size: 10px;
        """)
        footer_layout.addWidget(footer_label)
        
        main_layout.addWidget(footer_frame)
        
        print("PyQt UI setup complete")
    
    def update_progress(self, value, message=None):
        """Update progress bar and status message."""
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
    
    def refresh_video_lists(self):
        """Refresh the input and output video lists."""
        print("Refreshing video lists...")
        # Clear lists
        self.input_video_list.clear()
        self.output_video_list.clear()
        
        # Update paths from text fields
        self.input_video_path = self.input_video_path_field.text()
        self.input_audio_path = self.input_audio_path_field.text()
        self.output_path = self.output_path_field.text()
        
        # Fill input videos list
        if os.path.exists(self.input_video_path):
            input_videos = get_video_files(self.input_video_path)
            for video in input_videos:
                self.input_video_list.addItem(os.path.basename(video))
        
        # Fill output videos list
        if os.path.exists(self.output_path):
            output_videos = get_video_files(self.output_path)
            for video in output_videos:
                self.output_video_list.addItem(os.path.basename(video))
                
        # Update status
        input_count = self.input_video_list.count()
        output_count = self.output_video_list.count()
        self.status_label.setText(f"Found {input_count} input videos, {output_count} output videos")
    
    def play_video(self, list_widget):
        """Play the selected video in the default system player."""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Please select a video to play")
            return
            
        selected_name = selected_items[0].text()
        
        # Determine if it's an input or output video
        if list_widget == self.input_video_list:
            video_path = os.path.join(self.input_video_path, selected_name)
        else:
            video_path = os.path.join(self.output_path, selected_name)
            
        # Open video with system default player
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', video_path))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(video_path)
        else:  # Linux
            subprocess.call(('xdg-open', video_path))
    
    def delete_selected_output(self):
        """Delete the selected output video."""
        selected_items = self.output_video_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Please select a video to delete")
            return
            
        selected_name = selected_items[0].text()
        video_path = os.path.join(self.output_path, selected_name)
        
        # Create a custom styled message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Are you sure you want to delete {selected_name}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
            }}
            QPushButton {{
                background-color: {COLORS['dark_panel']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['green_accent']};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['green_accent']};
                color: black;
            }}
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(video_path)
                self.status_label.setText(f"Deleted {selected_name}")
                self.refresh_video_lists()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete file: {str(e)}")
    
    def browse_input_videos(self):
        """Open a file dialog to select the input videos directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Input Videos Directory",
            self.input_video_path
        )
        if directory:
            self.input_video_path_field.setText(directory)
            self.input_video_path = directory
            self.refresh_video_lists()
    
    def browse_input_audio(self):
        """Open a file dialog to select the input audio file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Audio File",
            os.path.dirname(self.input_audio_path),
            "Audio Files (*.mp3 *.wav)"
        )
        if file_path:
            self.input_audio_path_field.setText(file_path)
            self.input_audio_path = file_path
    
    def browse_output_dir(self):
        """Open a file dialog to select the output directory."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Directory",
            self.output_path
        )
        if directory:
            self.output_path_field.setText(directory)
            self.output_path = directory
            self.refresh_video_lists()
    
    def start_generation(self):
        """Validate inputs and start the video generation process."""
        # Validate inputs
        if not os.path.exists(self.input_video_path):
            self.show_error("Input videos directory does not exist!")
            return
            
        if not os.path.exists(self.input_audio_path):
            self.show_error("Input audio file does not exist!")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_path, exist_ok=True)
        
        # Update number of videos from spinner
        self.num_videos = self.num_videos_spinner.value()
        
        # Reset UI for generation
        self.progress_bar.setValue(0)
        self.status_label.setText("Generating videos...")
        
        # Start generation in a separate thread
        generation_thread = threading.Thread(target=self.generate_videos)
        generation_thread.daemon = True
        generation_thread.start()
    
    def generate_videos(self):
        """Generate videos in a background thread."""
        try:
            # Define progress callback
            def update_progress(progress, status_message=None):
                self.signals.progress.emit(progress, status_message or "")
            
            # Call the generate_batch function
            generate_batch(
                num_videos=self.num_videos,
                input_video_path=self.input_video_path,
                input_audio_path=self.input_audio_path,
                output_path=self.output_path,
                progress_callback=update_progress
            )
            
            # Signal completion (from worker thread)
            self.signals.progress.emit(100, "Generation complete!")
            self.signals.complete.emit(self.num_videos)
            
        except Exception as e:
            # Signal error (from worker thread)
            error_message = str(e)
            self.signals.progress.emit(0, f"Error: {error_message}")
            self.signals.error.emit(error_message)
    
    def show_error(self, message):
        """Show error message (called from main thread)."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
            }}
            QPushButton {{
                background-color: {COLORS['dark_panel']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['green_accent']};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['green_accent']};
                color: black;
            }}
        """)
        msg_box.exec_()
    
    def generation_complete(self, num_videos):
        """Handle generation completion (called from main thread)."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Success")
        msg_box.setText(f"Successfully generated {num_videos} videos!")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
            }}
            QPushButton {{
                background-color: {COLORS['dark_panel']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['green_accent']};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['green_accent']};
                color: black;
            }}
        """)
        msg_box.exec_()
        self.refresh_video_lists()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style as base for consistent cross-platform look
    window = ScrambleClipGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
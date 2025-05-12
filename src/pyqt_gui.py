import os
import sys
import threading
import platform
import subprocess
import shutil
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QFrame, QLineEdit, QSpinBox, QListWidget, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QGraphicsDropShadowEffect, QGridLayout, QCheckBox,
    QDesktopWidget, QFontComboBox, QComboBox, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QLinearGradient, QBrush, QPainter, QGradient, QPixmap

# Add parent directory to path to import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.generator import generate_batch
from src.utils import get_video_files

# Modern, clean color palette  
# Primary accent is a calm blue, with neutral light greys for backgrounds.  
# This palette aims for high-contrast readability and a more professional feel.
COLORS = {
    # Warm orange accents
    'primary': '#FFA726',        # Orange primary accent
    'lighter': '#FFB74D',        # Lighter orange for hover and highlights
    'darker_accent': '#FB8C00',  # Darker orange accent
    # Light brown backgrounds
    'dark': '#EFEBE9',           # Soft light brown background
    'darker': '#D7CCC8',         # Slightly darker brown for sections
    'darkest': '#FFFFFF',        # White for group boxes and cards
    # Dark brown text for contrast
    'text': '#4E342E'
}

# Define styled button with green gradient
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['darker_accent']}, stop:1 {COLORS['primary']});
                color: {COLORS['darkest']};
                border: none;
                padding: 8px 18px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['primary']}, stop:1 {COLORS['lighter']});
            }}
            QPushButton:pressed {{
                background: {COLORS['darker_accent']};
            }}
        """)
        
        # Add drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

# Define styled group box with green header
class StyledGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['darkest']};
                border: 1px solid {COLORS['darker']};
                border-radius: 8px;
                margin-top: 1.5em;
                font-weight: 600;
                color: {COLORS['primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 6px;
                color: {COLORS['primary']};
            }}
        """)
        
        # Add drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

class ProgressSignals(QObject):
    """Signals for updating progress and status from worker threads."""
    progress = pyqtSignal(int, str)
    error = pyqtSignal(str)
    complete = pyqtSignal(int)  # Sends number of videos generated

class ScrambleClipGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Paths
        self.input_video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "input_videos"))
        self.input_audio_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "input_audio", "audio.mp3"))
        self.output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        
        # Create required directories
        os.makedirs(self.input_video_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.input_audio_path), exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
        
        # Initialize UI
        self.init_ui()
        
        # Refresh video lists
        self.refresh_video_lists()
        print("PyQt GUI initialized")

    def init_ui(self):
        self.setWindowTitle("Scramble Clip 2.5")
        # Increase minimum and initial window size for better usability
        self.setMinimumSize(1200, 900)
        self.resize(1200, 900)
        
        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Center the window
        self.center()
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Create header with logo image
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "scramble clip 2.5 logo 222 for build.png")
        header = QLabel()
        pixmap = QPixmap(logo_path)
        # Scale banner to 10% of original size for a 90% reduction
        if not pixmap.isNull():
            new_width = int(pixmap.width() * 0.1)
            new_height = int(pixmap.height() * 0.1)
            scaled_pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            header.setPixmap(scaled_pixmap)
        else:
            header.setText("Scramble Clip 2.5")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"background-color: {COLORS['darkest']}; padding: 10px;")
        
        # Create central widget with dark background
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['dark']};")
        
        # Main container for all controls
        container = QVBoxLayout()
        container.setContentsMargins(20, 20, 20, 20)
        container.setSpacing(15)
        
        # Create path settings group box
        path_group = StyledGroupBox("Input/Output Paths")
        path_layout = QGridLayout()
        path_layout.setColumnStretch(1, 1)  # Make the path display stretch
        
        # Input videos path row
        path_layout.addWidget(QLabel("Input Videos:"), 0, 0)
        self.input_video_path_label = QLineEdit(self.input_video_path)
        self.input_video_path_label.setReadOnly(True)
        self.input_video_path_label.setStyleSheet(f"""
            background-color: {COLORS['darkest']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darker']};
            border-radius: 4px;
            padding: 6px;
        """)
        path_layout.addWidget(self.input_video_path_label, 0, 1)
        
        browse_input_btn = StyledButton("Browse")
        browse_input_btn.clicked.connect(lambda: self.browse_directory("input_video"))
        path_layout.addWidget(browse_input_btn, 0, 2)
        
        # Input audio path row
        path_layout.addWidget(QLabel("Input Audio:"), 1, 0)
        self.input_audio_path_label = QLineEdit(self.input_audio_path)
        self.input_audio_path_label.setReadOnly(True)
        self.input_audio_path_label.setStyleSheet(f"""
            background-color: {COLORS['darkest']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darker']};
            border-radius: 4px;
            padding: 6px;
        """)
        path_layout.addWidget(self.input_audio_path_label, 1, 1)
        
        browse_audio_btn = StyledButton("Browse")
        browse_audio_btn.clicked.connect(lambda: self.browse_file("input_audio"))
        path_layout.addWidget(browse_audio_btn, 1, 2)
        
        # Output path row
        path_layout.addWidget(QLabel("Output Path:"), 2, 0)
        self.output_path_label = QLineEdit(self.output_path)
        self.output_path_label.setReadOnly(True)
        self.output_path_label.setStyleSheet(f"""
            background-color: {COLORS['darkest']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darker']};
            border-radius: 4px;
            padding: 6px;
        """)
        path_layout.addWidget(self.output_path_label, 2, 1)
        
        browse_output_btn = StyledButton("Browse")
        browse_output_btn.clicked.connect(lambda: self.browse_directory("output"))
        path_layout.addWidget(browse_output_btn, 2, 2)
        
        # Overlay video path row (row 3)
        self.overlay_video_path = ""  # default empty
        path_layout.addWidget(QLabel("Overlay Video:"), 3, 0)
        self.overlay_video_path_label = QLineEdit(self.overlay_video_path)
        self.overlay_video_path_label.setReadOnly(True)
        self.overlay_video_path_label.setStyleSheet(f"""
             background-color: {COLORS['darkest']};
             color: {COLORS['text']};
             border: 1px solid {COLORS['darker']};
             border-radius: 4px;
             padding: 6px;
         """)
        path_layout.addWidget(self.overlay_video_path_label, 3, 1)
        self.browse_overlay_btn = StyledButton("Browse")
        self.browse_overlay_btn.clicked.connect(lambda: self.browse_file("overlay_video"))
        self.browse_overlay_btn.setEnabled(False)
        path_layout.addWidget(self.browse_overlay_btn, 3, 2)
        
        # disable overlay path label initially
        self.overlay_video_path_label.setEnabled(False)
        
        # Row 4: simple checkbox to quickly toggle overlay usage
        self.use_overlay_checkbox = QCheckBox("Enable Overlay")
        self.use_overlay_checkbox.setChecked(False)
        self.use_overlay_checkbox.stateChanged.connect(lambda s: self.toggle_overlay_input(s))
        path_layout.addWidget(self.use_overlay_checkbox, 4, 0, 1, 3)
        
        path_group.setLayout(path_layout)
        container.addWidget(path_group)
        
        # ------------ Output settings ------------
        output_opts_group = StyledGroupBox("Output Settings")
        out_layout = QGridLayout()

        out_layout.addWidget(QLabel("Target Duration (s):"), 0, 0)
        self.duration_spinner = QSpinBox()
        self.duration_spinner.setRange(5, 120)
        self.duration_spinner.setValue(16)
        self.duration_spinner.setSingleStep(1)
        self.duration_spinner.setStyleSheet(f"""
            background-color: {COLORS['darkest']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darker']};
            border-radius: 4px;
            padding: 4px;
        """)
        out_layout.addWidget(self.duration_spinner, 0, 1)

        output_opts_group.setLayout(out_layout)
        container.addWidget(output_opts_group)
        
        # Create video lists
        lists_layout = QHBoxLayout()
        
        # Input videos list
        input_group = StyledGroupBox("Input Videos")
        input_layout = QVBoxLayout()
        
        self.input_video_list = QListWidget()
        self.input_video_list.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        input_layout.addWidget(self.input_video_list)
        
        input_buttons = QHBoxLayout()
        play_input_btn = StyledButton("Play")
        play_input_btn.clicked.connect(lambda: self.play_video(self.input_video_list))
        input_buttons.addWidget(play_input_btn)
        
        add_input_btn = StyledButton("Add")
        add_input_btn.clicked.connect(self.add_input_video)
        input_buttons.addWidget(add_input_btn)
        
        remove_input_btn = StyledButton("Remove")
        remove_input_btn.clicked.connect(lambda: self.remove_video(self.input_video_list))
        input_buttons.addWidget(remove_input_btn)
        
        input_layout.addLayout(input_buttons)
        input_group.setLayout(input_layout)
        lists_layout.addWidget(input_group)
        
        # Output videos list
        output_group = StyledGroupBox("Output Videos")
        output_layout = QVBoxLayout()
        
        self.output_video_list = QListWidget()
        self.output_video_list.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        output_layout.addWidget(self.output_video_list)
        
        output_buttons = QHBoxLayout()
        play_output_btn = StyledButton("Play")
        play_output_btn.clicked.connect(lambda: self.play_video(self.output_video_list))
        output_buttons.addWidget(play_output_btn)
        
        open_output_folder_btn = StyledButton("Open Folder")
        open_output_folder_btn.clicked.connect(self.open_output_folder)
        output_buttons.addWidget(open_output_folder_btn)
        
        remove_output_btn = StyledButton("Remove")
        remove_output_btn.clicked.connect(lambda: self.remove_video(self.output_video_list))
        output_buttons.addWidget(remove_output_btn)
        
        output_layout.addLayout(output_buttons)
        output_group.setLayout(output_layout)
        lists_layout.addWidget(output_group)
        
        container.addLayout(lists_layout)
        
        # Create generation controls
        gen_group = StyledGroupBox("Generate Videos")
        gen_layout = QVBoxLayout()
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Number of videos:"))
        
        self.num_videos_spinner = QSpinBox()
        self.num_videos_spinner.setMinimum(1)
        self.num_videos_spinner.setMaximum(100)
        self.num_videos_spinner.setValue(5)
        self.num_videos_spinner.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        controls_layout.addWidget(self.num_videos_spinner)
        
        # Base name for output files
        controls_layout.addWidget(QLabel("Base name:"))
        self.basename_input = QLineEdit("output")
        self.basename_input.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 4px;
        """)
        controls_layout.addWidget(self.basename_input)
        
        # Add checkboxes to layout
        checks_layout = QVBoxLayout() 
        
        # Add AI toggle checkbox
        self.use_ai_checkbox = QCheckBox("Use AI for smart clip selection")
        self.use_ai_checkbox.setChecked(True)
        self.use_ai_checkbox.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            padding: 5px;
        """)
        self.use_ai_checkbox.setToolTip(
            "When enabled, AI analyzes video content to:\n"
            "• Select the most interesting video segments\n"
            "• Avoid repetitive content across output videos\n"
            "• Ensure visual variety in generated videos\n"
            "\n"
            "The AI scores clips based on motion, visual complexity, and more."
        )
        checks_layout.addWidget(self.use_ai_checkbox)
        
        # Add AI Effects checkbox
        self.use_effects_checkbox = QCheckBox("Add AI-powered effects & transitions")
        self.use_effects_checkbox.setChecked(False)
        self.use_effects_checkbox.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            padding: 5px;
        """)
        self.use_effects_checkbox.setToolTip(
            "When enabled, AI will enhance videos with:\n"
            "• Smart transitions between clips\n"
            "• Visual effects based on content analysis\n"
            "• Timed effects synced with audio\n"
            "\n"
            "Effects are chosen based on clip content and energy."
        )
        checks_layout.addWidget(self.use_effects_checkbox)
        
        # Effects style dropdown (Classic / Graincore)
        effects_style_layout = QHBoxLayout()
        self.effects_style_label = QLabel("Effects style:")
        self.effects_style_label.setStyleSheet(f"color: {COLORS['text']}; padding: 5px;")
        self.effects_style_combo = QComboBox()
        self.effects_style_combo.addItems(["Classic", "Graincore"])
        # Initially hidden
        self.effects_style_label.setVisible(False)
        self.effects_style_combo.setVisible(False)
        effects_style_layout.addWidget(self.effects_style_label)
        effects_style_layout.addWidget(self.effects_style_combo)
        checks_layout.addLayout(effects_style_layout)
        # Show/hide effects style when AI-effects toggled
        def _toggle_effects_style(state):
            visible = (state == Qt.Checked)
            self.effects_style_label.setVisible(visible)
            self.effects_style_combo.setVisible(visible)
            self.intensity_label.setVisible(visible)
            self.intensity_slider.setVisible(visible)
        self.use_effects_checkbox.stateChanged.connect(_toggle_effects_style)
        
        # Add Text Overlay checkbox
        self.use_text_checkbox = QCheckBox("Add text to videos")
        self.use_text_checkbox.setChecked(False)
        self.use_text_checkbox.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            padding: 5px;
        """)
        checks_layout.addWidget(self.use_text_checkbox)
        
        # Connect checkbox state change to show/hide text input
        self.use_text_checkbox.stateChanged.connect(self.toggle_text_input)
        
        # Add ImageMagick tooltip info
        self.use_text_checkbox.setToolTip(
            "When enabled, videos will include:\n"
            "• Attention-grabbing captions\n"
            "• Clear, visible text overlay\n"
            "• Professional styling suited for short-form content\n"
            "\n"
            "Note: For best text quality, ImageMagick should be installed.\n"
            "If not installed, a simplified text style will be used."
        )
        
        # Speed factor dropdown
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet(f"color: {COLORS['text']}; padding: 5px;")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["Normal (1.0x)", "1.25x", "1.5x", "1.75x"])
        self.speed_combo.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_combo)
        checks_layout.addLayout(speed_layout)
        
        # Intensity slider (0-100)
        intensity_layout = QHBoxLayout()
        self.intensity_label = QLabel("Intensity: 50")
        self.intensity_label.setStyleSheet(f"color: {COLORS['text']}; padding: 5px;")
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.setTickPosition(QSlider.TicksBelow)
        self.intensity_slider.setTickInterval(10)
        self.intensity_slider.setStyleSheet(f"margin-left:10px; margin-right:10px;")
        self.intensity_slider.valueChanged.connect(lambda v: self.intensity_label.setText(f"Intensity: {v}"))
        # hide initially
        self.intensity_label.setVisible(False)
        self.intensity_slider.setVisible(False)
        intensity_layout.addWidget(self.intensity_label)
        intensity_layout.addWidget(self.intensity_slider)
        checks_layout.addLayout(intensity_layout)
        
        # Add the checkboxes layout to the main layout
        gen_layout.addLayout(controls_layout)
        gen_layout.addLayout(checks_layout)
        
        # Add text input field for custom text and formatting controls
        self.text_input_layout = QHBoxLayout()
        self.text_input_label = QLabel("Custom text:")
        self.text_input_label.setStyleSheet(f"color: {COLORS['text']};")
        self.text_input = QLineEdit()
        # Font selection dropdown
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial"))
        self.font_combo.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        # Style toggles
        self.bold_checkbox = QCheckBox("Bold")
        self.italic_checkbox = QCheckBox("Italic")
        self.underline_checkbox = QCheckBox("Underline")
        # Position dropdown
        self.position_combo = QComboBox()
        self.position_combo.addItems(["Top", "Center", "Bottom"])
        self.position_combo.setCurrentIndex(0)  # Default Top
        self.position_combo.setStyleSheet(f"""
            background-color: {COLORS['darker']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['darkest']};
            border-radius: 4px;
            padding: 5px;
        """)
        # Style toggles styling and visibility
        for cb in (self.bold_checkbox, self.italic_checkbox, self.underline_checkbox):
            cb.setStyleSheet(f"color: {COLORS['text']}; padding: 5px;")
            cb.setVisible(False)
        self.position_combo.setVisible(False)
        # Initially hide text and controls
        self.text_input_label.setVisible(False)
        self.text_input.setVisible(False)
        self.font_combo.setVisible(False)
        self.bold_checkbox.setVisible(False)
        self.italic_checkbox.setVisible(False)
        self.underline_checkbox.setVisible(False)
        # Add widgets to layout
        self.text_input_layout.addWidget(self.text_input_label)
        self.text_input_layout.addWidget(self.text_input)
        self.text_input_layout.addWidget(self.font_combo)
        self.text_input_layout.addWidget(self.bold_checkbox)
        self.text_input_layout.addWidget(self.italic_checkbox)
        self.text_input_layout.addWidget(self.underline_checkbox)
        self.text_input_layout.addWidget(self.position_combo)
        
        # Initially hide the text input
        # (Visibility already set for label, input, and controls)
        
        # Add the text input layout to controls layout
        gen_layout.addLayout(self.text_input_layout)
        
        # Add buttons layout 
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        refresh_btn = StyledButton("Refresh Lists")
        refresh_btn.clicked.connect(self.refresh_video_lists)
        buttons_layout.addWidget(refresh_btn)
        
        generate_btn = StyledButton("Generate Videos")
        generate_btn.clicked.connect(self.generate_videos)
        generate_btn.setMinimumWidth(150)
        buttons_layout.addWidget(generate_btn)
        
        # Save / Load project buttons
        save_btn = StyledButton("Save Project")
        save_btn.clicked.connect(self.save_project)
        buttons_layout.addWidget(save_btn)

        load_btn = StyledButton("Load Project")
        load_btn.clicked.connect(self.load_project)
        buttons_layout.addWidget(load_btn)
        
        # Add Cancel Generation button
        self.cancel_btn = StyledButton("Cancel Generation")
        self.cancel_btn.clicked.connect(self.cancel_generation)
        self.cancel_btn.setEnabled(False)
        buttons_layout.addWidget(self.cancel_btn)
        
        gen_layout.addLayout(buttons_layout)
        
        # Progress bar and status
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['darker']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['darkest']};
                border-radius: 4px;
                padding: 1px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {COLORS['darker_accent']}, stop:1 {COLORS['primary']});
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 5px;
        """)
        progress_layout.addWidget(self.status_label)
        
        gen_layout.addLayout(progress_layout)
        gen_group.setLayout(gen_layout)
        container.addWidget(gen_group)
        
        # Add footer
        footer = QLabel("A tool by ClipmodeGo")
        footer.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 10px;
            background-color: {COLORS['darkest']};
            border-top: 1px solid {COLORS['primary']};
            font-style: italic;
        """)
        footer.setAlignment(Qt.AlignCenter)
        
        # Set layouts
        central_widget.setLayout(container)
        
        # Add all elements to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(central_widget)
        main_layout.addWidget(footer)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a widget to hold the main layout
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        
        # Center the window
        self.center()
    
    def update_progress(self, progress, status):
        """Update progress bar and status label."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        QApplication.processEvents()  # Ensure UI updates
    
    def refresh_video_lists(self):
        """Refresh the input and output video lists."""
        print("Refreshing video lists...")
        # Clear lists
        self.input_video_list.clear()
        self.output_video_list.clear()
        
        # Update paths from text fields
        self.input_video_path = self.input_video_path_label.text()
        self.input_audio_path = self.input_audio_path_label.text()
        self.output_path = self.output_path_label.text()
        
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
    
    def browse_directory(self, dir_type):
        """Browse for a directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            f"Select {dir_type.title()} Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            if dir_type == "input_video":
                self.input_video_path = directory
                self.input_video_path_label.setText(directory)
            elif dir_type == "output":
                self.output_path = directory
                self.output_path_label.setText(directory)
            
            self.refresh_video_lists()
    
    def browse_file(self, file_type):
        """Browse for a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {file_type.title()} File",
            "",
            (
                "Audio Files (*.mp3 *.wav *.ogg)" if file_type == "input_audio" else
                "Video Files (*.mov *.mp4 *.webm *.mkv)" if file_type == "overlay_video" else
                "All Files (*.*)"
            )
        )
        
        if file_path:
            if file_type == "input_audio":
                self.input_audio_path = file_path
                self.input_audio_path_label.setText(file_path)
            elif file_type == "overlay_video":
                self.overlay_video_path = file_path
                self.overlay_video_path_label.setText(file_path)
                if not self.use_overlay_checkbox.isChecked():
                    self.use_overlay_checkbox.setChecked(True)
    
    def generate_videos(self):
        """Generate videos with the selected settings."""
        # Ensure we have audio
        if not os.path.exists(self.input_audio_path):
            QMessageBox.warning(self, "Warning", "No audio file selected. Please select an audio file.")
            return
            
        # Ensure we have input videos
        input_videos = get_video_files(self.input_video_path)
        if len(input_videos) == 0:
            QMessageBox.warning(self, "Warning", "No input videos found. Please add videos to the input directory.")
            return
            
        # Validate output path - make sure it exists and we can write to it
        try:
            # Create output directory if it doesn't exist
            os.makedirs(self.output_path, exist_ok=True)
            
            # Test if we can write to the output directory
            test_file = os.path.join(self.output_path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            # If there's an issue with the output path, show a warning and suggest a simpler path
            simple_path = os.path.expanduser("~/Desktop/scramble_output")
            error_msg = f"Error with output path: {str(e)}\n\nThe path may contain spaces or special characters that are causing issues. Would you like to use a simpler path?\n\n{simple_path}"
            reply = QMessageBox.question(self, "Output Path Error", error_msg, 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            
            if reply == QMessageBox.Yes:
                self.output_path = simple_path
                os.makedirs(self.output_path, exist_ok=True)
                self.output_path_label.setText(f"Output Path: {self.output_path}")
            else:
                return
            
        # Print debug info
        print(f"Starting video generation with parameters:")
        print(f"- Input videos: {input_videos[:5] if len(input_videos) >= 5 else input_videos}... ({len(input_videos)} total)")
        print(f"- Input audio: {self.input_audio_path}")
        print(f"- Output directory: {self.output_path}")
        print(f"- Target duration: {self.duration_spinner.value()}s")
        print(f"- Overlay enabled: {self.use_overlay_checkbox.isChecked()}  Path: {self.overlay_video_path}")
        
        # Update UI
        self.status_label.setText("Starting generation...")
        self.progress_bar.setValue(0)
        QApplication.processEvents()
        
        # Disable UI
        self.setEnabled(False)
        # Enable cancel button during generation
        self.cancel_btn.setEnabled(True)
        QApplication.processEvents()
        
        try:
            # Start the generation process in a separate thread
            num_videos = self.num_videos_spinner.value()
            use_ai = self.use_ai_checkbox.isChecked()
            use_effects = self.use_effects_checkbox.isChecked()
            use_text = self.use_text_checkbox.isChecked()
            
            # Get custom text if text overlay is enabled
            custom_text = None
            if use_text:
                custom_text = self.text_input.text().strip()
                # If no custom text is provided but text overlay is enabled,
                # use automatic captions
                if not custom_text:
                    custom_text = None
            
            # Create thread
            self.generate_thread = QThread()
            self.generate_worker = GenerateWorker(
                num_videos=num_videos,
                input_video_path=self.input_video_path,
                input_audio_path=self.input_audio_path,
                output_path=self.output_path,
                base_name=self.basename_input.text(),
                target_duration=self.duration_spinner.value(),
                overlay_video_path=self.overlay_video_path if self.use_overlay_checkbox.isChecked() else None,
                use_ai=use_ai,
                use_effects=use_effects,
                use_text=use_text,
                custom_text=custom_text,
                font_name=self.font_combo.currentFont().family(),
                bold=self.bold_checkbox.isChecked(),
                italic=self.italic_checkbox.isChecked(),
                underline=self.underline_checkbox.isChecked(),
                text_position=self.position_combo.currentText().lower(),
                speed_factor=self.get_speed_factor(),
                effects_intensity=self.intensity_slider.value(),
                effects_style=self.effects_style_combo.currentText().lower()
            )
            
            # Move worker to thread
            self.generate_worker.moveToThread(self.generate_thread)
            
            # Connect signals
            self.generate_thread.started.connect(self.generate_worker.run)
            self.generate_worker.progress.connect(self.update_progress)
            self.generate_worker.finished.connect(self.generation_finished)
            self.generate_worker.error.connect(self.show_error)
            self.generate_worker.finished.connect(self.generate_thread.quit)
            self.generate_worker.finished.connect(self.generate_worker.deleteLater)
            self.generate_thread.finished.connect(self.generate_thread.deleteLater)
            
            # Start thread
            self.generate_thread.start()
            
            # Return immediately, allow cancel during generation
            return
        except Exception as e:
            self.setEnabled(True)
            import traceback
            traceback_str = traceback.format_exc()
            error_msg = f"Error starting generation: {str(e)}\n\n{traceback_str}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def show_error(self, message):
        """Show error message (called from main thread)."""
        self.setEnabled(True)  # Re-enable UI
        # Disable cancel button
        self.cancel_btn.setEnabled(False)
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['dark']};
                color: {COLORS['text']};
            }}
            QPushButton {{
                background-color: {COLORS['darker']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['primary']};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: black;
            }}
        """)
        msg_box.exec_()
    
    def generation_finished(self):
        """Handle generation completion."""
        self.setEnabled(True)
        # Disable cancel button when done
        self.cancel_btn.setEnabled(False)
        
        # Match files based on base name prefix
        prefix = self.basename_input.text() or 'output'
        output_files = [f for f in os.listdir(self.output_path) if f.endswith('.mp4') and f.startswith(f"{prefix}_")]
        print(f"Found {len(output_files)} output files in {self.output_path}")
        
        if not output_files:
            QMessageBox.warning(self, "Warning", 
                f"No output videos were found in {self.output_path}. "
                "The generation process completed but no videos were created.")
        else:
            QMessageBox.information(self, "Success", 
                f"Successfully generated {len(output_files)} videos in {self.output_path}!")
                
        self.refresh_video_lists()
    
    def add_input_video(self):
        """Add a video file to the input directory."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.mov *.avi *.mkv)"
        )
        
        if files:
            for file_path in files:
                # Copy file to input directory
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(self.input_video_path, filename)
                    shutil.copy2(file_path, dest_path)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Error copying file: {str(e)}")
            
            # Refresh the list
            self.refresh_video_lists()
    
    def remove_video(self, list_widget):
        """Remove a video file from its directory."""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Please select a video to remove")
            return
            
        selected_name = selected_items[0].text()
        
        # Determine if it's an input or output video
        if list_widget == self.input_video_list:
            video_path = os.path.join(self.input_video_path, selected_name)
        else:
            video_path = os.path.join(self.output_path, selected_name)
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete {selected_name}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(video_path)
                self.refresh_video_lists()
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error deleting file: {str(e)}")
    
    def open_output_folder(self):
        """Open the output folder in the file explorer."""
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', self.output_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.output_path)
            else:  # Linux
                subprocess.call(('xdg-open', self.output_path))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder: {str(e)}")
    
    def center(self):
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def toggle_text_input(self, state):
        """Show or hide the text input field based on the state of the text checkbox."""
        if state == Qt.Checked:
            self.text_input_label.setVisible(True)
            self.text_input.setVisible(True)
            self.font_combo.setVisible(True)
            self.bold_checkbox.setVisible(True)
            self.italic_checkbox.setVisible(True)
            self.underline_checkbox.setVisible(True)
            self.position_combo.setVisible(True)
            
            # First time the text checkbox is checked, show ImageMagick info
            if not hasattr(self, '_text_info_shown'):
                try:
                    # Try to import a module that requires ImageMagick
                    from moviepy.config import get_setting
                    magick_path = get_setting("IMAGEMAGICK_BINARY")
                    if magick_path == "unset" or not os.path.exists(magick_path):
                        raise Exception("ImageMagick not properly configured")
                except Exception:
                    # Show info about ImageMagick if it's not available
                    QMessageBox.information(self, "Text Overlay Info",
                        "For best text quality, ImageMagick should be installed.\n\n"
                        "Without ImageMagick, a simplified text style will be used. "
                        "Videos will still be created successfully, but text effects "
                        "may be limited.\n\n"
                        "This is only needed for high-quality text overlays.")
                    self._text_info_shown = True
        else:
            self.text_input_label.setVisible(False)
            self.text_input.setVisible(False)
            self.font_combo.setVisible(False)
            self.bold_checkbox.setVisible(False)
            self.italic_checkbox.setVisible(False)
            self.underline_checkbox.setVisible(False)
            self.position_combo.setVisible(False)

    # Add tooltip for the AI feature
    def use_ai_checkbox_tooltip(self):
        QMessageBox.information(self, "AI Feature Info",
            "When enabled, AI analyzes video content to:\n"
            "• Select the most interesting video segments\n"
            "• Avoid repetitive content across output videos\n"
            "• Ensure visual variety in generated videos\n"
            "\n"
            "The AI scores clips based on motion, visual complexity, and more."
        )

    # Add tooltip for the AI Effects feature
    def use_effects_checkbox_tooltip(self):
        QMessageBox.information(self, "AI Effects Feature Info",
            "When enabled, AI will enhance videos with:\n"
            "• Smart transitions between clips\n"
            "• Visual effects based on content analysis\n"
            "• Timed effects synced with audio\n"
            "\n"
            "Effects are chosen based on clip content and energy."
        )

    def cancel_generation(self):
        """Cancel the ongoing video generation."""
        if hasattr(self, 'generate_thread') and self.generate_thread.isRunning():
            # Terminate the thread (force stop)
            self.generate_thread.terminate()
            self.generate_thread.wait()
        self.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Generation canceled")
        self.cancel_btn.setEnabled(False)

    def get_speed_factor(self):
        mapping = {
            0: 1.0,
            1: 1.25,
            2: 1.5,
            3: 1.75
        }
        return mapping.get(self.speed_combo.currentIndex(), 1.0)

    # ---------- Project save/load ----------
    def collect_state(self):
        """Return dict representing current UI state."""
        # Safely get selected effects style or default
        combo = getattr(self, 'effects_style_combo', None)
        effects_style = combo.currentText() if combo else 'classic'
        state = {
            "input_video_path": self.input_video_path_label.text(),
            "input_audio_path": self.input_audio_path_label.text(),
            "output_path": self.output_path_label.text(),
            "num_videos": self.num_videos_spinner.value(),
            "base_name": self.basename_input.text(),
            "use_ai": self.use_ai_checkbox.isChecked(),
            "use_effects": self.use_effects_checkbox.isChecked(),
            "effects_style": effects_style,
            "use_text": self.use_text_checkbox.isChecked(),
            "custom_text": self.text_input.text(),
            "font_name": self.font_combo.currentFont().family(),
            "bold": self.bold_checkbox.isChecked(),
            "italic": self.italic_checkbox.isChecked(),
            "underline": self.underline_checkbox.isChecked(),
            "text_position": self.position_combo.currentText(),
            "speed_index": self.speed_combo.currentIndex(),
            "effects_intensity": self.intensity_slider.value(),
            "overlay_video_path": self.overlay_video_path,
            "use_overlay": self.use_overlay_checkbox.isChecked(),
            "duration": self.duration_spinner.value()
        }
        return state

    def apply_state(self, state):
        """Apply state dict to UI."""
        self.input_video_path_label.setText(state.get("input_video_path", self.input_video_path))
        self.input_audio_path_label.setText(state.get("input_audio_path", self.input_audio_path))
        self.output_path_label.setText(state.get("output_path", self.output_path))

        self.num_videos_spinner.setValue(state.get("num_videos", 5))
        self.use_ai_checkbox.setChecked(state.get("use_ai", True))
        self.use_effects_checkbox.setChecked(state.get("use_effects", False))
        # Safely restore effects style selection
        combo = getattr(self, 'effects_style_combo', None)
        if combo:
            combo.setCurrentText(state.get("effects_style", "Classic"))
        self.use_text_checkbox.setChecked(state.get("use_text", False))
        self.text_input.setText(state.get("custom_text", ""))

        # font
        font_name = state.get("font_name", "Arial")
        self.font_combo.setCurrentFont(QFont(font_name))
        self.bold_checkbox.setChecked(state.get("bold", False))
        self.italic_checkbox.setChecked(state.get("italic", False))
        self.underline_checkbox.setChecked(state.get("underline", False))
        self.position_combo.setCurrentText(state.get("text_position", "Top"))
        self.speed_combo.setCurrentIndex(state.get("speed_index", 0))
        self.intensity_slider.setValue(state.get("effects_intensity", 50))

        # overlay video
        self.overlay_video_path = state.get("overlay_video_path", "")
        self.overlay_video_path_label.setText(self.overlay_video_path)

        # use overlay
        self.use_overlay_checkbox.setChecked(state.get("use_overlay", False))

        # duration
        self.duration_spinner.setValue(state.get("duration", 16))

        # Restore base name
        self.basename_input.setText(state.get("base_name", "output"))

        # Refresh lists with new paths
        self.refresh_video_lists()

    def save_project(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "Scramble Project (*.scp)", options=options)
        if file_path:
            if not file_path.endswith(".scp"):
                file_path += ".scp"
            try:
                with open(file_path, "w") as f:
                    json.dump(self.collect_state(), f, indent=2)
                QMessageBox.information(self, "Saved", f"Project saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save project: {e}")

    def load_project(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "Scramble Project (*.scp)", options=options)
        if file_path:
            try:
                with open(file_path, "r") as f:
                    state = json.load(f)
                self.apply_state(state)
                QMessageBox.information(self, "Loaded", f"Project loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load project: {e}")

    def toggle_overlay_input(self, state):
        """Enable/disable overlay controls visibility."""
        enabled = state == Qt.Checked
        self.overlay_video_path_label.setEnabled(enabled)
        self.browse_overlay_btn.setEnabled(enabled)
        # nothing else for now

class GenerateWorker(QObject):
    """Worker thread for video generation."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, num_videos, input_video_path, input_audio_path, output_path, base_name="output", target_duration=16, overlay_video_path=None, use_ai=True, use_effects=False, use_text=False, custom_text=None, font_name=None, bold=False, italic=False, underline=False, text_position="top", speed_factor=1.0, effects_intensity=50, effects_style='classic'):
        super().__init__()
        self.num_videos = num_videos
        self.input_video_path = input_video_path
        self.input_audio_path = input_audio_path
        self.output_path = output_path
        self.base_name = base_name
        self.target_duration = target_duration
        self.overlay_video_path = overlay_video_path
        self.use_ai = use_ai
        self.use_effects = use_effects
        self.use_text = use_text
        self.custom_text = custom_text
        self.font_name = font_name
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.text_position = text_position
        self.speed_factor = speed_factor
        self.effects_intensity = effects_intensity
        self.effects_style = effects_style
    
    def run(self):
        """Run the video generation process."""
        try:
            # Print debug info
            print(f"Starting generation with:")
            print(f"- Videos: {self.num_videos}")
            print(f"- Input video path: {self.input_video_path}")
            print(f"- Input audio path: {self.input_audio_path}")
            print(f"- Overlay video path: {self.overlay_video_path}")
            print(f"- Target duration: {self.target_duration}s")
            print(f"- Output path: {self.output_path}")
            print(f"- Use AI: {self.use_ai}")
            print(f"- Use Effects: {self.use_effects}")
            print(f"- Use Text: {self.use_text}")
            print(f"- Custom Text: {self.custom_text}")
            
            # Verify paths exist
            if not os.path.exists(self.input_video_path):
                self.error.emit(f"Input video path does not exist: {self.input_video_path}")
                return
                
            if not os.path.exists(self.input_audio_path):
                self.error.emit(f"Input audio path does not exist: {self.input_audio_path}")
                return
                
            # Optional overlay video path check (only if provided)
            if self.overlay_video_path:
                if not os.path.exists(self.overlay_video_path):
                    self.error.emit(f"Overlay video path does not exist: {self.overlay_video_path}")
                    return
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_path, exist_ok=True)
            
            # Get list of input video files
            input_videos = get_video_files(self.input_video_path)
            if not input_videos:
                self.error.emit(f"No video files found in: {self.input_video_path}")
                return
                
            # Define progress callback
            def progress_callback(progress, status):
                self.progress.emit(progress, status)
                print(f"Progress: {progress}%, Status: {status}")
            
            # Call generate_batch with the updated signature
            generate_batch(
                input_videos=input_videos,
                audio_files=[self.input_audio_path],
                num_videos=self.num_videos,
                min_clips=10,
                max_clips=30,
                min_clip_duration=1.5,
                max_clip_duration=3.5,
                output_dir=self.output_path,
                base_name=self.base_name,
                use_effects=self.use_effects,
                use_text=self.use_text,
                custom_text=self.custom_text,
                font_name=self.font_name,
                bold=self.bold,
                italic=self.italic,
                underline=self.underline,
                text_position=self.text_position,
                speed_factor=self.speed_factor,
                effects_intensity=self.effects_intensity,
                effects_style=self.effects_style,
                overlay_video_path=self.overlay_video_path if self.overlay_video_path else None,
                target_duration=self.target_duration,
                progress_callback=progress_callback
            )
            
            # Print paths again for verification
            print(f"Generation completed. Files should be in: {self.output_path}")
            if os.path.exists(self.output_path):
                files = os.listdir(self.output_path)
                print(f"Files in output directory: {files}")
            else:
                print(f"Output path does not exist: {self.output_path}")
            
            self.finished.emit()
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            error_msg = f"Error generating videos: {str(e)}\n\n{traceback_str}"
            print(error_msg)
            self.error.emit(error_msg)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style as base for consistent cross-platform look
    window = ScrambleClipGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
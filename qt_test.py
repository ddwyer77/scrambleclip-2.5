"""
This is a simple test script using PyQt5 instead of Tkinter.
You'll need to install PyQt5 first with:
pip install PyQt5
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

class SimpleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Test Window")
        self.setGeometry(100, 100, 400, 300)
        
        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        label = QLabel("This is a PyQt5 test window")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        # Add a button
        button = QPushButton("Click Me")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)
        
        print("PyQt5 window created")
    
    def on_button_click(self):
        print("Button clicked!")

if __name__ == "__main__":
    print("Starting PyQt5 application")
    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    print("Window shown, entering event loop")
    sys.exit(app.exec_()) 
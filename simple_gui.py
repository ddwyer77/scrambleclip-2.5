import tkinter as tk
from tkinter import ttk

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple GUI Test")
        self.root.geometry("600x400")
        self.root.configure(bg="lightgray")  # Set a visible background color
        
        # Create a main frame with visible border and background
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label
        label = ttk.Label(main_frame, text="Scramble Clip 2", font=("Arial", 20, "bold"))
        label.pack(pady=20)
        
        # Add a button
        button = ttk.Button(main_frame, text="Test Button", command=self.on_button_click)
        button.pack(pady=10)
        
        # Add an entry field
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(entry_frame, text="Test Input:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(entry_frame, width=30)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        # Add a status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=10)
        
        print("All simple GUI widgets created")
    
    def on_button_click(self):
        self.status_var.set(f"Button clicked! Entry value: {self.entry.get()}")
        print("Button clicked")

if __name__ == "__main__":
    print("Creating root window")
    root = tk.Tk()
    print("Creating SimpleGUI instance")
    app = SimpleGUI(root)
    print("Starting mainloop")
    root.mainloop() 
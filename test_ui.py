import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Tkinter Test")
    root.geometry("400x300")
    
    # Create a label
    label = ttk.Label(root, text="This is a test label")
    label.pack(pady=20)
    
    # Create a button
    button = ttk.Button(root, text="Test Button", command=lambda: print("Button clicked"))
    button.pack(pady=10)
    
    print("UI elements created and packed")
    
    root.mainloop()
    
if __name__ == "__main__":
    print("Starting test UI")
    main() 
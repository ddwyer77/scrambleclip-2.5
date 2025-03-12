import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Basic Tkinter Test")
    root.geometry("500x400")
    root.configure(bg="lightblue")
    
    # Create basic tkinter widgets (not ttk)
    label = tk.Label(root, text="Basic Tkinter Test", font=("Arial", 16), bg="lightblue")
    label.pack(pady=20)
    
    button = tk.Button(root, text="Click Me", command=lambda: print("Button clicked"))
    button.pack(pady=10)
    
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    entry.insert(0, "Test text")
    
    text = tk.Text(root, width=40, height=5)
    text.pack(pady=10)
    text.insert(tk.END, "This is a test text area.\nIt should be visible.")
    
    print("Basic UI elements created and packed")
    root.mainloop()

if __name__ == "__main__":
    print("Starting basic GUI")
    main() 
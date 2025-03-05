import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk, font
import re
import pandas as pd


class TextEditor():
    def __init__(self, root):
        self.root = root
        self.root.title("Text Editor")

        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()

        self.initialWidth = int(screenWidth * 0.7)
        self.initialHeight = int(screenHeight * 0.6)

        self.root.geometry(f"{self.initialWidth}x{self.initialHeight}")
        self.root.resizable(True, True) 

        self.widgets()
        self.shortcuts()

        # Variables for find functionality
        self.find_text = ""
        self.search_start = "1.0"


    def shortcuts(self):
        self.root.bind("<Control-s>", lambda event: self.saveFile())
        self.root.bind("<Control-o>", lambda event: self.openFile())
        self.root.bind("<Control-f>", self.search)
        self.root.bind("<Control-n>", self.find_next)  # Bind Ctrl+N for "Find Next"
    

    def menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Open", command=self.openFile, accelerator="Ctrl + O")
        fileMenu.add_command(label="Save As", command=self.saveFile, accelerator="Ctrl + S")
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.root.quit)

        # Edit Menu
        editMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Find", command=self.search, accelerator="Ctrl + F")
        editMenu.add_command(label="Find Next", command=self.find_next, accelerator="Ctrl + N")

        # Adjust the font for a lighter accelerator text
        menu_font = font.Font(family="Segoe UI", size=9, weight="normal")
        fileMenu.configure(font=menu_font)
        editMenu.configure(font=menu_font)
        menubar.configure(font=menu_font)

        # Add a postcommand to adjust the width dynamically
        fileMenu.postcommand = lambda: self.adjust_menu_width(fileMenu)
        editMenu.postcommand = lambda: self.adjust_menu_width(editMenu)
       

    def widgets(self):
        self.menu()
        # Top Frame for controls
        mainFrame = ttk.Frame(self.root)
        mainFrame.grid(row=0, column=0, padx=10, pady=(15, 5), sticky="ew")
        
        # Configure the second column of mainFrame to expand with resizing
        mainFrame.columnconfigure(1, weight=1)

        self.browseButton = ttk.Button(mainFrame, text="Open", command=self.openFile)
        self.browseButton.grid(row=0, column=0, padx=(10, 5))

        self.browseEntry = ttk.Entry(mainFrame)
        self.browseEntry.grid(row=0, column=1, padx=(0, 30), sticky="ew")

        self.fontLabel = ttk.Label(mainFrame, text="Font")
        self.fontLabel.grid(row=0, column=2, padx=(0, 5))

        # Add basic Windows fonts to fontSelect combobox
        fonts = sorted(["Arial", "Calibri", "Cambria", "Comic Sans MS", "Courier New", "Georgia", "Segoe UI", "Times New Roman", "Verdana"])
        self.fontSelect = ttk.Combobox(mainFrame, state="readonly", values=fonts, width=15)
        self.fontSelect.grid(row=0, column=3, padx=(0, 5))
        self.fontSelect.bind("<<ComboboxSelected>>", self.updateFont)
        self.fontSelect.set("Courier New")

        # Add font sizes up to 72 in fontSizeSelect combobox
        fontSizes = list(range(8, 73, 2))
        self.fontSizeSelect = ttk.Combobox(mainFrame, state="readonly", values=fontSizes, width=5)
        self.fontSizeSelect.grid(row=0, column=4, padx=(0, 10))
        self.fontSizeSelect.bind("<<ComboboxSelected>>", self.updateFontSize)
        self.fontSizeSelect.set("10")

        # Text Frame containing Text widget and Scrollbar
        textFrame = ttk.Frame(self.root)
        textFrame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(10, 10))
        
        self.textEntry = tk.Text(textFrame, wrap="word", undo=True, padx = 5, pady = 5)
        self.textEntry.grid(row=0, column=0, sticky="nsew", padx = 10, pady = 10)

        # Scrollbar for Text widget
        scrollbar = ttk.Scrollbar(textFrame, orient="vertical", command=self.textEntry.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.textEntry.config(yscrollcommand=scrollbar.set)

        # Configure grid weights to ensure resizing works properly
        textFrame.columnconfigure(0, weight=1)
        textFrame.rowconfigure(0, weight=1)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Top frame shouldn't resize vertically
        self.root.rowconfigure(1, weight=1)  # Text widget should resize

        # Initialize font settings
        self.currentFont = font.Font(family = "Courier New", size = 12)
        self.textEntry.configure(font = self.currentFont)


    def openFile(self):
        filePath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

        if not filePath:
            return 
        
        self.browseEntry.delete(0, tk.END)
        self.browseEntry.insert(0, filePath)

        try:
            with open(filePath, "r") as file:
                content = file.read()
                self.textEntry.delete(1.0, tk.END)  # Clear any existing content
                self.textEntry.insert(tk.END, content)  # Insert the file content
            
        except Exception as e:
            print(f"Error, Could not read the text file: {e}")


    def saveFile(self):
        content = self.textEntry.get(1.0, tk.END).strip()

        saveLocation = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt"), ("All Files", "*.*")])

        if saveLocation:
            with open(saveLocation, "w") as file:
                file.write(content)


    def updateFont(self, event=None):
        selectedFont = self.fontSelect.get()
        self.currentFont.config(family=selectedFont)


    def updateFontSize(self, event=None):
        selectedSize = self.fontSizeSelect.get()
        self.currentFont.config(size=int(selectedSize))


    def search(self, event=None):
        find_dialog = tk.Toplevel(self.root)
        find_dialog.title("Find")
        find_dialog.transient(self.root)

        tk.Label(find_dialog, text="Find:").grid(row=0, column=0, padx=4, pady=4)
        find_entry = ttk.Entry(find_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=4, pady=4)
        find_entry.focus_set()

        def on_find():
            self.find_text = find_entry.get()
            self.search_start = "1.0"
            self.find_next()
            find_dialog.destroy()

        find_button = ttk.Button(find_dialog, text="Find", command=on_find)
        find_button.grid(row=0, column=2, padx=4, pady=4)

        find_dialog.bind("<Return>", lambda event: on_find())
        find_dialog.bind("<Escape>", lambda event: find_dialog.destroy())


    def find_next(self, event=None):
        if self.find_text:
            start_pos = self.textEntry.search(self.find_text, self.search_start, stopindex=tk.END)
            if start_pos:
                end_pos = f"{start_pos}+{len(self.find_text)}c"
                self.textEntry.tag_remove("highlight", "1.0", tk.END)  # Remove previous highlights
                self.textEntry.tag_add("highlight", start_pos, end_pos)
                self.textEntry.tag_config("highlight", background="yellow")
                self.textEntry.mark_set(tk.INSERT, end_pos)
                self.search_start = end_pos  # Update search_start to continue searching
                self.textEntry.see(start_pos)  # Scroll to the found text
            else:
                messagebox.showinfo("Find", "No more occurrences found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()
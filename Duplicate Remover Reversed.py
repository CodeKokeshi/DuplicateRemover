import os
import tkinter as tk
from tkinter import messagebox, filedialog

class FileFinderDeleterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Deleter (Reversed)")
        self.root.geometry("600x400")  # Set a fixed resolution


        self.selected_folder = tk.StringVar()
        self.search_keyword = tk.StringVar()
        self.file_vars = []  # Keep track of selected files
        self.root.resizable(width=False, height=False)

        self.create_widgets()

    def create_widgets(self):
        # Folder Selector
        folder_label = tk.Label(self.root, text="Select Folder:")
        folder_label.pack()

        self.folder_entry = tk.Entry(self.root, textvariable=self.selected_folder, state="readonly")
        self.folder_entry.pack(fill=tk.X, padx=10, pady=5)

        browse_button = tk.Button(self.root, text="Browse Folder", command=self.browse_folder)
        browse_button.pack(padx=10, pady=5)

        # Search Bar
        search_label = tk.Label(self.root, text="Search Keyword: (Type the keyword you want to except. Example: (USA) then\n(USA) will not be shown in the results.)")
        search_label.pack()

        self.search_entry = tk.Entry(self.root, textvariable=self.search_keyword)
        self.search_entry.pack(fill=tk.X, padx=10, pady=5)

        search_button = tk.Button(self.root, text="Search", command=self.search_files)
        search_button.pack(padx=10, pady=5)

        # File Listbox
        self.file_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)


        # Delete Button
        delete_button = tk.Button(self.root, text="Delete Selected", command=self.delete_selected)
        delete_button.pack(padx=10, pady=5)


    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.selected_folder.set(folder_path)

    def search_files(self):
        self.file_listbox.delete(0, tk.END)
        search_keyword = self.search_keyword.get().lower()  # Convert search keyword to lowercase
        folder_path = self.selected_folder.get()

        if not search_keyword or not folder_path:
            return

        for filename in os.listdir(folder_path):
            if search_keyword not in filename.lower():  # Convert filename to lowercase before comparing
                self.file_listbox.insert(tk.END, filename)

    def delete_selected(self):
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return

        selected_files = [self.file_listbox.get(index) for index in selected_indices]
        folder_path = self.selected_folder.get()

        for filename in selected_files:
            file_path = os.path.join(folder_path, filename)
            try:
                os.remove(file_path)
                self.file_listbox.delete(self.file_listbox.get(0, tk.END).index(filename))
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting {filename}: {e}")


if __name__ == "__main__":
    root = tk.Tk()

    app = FileFinderDeleterApp(root)
    root.mainloop()

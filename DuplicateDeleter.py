import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import time
from collections import defaultdict
import hashlib

class AdvancedFileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Manager & Duplicate Remover")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Variables
        self.selected_folder = tk.StringVar()
        self.search_keyword = tk.StringVar()
        self.search_mode = tk.StringVar(value="include")  # include or exclude
        self.case_sensitive = tk.BooleanVar()
        self.include_subdirs = tk.BooleanVar(value=True)
        self.file_extension_filter = tk.StringVar()
        
        # Threading
        self.search_thread = None
        self.progress_queue = queue.Queue()
        self.is_searching = False
        
        # File data
        self.file_data = []
        self.duplicate_groups = []
        
        # Style configuration
        self.setup_styles()
        self.create_widgets()
        self.setup_bindings()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors and styles
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Search.TButton', font=('Arial', 9, 'bold'))
        style.configure('Delete.TButton', font=('Arial', 9, 'bold'), foreground='white')
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Advanced File Manager & Duplicate Remover", style='Title.TLabel')
        title_label.pack(pady=(0, 15))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # File Search Tab
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="File Search & Delete")
        self.create_search_tab()
        
        # Duplicate Finder Tab
        self.duplicate_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.duplicate_frame, text="Duplicate Finder")
        self.create_duplicate_tab()
        
    def create_search_tab(self):
        # Folder selection frame
        folder_frame = ttk.LabelFrame(self.search_frame, text="Folder Selection", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(folder_frame, text="Selected Folder:").pack(anchor=tk.W)
        folder_entry_frame = ttk.Frame(folder_frame)
        folder_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.folder_entry = ttk.Entry(folder_entry_frame, textvariable=self.selected_folder, state="readonly")
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(folder_entry_frame, text="Browse", command=self.browse_folder)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Search options frame
        options_frame = ttk.LabelFrame(self.search_frame, text="Search Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search keyword
        ttk.Label(options_frame, text="Search Keyword:").pack(anchor=tk.W)
        self.search_entry = ttk.Entry(options_frame, textvariable=self.search_keyword)
        self.search_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Options row 1
        options_row1 = ttk.Frame(options_frame)
        options_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(options_row1, text="Search Mode:").pack(side=tk.LEFT)
        mode_frame = ttk.Frame(options_row1)
        mode_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Radiobutton(mode_frame, text="Include files with keyword", variable=self.search_mode, value="include").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Exclude files with keyword", variable=self.search_mode, value="exclude").pack(side=tk.LEFT, padx=(10, 0))
        
        # Options row 2
        options_row2 = ttk.Frame(options_frame)
        options_row2.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Checkbutton(options_row2, text="Case sensitive", variable=self.case_sensitive).pack(side=tk.LEFT)
        ttk.Checkbutton(options_row2, text="Include subdirectories", variable=self.include_subdirs).pack(side=tk.LEFT, padx=(20, 0))
        
        # File extension filter
        ext_frame = ttk.Frame(options_frame)
        ext_frame.pack(fill=tk.X)
        
        ttk.Label(ext_frame, text="File extension filter (e.g., .txt,.pdf):").pack(side=tk.LEFT)
        ttk.Entry(ext_frame, textvariable=self.file_extension_filter, width=20).pack(side=tk.LEFT, padx=(10, 0))
        
        # Search button and progress
        search_control_frame = ttk.Frame(self.search_frame)
        search_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_button = ttk.Button(search_control_frame, text="Search Files", command=self.search_files, style='Search.TButton')
        self.search_button.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(search_control_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(self.search_frame, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # File list with scrollbar
        list_frame = ttk.Frame(results_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for better file display
        columns = ('Name', 'Size', 'Modified', 'Path')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', selectmode='extended')
        
        # Configure columns
        self.file_tree.heading('#0', text='', anchor=tk.W)
        self.file_tree.column('#0', width=30, minwidth=30)
        self.file_tree.heading('Name', text='File Name')
        self.file_tree.column('Name', width=250, minwidth=150)
        self.file_tree.heading('Size', text='Size')
        self.file_tree.column('Size', width=80, minwidth=60)
        self.file_tree.heading('Modified', text='Modified')
        self.file_tree.column('Modified', width=120, minwidth=100)
        self.file_tree.heading('Path', text='Full Path')
        self.file_tree.column('Path', width=300, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Action buttons
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Select All", command=self.select_all_files).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="Deselect All", command=self.deselect_all_files).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(action_frame, text="Preview Selected", command=self.preview_selected).pack(side=tk.LEFT, padx=(5, 0))
        
        self.delete_button = ttk.Button(action_frame, text="Delete Selected Files", command=self.delete_selected, style='Delete.TButton')
        self.delete_button.pack(side=tk.RIGHT)
        
        self.status_label = ttk.Label(results_frame, text="Ready")
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
    def create_duplicate_tab(self):
        # Duplicate finder controls
        dup_control_frame = ttk.LabelFrame(self.duplicate_frame, text="Duplicate Detection", padding=10)
        dup_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dup_control_frame, text="Find duplicate files in the selected folder").pack(anchor=tk.W)
        
        dup_button_frame = ttk.Frame(dup_control_frame)
        dup_button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.find_duplicates_button = ttk.Button(dup_button_frame, text="Find Duplicates", command=self.find_duplicates)
        self.find_duplicates_button.pack(side=tk.LEFT)
        
        self.dup_progress_bar = ttk.Progressbar(dup_button_frame, mode='determinate')
        self.dup_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Duplicate results
        dup_results_frame = ttk.LabelFrame(self.duplicate_frame, text="Duplicate Groups", padding=10)
        dup_results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Duplicate tree
        dup_list_frame = ttk.Frame(dup_results_frame)
        dup_list_frame.pack(fill=tk.BOTH, expand=True)
        
        dup_columns = ('Group', 'Files', 'Size', 'Total Size')
        self.dup_tree = ttk.Treeview(dup_list_frame, columns=dup_columns, show='tree headings', selectmode='extended')
        
        self.dup_tree.heading('#0', text='', anchor=tk.W)
        self.dup_tree.column('#0', width=30, minwidth=30)
        self.dup_tree.heading('Group', text='Group')
        self.dup_tree.column('Group', width=100, minwidth=80)
        self.dup_tree.heading('Files', text='File Count')
        self.dup_tree.column('Files', width=80, minwidth=60)
        self.dup_tree.heading('Size', text='File Size')
        self.dup_tree.column('Size', width=100, minwidth=80)
        self.dup_tree.heading('Total Size', text='Total Wasted')
        self.dup_tree.column('Total Size', width=120, minwidth=100)
        
        dup_v_scrollbar = ttk.Scrollbar(dup_list_frame, orient=tk.VERTICAL, command=self.dup_tree.yview)
        self.dup_tree.configure(yscrollcommand=dup_v_scrollbar.set)
        
        self.dup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dup_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Duplicate actions
        dup_action_frame = ttk.Frame(dup_results_frame)
        dup_action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(dup_action_frame, text="Keep Oldest", command=lambda: self.auto_select_duplicates('oldest')).pack(side=tk.LEFT)
        ttk.Button(dup_action_frame, text="Keep Newest", command=lambda: self.auto_select_duplicates('newest')).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(dup_action_frame, text="Delete Selected Duplicates", command=self.delete_selected_duplicates).pack(side=tk.RIGHT)        
    def setup_bindings(self):
        # Keyboard shortcuts
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<F5>', lambda e: self.search_files())
        self.root.bind('<Delete>', lambda e: self.delete_selected())
        self.search_entry.bind('<Return>', lambda e: self.search_files())
        
        # Double-click to open file location
        self.file_tree.bind('<Double-1>', self.open_file_location)
        self.dup_tree.bind('<Double-1>', self.open_duplicate_location)
        
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder to search")
        if folder_path:
            self.selected_folder.set(folder_path)
            
    def format_file_size(self, size_bytes):
        """Convert bytes to human readable format"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def get_file_info(self, file_path):
        """Get file information including size and modification time"""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            modified = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
            return size, modified
        except:
            return 0, "Unknown"
            
    def search_files_worker(self):
        """Worker thread for file searching"""
        try:
            folder_path = self.selected_folder.get()
            search_keyword = self.search_keyword.get()
            search_mode = self.search_mode.get()
            case_sensitive = self.case_sensitive.get()
            include_subdirs = self.include_subdirs.get()
            extension_filter = self.file_extension_filter.get().strip()
            
            if not case_sensitive:
                search_keyword = search_keyword.lower()
                
            # Parse extension filter
            extensions = []
            if extension_filter:
                extensions = [ext.strip() for ext in extension_filter.split(',') if ext.strip()]
                extensions = [ext if ext.startswith('.') else '.' + ext for ext in extensions]
            
            found_files = []
            total_files = 0
            
            # Count total files first for progress
            for root, dirs, files in os.walk(folder_path):
                if not include_subdirs and root != folder_path:
                    continue
                total_files += len(files)
            
            processed = 0
            
            for root, dirs, files in os.walk(folder_path):
                if not include_subdirs and root != folder_path:
                    continue
                    
                for filename in files:
                    if not self.is_searching:  # Check if search was cancelled
                        return
                        
                    processed += 1
                    progress = (processed / total_files) * 100 if total_files > 0 else 0
                    self.progress_queue.put(('progress', progress, f"Scanning: {filename[:30]}..."))
                    
                    # Apply extension filter
                    if extensions:
                        file_ext = os.path.splitext(filename)[1].lower()
                        if not any(file_ext == ext.lower() for ext in extensions):
                            continue
                    
                    # Apply keyword filter
                    check_name = filename if case_sensitive else filename.lower()
                    
                    if search_keyword:
                        if search_mode == "include":
                            if search_keyword not in check_name:
                                continue
                        else:  # exclude mode
                            if search_keyword in check_name:
                                continue
                    
                    file_path = os.path.join(root, filename)
                    size, modified = self.get_file_info(file_path)
                    
                    found_files.append({
                        'name': filename,
                        'path': file_path,
                        'size': size,
                        'modified': modified,
                        'relative_path': os.path.relpath(file_path, folder_path)
                    })
            
            self.progress_queue.put(('complete', found_files))
            
        except Exception as e:
            self.progress_queue.put(('error', str(e)))
    
    def search_files(self):
        """Start file search in a separate thread"""
        if not self.selected_folder.get():
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
            
        if self.is_searching:
            # Cancel current search
            self.is_searching = False
            self.search_button.config(text="Search Files")
            self.progress_bar.stop()
            self.status_label.config(text="Search cancelled")
            return
        
        # Clear previous results
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        self.is_searching = True
        self.search_button.config(text="Cancel Search")
        self.progress_bar.start()
        self.status_label.config(text="Searching...")
        
        # Start search thread
        self.search_thread = threading.Thread(target=self.search_files_worker, daemon=True)
        self.search_thread.start()
        
        # Start checking for results
        self.check_search_progress()
    
    def check_search_progress(self):
        """Check search progress and update UI"""
        try:
            while True:
                try:
                    message = self.progress_queue.get_nowait()
                    msg_type = message[0]
                    
                    if msg_type == 'progress':
                        _, progress, status = message
                        self.status_label.config(text=status)
                        
                    elif msg_type == 'complete':
                        _, found_files = message
                        self.display_search_results(found_files)
                        self.is_searching = False
                        self.search_button.config(text="Search Files")
                        self.progress_bar.stop()
                        self.status_label.config(text=f"Found {len(found_files)} files")
                        return
                        
                    elif msg_type == 'error':
                        _, error_msg = message
                        messagebox.showerror("Search Error", f"Error during search: {error_msg}")
                        self.is_searching = False
                        self.search_button.config(text="Search Files")
                        self.progress_bar.stop()
                        self.status_label.config(text="Search failed")
                        return
                        
                except queue.Empty:
                    break
                    
        except:
            pass
            
        if self.is_searching:
            self.root.after(100, self.check_search_progress)
    
    def display_search_results(self, files):
        """Display search results in the treeview"""
        self.file_data = files
        
        for i, file_info in enumerate(files):
            size_str = self.format_file_size(file_info['size'])
            self.file_tree.insert('', 'end', iid=str(i), values=(
                file_info['name'],
                size_str,
                file_info['modified'],
                file_info['path']
            ))
    
    def select_all_files(self):
        """Select all files in the list"""
        children = self.file_tree.get_children()
        self.file_tree.selection_set(children)
    
    def deselect_all_files(self):
        """Deselect all files in the list"""
        self.file_tree.selection_remove(self.file_tree.selection())
    
    def preview_selected(self):
        """Show a preview of selected files"""
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No files selected.")
            return
        
        total_size = 0
        file_list = []
        
        for item_id in selected:
            file_info = self.file_data[int(item_id)]
            file_list.append(file_info['name'])
            total_size += file_info['size']
        
        preview_text = f"Selected {len(file_list)} files:\n\n"
        preview_text += "\n".join(file_list[:20])  # Show first 20 files
        if len(file_list) > 20:
            preview_text += f"\n... and {len(file_list) - 20} more files"
        preview_text += f"\n\nTotal size: {self.format_file_size(total_size)}"
        
        messagebox.showinfo("Selected Files Preview", preview_text)
    
    def delete_selected(self):
        """Delete selected files with confirmation"""
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No files selected.")
            return
        
        # Show confirmation with file count and total size
        total_size = sum(self.file_data[int(item_id)]['size'] for item_id in selected)
        size_str = self.format_file_size(total_size)
        
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected)} files?\n"
            f"Total size: {size_str}\n\n"
            f"This action cannot be undone!"
        )
        
        if not result:
            return
        
        # Delete files and update display
        deleted_count = 0
        failed_files = []
        
        # Sort in reverse order to maintain indices when deleting
        sorted_selection = sorted(selected, key=lambda x: int(x), reverse=True)
        
        for item_id in sorted_selection:
            file_info = self.file_data[int(item_id)]
            try:
                os.remove(file_info['path'])
                self.file_tree.delete(item_id)
                self.file_data.pop(int(item_id))
                deleted_count += 1
                
                # Update indices for remaining items
                for i in range(len(self.file_data)):
                    if i >= int(item_id):
                        old_iid = str(i + 1)
                        if self.file_tree.exists(old_iid):
                            values = self.file_tree.item(old_iid)['values']
                            self.file_tree.delete(old_iid)
                            self.file_tree.insert('', i, iid=str(i), values=values)
                            
            except Exception as e:
                failed_files.append(f"{file_info['name']}: {str(e)}")
        
        # Show results
        message = f"Successfully deleted {deleted_count} files."
        if failed_files:
            message += f"\n\nFailed to delete {len(failed_files)} files:\n" + "\n".join(failed_files[:5])
            if len(failed_files) > 5:
                message += f"\n... and {len(failed_files) - 5} more"
        
        messagebox.showinfo("Deletion Complete", message)
        self.status_label.config(text=f"Deleted {deleted_count} files")
    
    def open_file_location(self, event):
        """Open file location in explorer"""
        selection = self.file_tree.selection()
        if selection:
            file_info = self.file_data[int(selection[0])]
            folder_path = os.path.dirname(file_info['path'])
            os.startfile(folder_path)
    
    def calculate_file_hash(self, file_path):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def find_duplicates_worker(self):
        """Worker thread for finding duplicate files"""
        try:
            folder_path = self.selected_folder.get()
            if not folder_path:
                self.progress_queue.put(('dup_error', "No folder selected"))
                return
            
            # Dictionary to store file hashes
            hash_dict = defaultdict(list)
            total_files = 0
            processed = 0
            
            # Count total files
            for root, dirs, files in os.walk(folder_path):
                total_files += len(files)
            
            self.progress_queue.put(('dup_progress', 0, f"Scanning {total_files} files..."))
            
            # Process each file
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if not self.is_searching:
                        return
                    
                    file_path = os.path.join(root, filename)
                    processed += 1
                    progress = (processed / total_files) * 100 if total_files > 0 else 0
                    
                    self.progress_queue.put(('dup_progress', progress, f"Hashing: {filename[:30]}..."))
                    
                    # Calculate file hash
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        size, modified = self.get_file_info(file_path)
                        hash_dict[file_hash].append({
                            'path': file_path,
                            'name': filename,
                            'size': size,
                            'modified': modified
                        })
            
            # Find duplicate groups (more than one file with same hash)
            duplicate_groups = []
            for file_hash, files in hash_dict.items():
                if len(files) > 1:
                    duplicate_groups.append(files)
            
            self.progress_queue.put(('dup_complete', duplicate_groups))
            
        except Exception as e:
            self.progress_queue.put(('dup_error', str(e)))
    
    def find_duplicates(self):
        """Start duplicate finding process"""
        if not self.selected_folder.get():
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        
        if self.is_searching:
            self.is_searching = False
            self.find_duplicates_button.config(text="Find Duplicates")
            self.dup_progress_bar.stop()
            return
        
        # Clear previous results
        for item in self.dup_tree.get_children():
            self.dup_tree.delete(item)
        
        self.duplicate_groups = []
        self.is_searching = True
        self.find_duplicates_button.config(text="Cancel")
        self.dup_progress_bar.config(mode='determinate')
        
        # Start duplicate finding thread
        threading.Thread(target=self.find_duplicates_worker, daemon=True).start()
        
        # Start checking for results
        self.check_duplicate_progress()
    
    def check_duplicate_progress(self):
        """Check duplicate finding progress"""
        try:
            while True:
                try:
                    message = self.progress_queue.get_nowait()
                    msg_type = message[0]
                    
                    if msg_type == 'dup_progress':
                        _, progress, status = message
                        self.dup_progress_bar['value'] = progress
                        
                    elif msg_type == 'dup_complete':
                        _, duplicate_groups = message
                        self.display_duplicate_results(duplicate_groups)
                        self.is_searching = False
                        self.find_duplicates_button.config(text="Find Duplicates")
                        return
                        
                    elif msg_type == 'dup_error':
                        _, error_msg = message
                        messagebox.showerror("Duplicate Finding Error", f"Error: {error_msg}")
                        self.is_searching = False
                        self.find_duplicates_button.config(text="Find Duplicates")
                        return
                        
                except queue.Empty:
                    break
                    
        except:
            pass
            
        if self.is_searching:
            self.root.after(100, self.check_duplicate_progress)
    
    def display_duplicate_results(self, duplicate_groups):
        """Display duplicate results in the treeview"""
        self.duplicate_groups = duplicate_groups
        total_wasted_space = 0
        
        for i, group in enumerate(duplicate_groups):
            group_size = group[0]['size']
            wasted_space = group_size * (len(group) - 1)
            total_wasted_space += wasted_space
            
            # Insert group header
            group_id = f"group_{i}"
            self.dup_tree.insert('', 'end', iid=group_id, values=(
                f"Group {i+1}",
                len(group),
                self.format_file_size(group_size),
                self.format_file_size(wasted_space)
            ))
            
            # Insert individual files
            for j, file_info in enumerate(group):
                self.dup_tree.insert(group_id, 'end', iid=f"{group_id}_file_{j}", values=(
                    file_info['name'],
                    1,
                    self.format_file_size(file_info['size']),
                    file_info['path']
                ))
        
        # Update status
        messagebox.showinfo(
            "Duplicate Scan Complete", 
            f"Found {len(duplicate_groups)} duplicate groups\n"
            f"Total wasted space: {self.format_file_size(total_wasted_space)}"
        )
    
    def auto_select_duplicates(self, mode):
        """Auto-select duplicates based on mode (oldest/newest)"""
        selection = []
        
        for i, group in enumerate(self.duplicate_groups):
            if mode == 'oldest':
                # Keep oldest (first created), select others
                sorted_group = sorted(group, key=lambda x: os.path.getctime(x['path']))
                to_delete = sorted_group[1:]  # All except oldest
            else:  # newest
                # Keep newest (last created), select others
                sorted_group = sorted(group, key=lambda x: os.path.getctime(x['path']), reverse=True)
                to_delete = sorted_group[1:]  # All except newest
            
            for j, file_info in enumerate(group):
                if file_info in to_delete:
                    selection.append(f"group_{i}_file_{j}")
        
        self.dup_tree.selection_set(selection)
    
    def delete_selected_duplicates(self):
        """Delete selected duplicate files"""
        selected = self.dup_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "No files selected.")
            return
        
        # Filter to get only file items (not group headers)
        file_items = [item for item in selected if '_file_' in item]
        
        if not file_items:
            messagebox.showinfo("Info", "No individual files selected. Please select specific files, not group headers.")
            return
        
        # Get file paths
        files_to_delete = []
        total_size = 0
        
        for item_id in file_items:
            parts = item_id.split('_')
            group_idx = int(parts[1])
            file_idx = int(parts[3])
            
            file_info = self.duplicate_groups[group_idx][file_idx]
            files_to_delete.append(file_info)
            total_size += file_info['size']
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Duplicate Deletion",
            f"Delete {len(files_to_delete)} duplicate files?\n"
            f"Total size: {self.format_file_size(total_size)}\n\n"
            f"This will free up disk space but cannot be undone!"
        )
        
        if not result:
            return
        
        # Delete files
        deleted_count = 0
        failed_files = []
        
        for file_info in files_to_delete:
            try:
                os.remove(file_info['path'])
                deleted_count += 1
            except Exception as e:
                failed_files.append(f"{file_info['name']}: {str(e)}")
        
        # Refresh duplicate display
        self.find_duplicates()
        
        # Show results
        message = f"Successfully deleted {deleted_count} duplicate files."
        if failed_files:
            message += f"\n\nFailed to delete {len(failed_files)} files:\n" + "\n".join(failed_files[:3])
        
        messagebox.showinfo("Deletion Complete", message)
    
    def open_duplicate_location(self, event):
        """Open duplicate file location in explorer"""
        selection = self.dup_tree.selection()
        if selection and '_file_' in selection[0]:
            parts = selection[0].split('_')
            group_idx = int(parts[1])
            file_idx = int(parts[3])
            
            file_info = self.duplicate_groups[group_idx][file_idx]
            folder_path = os.path.dirname(file_info['path'])
            os.startfile(folder_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFileManagerApp(root)
    root.mainloop()

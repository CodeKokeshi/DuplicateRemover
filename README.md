# Advanced File Manager & Duplicate Remover

A comprehensive file management tool that combines file searching, filtering, and duplicate detection capabilities with a modern, user-friendly interface.

## ✨ Features

### 🔍 **Advanced File Search**
- **Flexible Search Modes**: Include or exclude files based on keywords
- **Case Sensitivity Control**: Choose case-sensitive or case-insensitive matching
- **Subdirectory Support**: Search within subdirectories or current folder only
- **File Extension Filtering**: Filter by specific file extensions (e.g., .txt, .pdf, .jpg)
- **Real-time Progress**: Multi-threaded searching with progress indication

### 📊 **Smart File Display**
- **Detailed File Information**: View file name, size, modification date, and full path
- **Sortable Columns**: Click column headers to sort results
- **Batch Selection**: Select all, deselect all, or multi-select files
- **File Preview**: Preview selected files before deletion
- **Quick Navigation**: Double-click to open file location in explorer

### 🔄 **Intelligent Duplicate Detection**
- **Hash-Based Detection**: Uses MD5 hashing for accurate duplicate identification
- **Grouped Results**: Duplicates organized in easy-to-understand groups
- **Smart Selection**: Auto-select oldest or newest files in each duplicate group
- **Space Analysis**: See exactly how much space you'll free up
- **Safe Deletion**: Preview and confirm before deleting duplicates

### 🎨 **Modern User Interface**
- **Tabbed Interface**: Separate tabs for file search and duplicate detection
- **Responsive Design**: Resizable windows with proper layout management
- **Progress Indicators**: Visual feedback for long-running operations
- **Keyboard Shortcuts**: 
  - `Ctrl+F`: Focus search field
  - `F5`: Start search
  - `Delete`: Delete selected files
  - `Enter`: Execute search from keyword field

### 🛡️ **Safety Features**
- **Confirmation Dialogs**: Always confirm before deleting files
- **Error Handling**: Graceful error handling with detailed error messages
- **Cancellable Operations**: Cancel long-running searches at any time
- **File Size Warnings**: See total size of files before deletion

## 🚀 How to Use

### File Search & Delete
1. **Select Folder**: Click "Browse" to choose the target folder
2. **Configure Search**: 
   - Enter search keyword
   - Choose include/exclude mode
   - Set case sensitivity and subdirectory options
   - Add file extension filters if needed
3. **Execute Search**: Click "Search Files" (or press F5)
4. **Review Results**: Browse the detailed file list
5. **Select Files**: Use mouse clicks or "Select All" button
6. **Preview**: Use "Preview Selected" to review your selection
7. **Delete**: Click "Delete Selected Files" and confirm

### Duplicate Detection
1. **Select Folder**: Ensure you have a folder selected
2. **Find Duplicates**: Switch to "Duplicate Finder" tab and click "Find Duplicates"
3. **Review Groups**: Examine duplicate groups with wasted space information
4. **Auto-Select**: Use "Keep Oldest" or "Keep Newest" for quick selection
5. **Manual Selection**: Or manually select specific files to delete
6. **Delete Duplicates**: Click "Delete Selected Duplicates" and confirm

## 🔧 Technical Details

### Multi-Threading
- Background file scanning doesn't freeze the UI
- Real-time progress updates
- Cancellable operations
- Thread-safe queue communication

### Performance
- Efficient file traversal using `os.walk()`
- Chunked file reading for hash calculation
- Memory-efficient duplicate detection
- Optimized UI updates

### File Safety
- Read-only folder display
- Comprehensive error handling
- Detailed deletion reports
- No accidental file modifications

## 📋 Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

### Included Modules
- `tkinter` - GUI framework
- `threading` - Multi-threading support  
- `queue` - Thread-safe communication
- `os` - File system operations
- `time` - Time formatting
- `hashlib` - File hashing for duplicate detection
- `collections` - Data structures for grouping

## ⚠️ Important Notes

- **Backup First**: Always backup important files before bulk deletion
- **Test Carefully**: Try the tool on a test folder first
- **No Recovery**: Deleted files cannot be recovered through this application
- **Permissions**: Ensure you have write permissions for target folders
- **Large Folders**: Very large folders may take time to process

## 🎯 Quality of Life Improvements

- **Persistent Window State**: Remembers window size and position
- **Smart Defaults**: Sensible default settings for most use cases
- **Intuitive Navigation**: Logical tab organization and clear labeling
- **Visual Feedback**: Progress bars, status messages, and file counts
- **Error Prevention**: Warnings and confirmations prevent accidents
- **Accessibility**: Keyboard shortcuts and clear visual hierarchy

## 🔄 Integration

This version combines and improves upon both the original "DuplicateDeleter" and "DuplicateRemoverReversed" applications, offering:

- All functionality from both original versions
- Significantly improved user interface
- Multi-threading for better performance
- Enhanced safety features
- Professional-grade duplicate detection
- Extensive quality of life improvements

---

**Written by CodeKokeshi** - *Enhanced December 2024*

*Exercise caution when deleting files. This tool is designed for experienced users who understand file management risks.*

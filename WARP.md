# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a collection of Python utility projects, each designed for specific file and system management tasks. The repository contains four distinct projects:

- **Project 1**: Text replacement utility for batch editing `.txt` files
- **Project 2**: Batch file renaming tool with backup functionality
- **Project 3**: SFTP file search and download utility
- **Project 4**: Minecraft server management tool with SSH/SFTP capabilities

## Project Structure

Each project is self-contained in its own directory with a main `app.py` file. Projects 3 and 4 are more complex applications that handle remote server operations using SSH/SFTP.

```
Python-Projects/
├── Project 1/          # Text replacement in .txt files
│   ├── app.py
│   └── test.txt
├── Project 2/          # Batch file renamer
│   └── app.py
├── Project 3/          # SFTP file downloader
│   ├── app.py
│   ├── appcopy.py
│   ├── SFTPDownloader.spec  # PyInstaller spec file
│   └── build/          # PyInstaller build artifacts
├── Project 4/          # Minecraft server manager
│   └── app.py
├── README.md
└── documentation.md
```

## Common Development Commands

### Running Individual Projects
```bash
# Project 1 - Text replacement utility
cd "Project 1" && python app.py

# Project 2 - Batch file renamer
cd "Project 2" && python app.py

# Project 3 - SFTP downloader
cd "Project 3" && python app.py

# Project 4 - Minecraft server manager
cd "Project 4" && python app.py
```

### Installing Dependencies
Projects 3 and 4 require external dependencies:
```bash
# For Project 3 and 4 (SFTP/SSH functionality)
pip install paramiko python-dotenv

# For Project 3 building with PyInstaller
pip install pyinstaller
```

### Building Executables (Project 3)
Project 3 includes PyInstaller configuration:
```bash
cd "Project 3"
pyinstaller SFTPDownloader.spec
```

## Architecture and Key Components

### Project 1 - Text Replacement Utility
- **Core Function**: `hasfiles()` - Handles file reading, text replacement, and writing
- **Pattern**: Interactive file selection from current directory
- **File Handling**: Focuses on `.txt` files with error handling for file operations

### Project 2 - Batch File Renamer
- **Core Functions**: 
  - `createbackup()` - Creates backup directories before renaming
  - `batchrename()` - Performs sequential renaming with index numbers
- **Pattern**: Safety-first approach with backup creation before destructive operations
- **Path Handling**: Uses `pathlib.Path` for modern file system operations

### Project 3 - SFTP File Downloader
- **Architecture**: Modular design with separate concerns for connection, search, and download
- **Key Components**:
  - `sftpconnect()` - Establishes secure SFTP connections using credentials from `.env`
  - `searchfile()` - Recursive directory traversal and file matching
  - `createdownloadfolder()` - Local file management
- **Configuration**: Environment-based credentials with `.env` file auto-creation
- **PyInstaller Ready**: Includes proper path resolution for bundled executables

### Project 4 - Minecraft Server Manager
- **Architecture**: Menu-driven SSH administration tool
- **Key Components**:
  - `menu()` - Multi-page navigation system using pattern matching
  - `sshconnect()` and `sshconnect_interactive()` - Different connection modes
  - `createuserserver()` - Remote user management with sudo operations
  - `updateserver()` - System administration commands
- **Pattern**: Interactive CLI with real-time command output streaming
- **Security**: Separate credential handling for different privilege levels

## Environment Configuration

### For Projects 3 & 4 (.env file)
```
SFTP_HOST=your-server-hostname
SFTP_USER=your-username
SFTP_PASS=your-password
SFTP_PORT=22
```

Both applications will prompt to create this file if it doesn't exist.

## Testing and Debugging

### Running Individual Components
```bash
# Test SFTP connection (Project 3)
cd "Project 3" && python -c "from app import sftpconnect; sftpconnect()"

# Test SSH connection (Project 4) 
cd "Project 4" && python -c "from app import sshconnect; sshconnect()"
```

### Common Issues
- **Permission Errors**: Projects 1 & 2 require write permissions in target directories
- **Connection Timeouts**: Projects 3 & 4 may need network troubleshooting
- **Missing Dependencies**: Install `paramiko` and `python-dotenv` for SFTP/SSH projects

## Git Workflow
Based on documentation.md, the standard git workflow is:
```bash
git pull origin main --allow-unrelated-histories
git add .
git commit -m "descriptive message"
git push -u origin main
```

## Security Considerations
- Projects 3 & 4 handle SSH credentials - ensure `.env` files are not committed
- Project 4 requires root/sudo access for server management operations
- All credential prompts are handled interactively for security
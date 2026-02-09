# Minecraft Guerra 2 Installer

A modern, wizard-based installer for the Minecraft Guerra 2 modpack, featuring a clean GUI and automated launcher configuration.

## Overview

This installer streamlines the process of setting up the Minecraft Guerra 2 modpack across multiple launchers. What started as a simple utility quickly evolved into a full-featured installation wizard with smart update capabilities, profile automation, and support for both official and alternative Minecraft launchers.

The tool handles the entire installation workflow—from downloading the modpack to configuring launcher profiles—while preserving user data during updates.

## Why This Project Exists

Installing Minecraft modpacks can be tedious, especially when managing multiple versions or launchers. This installer was built to:

- **Eliminate manual configuration**: Automatically set up launcher profiles without editing JSON or SQLite databases manually
- **Support diverse environments**: Work with both official (Modrinth, CurseForge) and alternative (TLauncher, SKLauncher) launchers
- **Enable smart updates**: Update mods and configs while preserving saves, screenshots, and user settings
- **Provide flexibility**: Offer three modpack variants (Full, Intermediate, Lightweight) to accommodate different hardware capabilities

## Tech Stack

- **Python 3.8+** - Core application logic
- **CustomTkinter** - Modern, themed UI framework with dark/light mode support
- **Requests** - HTTP client for downloading modpack files
- **Pillow** - Image processing for UI assets
- **Standard Library**:
  - `tkinter` - Base GUI framework
  - `zipfile` - Archive extraction
  - `sqlite3` - Modrinth database manipulation
  - `json` - SKLauncher profile configuration
  - `threading` - Non-blocking installation process

## Features

- **5-Step Wizard Interface**: Intuitive flow from welcome screen to installation completion
- **Multi-Launcher Support**:
  - Official: Modrinth App, CurseForge
  - Alternative: TLauncher, SKLauncher
  - Manual: Custom directory installation
- **Three Modpack Variants**:
  - Full (~550MB): Complete experience with all mods
  - Intermediate (~300MB): Balanced for most PCs
  - Lightweight (~150MB): Optimized for lower-end hardware
- **Smart Update System**: Replaces mods and configs while preserving user data
- **Automated Profile Configuration**: Generates launcher profiles programmatically
- **Visual Progress Tracking**: Step indicators with completion states
- **Process Management**: Automatically closes conflicting launcher and game processes

## Architecture

The installer follows a wizard pattern with five distinct screens:

1. **Welcome Screen**: Introduction and overview
2. **License Type Selection**: Choose between official or alternative launchers
3. **Launcher Selection**: Pick specific launcher based on license type
4. **Version Selection**: Choose modpack variant
5. **Installation**: Download, extract, and configure

### Key Components

- **ModpackWizard Class**: Main application controller managing UI state and navigation
- **Threading Model**: Installation runs on a separate thread to keep UI responsive
- **Target Directory Resolution**: Determines installation paths based on launcher type and system environment
- **Profile Configurators**:
  - `configure_sklauncher_profile()`: Manipulates JSON configuration files
  - `configure_modrinth_profile()`: Writes to SQLite database
- **Update Logic**: Selective file replacement preserving `saves/`, `screenshots/`, `options.txt`, and `servers.dat`

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows 10/11
- Active internet connection

### Installation

1. Clone the repository:
```bash
git clone https://github.com/BLMChoosen/Minecraft-Guerra-Installer.git
cd Minecraft-Guerra-Installer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the installer:
```bash
python Installer.py
```

### Building an Executable

For distribution as a standalone executable:

```bash
pip install pyinstaller
python -m PyInstaller --noconsole --onefile --clean \
  --add-data "PATH_TO_PYTHON\Lib\site-packages\customtkinter;customtkinter" \
  Installer.py
```

The compiled executable will be in the `dist/` directory.

## Example Usage

1. Launch the installer with `python Installer.py`
2. Select your license type (official or alternative)
3. Choose your launcher (e.g., Modrinth App)
4. Select modpack variant (e.g., Intermediate)
5. Wait for download and automatic configuration
6. Launch your chosen launcher and select the "Minecraft Guerra 2" profile

The installer creates isolated instances per version, allowing multiple variants to coexist on the same launcher.

## Engineering Highlights

### Smart Update System

The update mechanism intelligently replaces only essential modpack files while preserving user data:

- Replaces: `mods/`, `config/`, `resourcepacks/`
- Preserves: `saves/`, `screenshots/`, `options.txt`, `servers.dat`

This approach prevents data loss during updates, a common pain point in modpack management.

### Cross-Launcher Profile Automation

Different launchers use different configuration formats. This installer handles both:

- **SKLauncher**: JSON file manipulation in `%APPDATA%\.minecraft\skmedix`
- **Modrinth**: SQLite database operations in `%APPDATA%\com.modrinth.theseus\profiles`

Both configurators generate profiles with proper Forge loader settings, memory allocation, and game directory paths.

### Responsive UI Without Blocking

Installation operations run on background threads while the main thread handles UI updates via `after()` callbacks, preventing the interface from freezing during downloads or extraction.

## What I Learned

This project deepened my understanding of:

- **GUI Development**: Building polished user interfaces with CustomTkinter's theming system
- **Cross-Platform Path Handling**: Working with Windows-specific paths and environment variables
- **Data Persistence**: Manipulating different config formats (JSON, SQLite) programmatically
- **Threading in GUI Applications**: Implementing non-blocking operations while maintaining UI responsiveness
- **Software Distribution**: Packaging Python applications as executables with PyInstaller
- **User Experience Design**: Creating intuitive installation workflows with clear visual feedback

## Future Improvements

- Linux and macOS support
- Automatic modpack version detection and update notifications
- Rollback functionality for failed installations
- Telemetry to track which versions and launchers are most popular
- Custom theme/color scheme support
- Multi-language localization support (Portuguese, Spanish, etc.)

---

**Developed by BLMChoosen | 2025**

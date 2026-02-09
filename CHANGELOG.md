# Changelog

All notable changes to DeMoD Nixpkgs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-09

### Added
- 🎨 Beautiful, modern TUI with custom theming
- 🔍 Real-time package search via NixOS API
- 📦 One-click package installation
- 🗂️ Category-based package management (Development, Productivity, Media, Utilities, Custom)
- 🏗️ Two-flake architecture (System flake + Managed packages flake)
- ⌨️ Comprehensive keyboard shortcuts
- 📋 Rich package details view with enhanced formatting
- 🔖 Flake snippet generation
- 💻 NixOS and Home Manager integration modules
- 🎯 Status bar showing connection and search statistics
- 📱 Responsive UI with tabs and scrolling
- 🎨 Emoji-enhanced category selection
- 🔄 Automatic managed packages flake initialization
- 📊 Color-coded interface with cyan/green accent theme

### Features
- **Search**: Lightning-fast package discovery
- **Install**: Direct installation via `nix profile install`
- **Manage**: Add packages to organized categories
- **Details**: View comprehensive package information
- **Export**: Generate flake.nix snippets
- **Clipboard**: Auto-copy support (xclip/wl-clipboard)

### Developer Features
- Development shell with all dependencies
- Makefile with common tasks
- Support for both flakes and legacy nix-shell
- Template system for managed packages
- Automatic directory structure initialization

### Documentation
- Comprehensive README with examples
- Architecture documentation
- Complete integration examples
- Managed packages guide
- Quick start guide

### Design
- Custom branded header
- Color-coded buttons and UI elements
- Enhanced table display with alternating rows
- Professional status bar
- Rich text formatting for package details
- Emoji-enhanced notifications

## Copyright

Copyright (c) 2026 DeMoD LLC

Licensed under MIT License

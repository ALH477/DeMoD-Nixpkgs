# DeMoD Nixpkgs

**Beautiful Package Management for Nix**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Nix Flakes](https://img.shields.io/badge/Nix-Flakes-blue.svg)](https://nixos.wiki/wiki/Flakes)
[![Made by DeMoD LLC](https://img.shields.io/badge/Made%20by-DeMoD%20LLC-00d4ff.svg)](https://demod.ltd)

A modern, elegant Terminal User Interface (TUI) for discovering, managing, and installing Nix packages with real-time search powered by the official NixOS API.

```
╔══════════════════════════════════════════════════════════════╗
║  DeMoD Nixpkgs  │  Beautiful Package Management for Nix      ║
╚══════════════════════════════════════════════════════════════╝
```

##  Features

-  **Lightning-Fast Search** - Real-time package discovery via NixOS API
-  **Beautiful Interface** - Carefully designed TUI with custom theming
-  **One-Click Install** - Install packages directly from the interface
-  **Smart Management** - Organize packages by category in a separate flake
-  **Flake Integration** - Generate snippets for your Nix configurations
-  **Keyboard First** - Efficient navigation with intuitive shortcuts
-  **Rich Details** - View descriptions, versions, licenses, and homepage links
-  **Two-Flake Architecture** - Clean separation of tool and package data

##  Preview

```
┌─ Package Information ─────────────────────────────────────┐

Package:     python3
Version:     3.11.6

Description:
  A high-level dynamically-typed programming language

Programs:    python, python3, pip, idle
License:     Python Software Foundation License
Platforms:   All platforms
Homepage:    https://www.python.org

┌─ Installation ────────────────────────────────────────────┐

Direct Install:
  $ nix profile install nixpkgs#python3

Flake Usage:
  environment.systemPackages = [ pkgs.python3 ];

Shell Environment:
  $ nix shell nixpkgs#python3
```

##  Quick Start

### Run Instantly (No Installation)

```bash
nix run github:demod-llc/nixpkgs
```

### Install Globally

```bash
nix profile install github:demod-llc/nixpkgs
demod-nixpkgs
```

### From Source

```bash
git clone https://github.com/demod-llc/nixpkgs.git
cd nixpkgs
nix run
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `S` | Focus search input |
| `I` | Install selected package |
| `A` | Add to managed packages |
| `R` | Refresh current search |
| `Q` | Quit application |
| `?` | Show help |
| `↑` `↓` | Navigate results |
| `Enter` | View package details |
| `Tab` | Switch between tabs |

##  Architecture

DeMoD Nixpkgs uses a **two-flake system** for clean separation:

### System Flake (The Tool)
- **Location**: This repository
- **Contains**: The TUI application and its dependencies
- **Purpose**: Provides the package management interface
- **Updates**: Tool improvements and features

### Managed Flake (Your Packages)  
- **Location**: `~/.demod-nixpkgs/managed-packages/`
- **Contains**: Your declarative package selections
- **Purpose**: Organized package collections by category
- **Updates**: Your package choices via the TUI

This design means updates to the tool never affect your package selections.

##  Managing Packages

### Add Packages via TUI

1. Search for a package (e.g., "python")
2. Select it from results
3. Choose a category:
   -  Development
   -  Productivity
   -  Media
   -  Utilities
   -  Custom
4. Press `A` or click "Add to Managed"

The package is automatically added to `~/.demod-nixpkgs/managed-packages/packages.nix`

### Install Your Managed Packages

```bash
# Install all categories
nix profile install ~/.demod-nixpkgs/managed-packages#all

# Install specific category
nix profile install ~/.demod-nixpkgs/managed-packages#development
```

### NixOS Integration

Add to your `/etc/nixos/flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    demod-nixpkgs.url = "github:demod-llc/nixpkgs";
    managed-packages.url = "path:/home/user/.demod-nixpkgs/managed-packages";
  };

  outputs = { nixpkgs, demod-nixpkgs, managed-packages, ... }: {
    nixosConfigurations.mypc = nixpkgs.lib.nixosSystem {
      modules = [
        demod-nixpkgs.nixosModules.default
        managed-packages.nixosModules.default
        {
          # Enable the tool
          programs.demod-nixpkgs.enable = true;
          
          # Enable your managed packages
          demod-nixpkgs.managed-packages = {
            enable = true;
            categories = [ "all" ];  # or [ "development" "utilities" ]
          };
        }
      ];
    };
  };
}
```

### Home Manager Integration

```nix
{
  inputs.managed-packages.url = "path:/home/user/.demod-nixpkgs/managed-packages";
  
  # In your home configuration:
  demod-nixpkgs.managed-packages = {
    enable = true;
    categories = [ "all" ];
  };
}
```

## Development

### Enter Development Shell

```bash
nix develop
```

### Run from Source

```bash
python demod_nixpkgs.py
```

### Build Package

```bash
nix build
```

##  Documentation

- [**ARCHITECTURE.md**](ARCHITECTURE.md) - Detailed architecture explanation
- [**COMPLETE-EXAMPLE.md**](COMPLETE-EXAMPLE.md) - Full integration examples
- [**managed-packages/README.md**](managed-packages/README.md) - Managed packages guide
- [**QUICKSTART.md**](QUICKSTART.md) - Getting started guide

##  Use Cases

### For Developers
- Quickly discover and try new development tools
- Maintain reproducible dev environments
- Share team package configurations

### For DSP Engineers
Create custom DSP toolchain:
```nix
custom = with pkgs; [
  ardour      # DAW
  lmms        # Music production
  jack2       # Audio server
  qjackctl    # Jack control
  carla       # Plugin host
];
```

### For System Administrators
- Declaratively manage server packages
- Version control package selections
- Deploy consistent environments

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

```bash
git clone https://github.com/demod-llc/nixpkgs.git
cd nixpkgs
nix develop
# Make your changes
python demod_nixpkgs.py
```

##  License

MIT License - Copyright (c) 2026 DeMoD LLC

See [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual) TUI framework
- Powered by [NixOS Package Search API](https://search.nixos.org/)
- Inspired by the Nix community's commitment to declarative systems

##  Support

- **Issues**: [GitHub Issues](https://github.com/ALH477/nixpkgs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ALH477/nixpkgs/discussions)
- **NixOS Community**: [discourse.nixos.org](https://discourse.nixos.org/)

---

<div align="center">

**Made with poop by [DeMoD LLC](https://demod.llc)**

*Beautiful Package Management for Nix*

</div>

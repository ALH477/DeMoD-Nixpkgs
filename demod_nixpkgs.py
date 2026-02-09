#!/usr/bin/env python3
"""
DeMoD Nixpkgs - A Beautiful Terminal Interface for Nix Package Management
Copyright (c) 2026 DeMoD LLC
Licensed under MIT License

Searches and manages packages using the NixOS search API
"""

import asyncio
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import httpx
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TabbedContent,
    TabPane,
    Select,
)
from textual.binding import Binding
from textual.reactive import reactive


# Configuration
MANAGED_FLAKE_DIR = Path.home() / ".demod-nixpkgs" / "managed-packages"
MANAGED_PACKAGES_FILE = MANAGED_FLAKE_DIR / "packages.nix"

# Branding
APP_NAME = "DeMoD Nixpkgs"
APP_VERSION = "1.0.0"
APP_TAGLINE = "Beautiful Package Management for Nix"


class BrandedHeader(Static):
    """Custom branded header with logo"""

    def compose(self) -> ComposeResult:
        yield Static(f"""[bold #00d4ff]╔══════════════════════════════════════════════════════════════╗
║  [bold white]DeMoD[/bold white] [#00d4ff]Nixpkgs[/#00d4ff]  │  {APP_TAGLINE}           ║
╚══════════════════════════════════════════════════════════════╝[/bold #00d4ff]""", id="app-header")


class PackageDetails(Static):
    """Widget to display detailed package information with enhanced styling"""

    def update_package(self, package: dict) -> None:
        """Update the displayed package details"""
        name = package.get("package_attr_name", "N/A")
        version = package.get("package_pversion", "N/A")
        description = package.get("package_description", "No description available")
        programs = package.get("package_programs", [])
        homepage = package.get("package_homepage", ["N/A"])
        license_info = package.get("package_license", [{"fullName": "N/A"}])
        platforms = package.get("package_platforms", [])

        programs_str = ", ".join(programs[:5]) if programs else "None"
        if len(programs) > 5:
            programs_str += f" (+{len(programs) - 5} more)"

        license_names = [lic.get("fullName", "Unknown") for lic in license_info]
        license_str = ", ".join(license_names[:3]) if license_names else "N/A"
        if len(license_names) > 3:
            license_str += f" (+{len(license_names) - 3} more)"

        platforms_str = ", ".join(platforms[:5]) if platforms else "All platforms"
        if len(platforms) > 5:
            platforms_str += f" (+{len(platforms) - 5} more)"

        homepage_str = homepage[0] if isinstance(homepage, list) and homepage else str(homepage)

        # Enhanced details with better formatting
        details = f"""[bold #00d4ff]┌─ Package Information ─────────────────────────────────────┐[/bold #00d4ff]

[bold #00d4ff]Package:[/bold #00d4ff]     [bold white]{name}[/bold white]
[bold #00d4ff]Version:[/bold #00d4ff]     [#88ff88]{version}[/#88ff88]

[bold #00d4ff]Description:[/bold #00d4ff]
  [dim]{description}[/dim]

[bold #00d4ff]Programs:[/bold #00d4ff]    {programs_str}
[bold #00d4ff]License:[/bold #00d4ff]     {license_str}
[bold #00d4ff]Platforms:[/bold #00d4ff]   {platforms_str}
[bold #00d4ff]Homepage:[/bold #00d4ff]    [link={homepage_str}]{homepage_str}[/link]

[bold #00d4ff]┌─ Installation ────────────────────────────────────────────┐[/bold #00d4ff]

[bold #ffaa00]Direct Install:[/bold #ffaa00]
  [dim]$[/dim] nix profile install nixpkgs#{name}

[bold #ffaa00]Flake Usage:[/bold #ffaa00]
  environment.systemPackages = [ pkgs.{name.split('.')[-1]} ];

[bold #ffaa00]Shell Environment:[/bold #ffaa00]
  [dim]$[/dim] nix shell nixpkgs#{name}

[bold #00d4ff]└───────────────────────────────────────────────────────────┘[/bold #00d4ff]
"""
        self.update(details)


class StatusBar(Static):
    """Custom status bar showing connection and stats"""
    
    package_count = reactive(0)
    search_query = reactive("")
    
    def watch_package_count(self, count: int) -> None:
        self.update_status()
    
    def watch_search_query(self, query: str) -> None:
        self.update_status()
    
    def update_status(self) -> None:
        status = f"[#00d4ff]●[/#00d4ff] Connected to NixOS API"
        if self.search_query:
            status += f"  │  [dim]Query:[/dim] [bold]{self.search_query}[/bold]"
        if self.package_count > 0:
            status += f"  │  [dim]Results:[/dim] [bold #88ff88]{self.package_count}[/bold #88ff88]"
        
        managed_path = f"[dim]{MANAGED_FLAKE_DIR.relative_to(Path.home())}[/dim]"
        status += f"  │  [dim]Managed:[/dim] ~/{managed_path}"
        
        self.update(status)


class DeMoDNixpkgs(App):
    """DeMoD Nixpkgs - Beautiful TUI for browsing and managing Nix packages"""

    CSS = """
    Screen {
        background: $surface;
    }

    #app-header {
        height: auto;
        padding: 0 1;
        background: $boost;
        color: #00d4ff;
        text-align: center;
    }

    #search-container {
        height: auto;
        padding: 1;
        background: $panel;
        border: tall $primary;
    }

    #search-input {
        width: 100%;
        border: tall #00d4ff;
    }

    #search-input:focus {
        border: tall #00ff88;
    }

    #results-table {
        height: 1fr;
        border: solid #00d4ff;
    }

    #details-pane {
        height: 100%;
        padding: 1;
        background: $panel;
        overflow-y: auto;
        border: solid #00d4ff;
    }

    .button-container {
        height: auto;
        padding: 1;
        background: $panel;
        border-top: solid #00d4ff;
    }

    Button {
        margin-right: 1;
        min-width: 16;
    }
    
    Button.-primary {
        background: #00d4ff;
        color: #000000;
        border: none;
    }
    
    Button.-primary:hover {
        background: #00ff88;
    }
    
    Button.-success {
        background: #00ff88;
        color: #000000;
        border: none;
    }
    
    Button.-success:hover {
        background: #88ff88;
    }
    
    Button:hover {
        background: #00d4ff;
        color: #000000;
    }
    
    Select {
        width: 24;
        margin-right: 1;
        border: solid #00d4ff;
    }
    
    Select:focus {
        border: solid #00ff88;
    }
    
    DataTable {
        background: $surface;
        color: #ffffff;
    }
    
    DataTable > .datatable--cursor {
        background: #00d4ff 20%;
    }
    
    DataTable > .datatable--header {
        background: #00d4ff;
        color: #000000;
        text-style: bold;
    }
    
    DataTable > .datatable--odd-row {
        background: $surface;
    }
    
    DataTable > .datatable--even-row {
        background: $panel;
    }
    
    #status-bar {
        height: 1;
        background: $panel;
        padding: 0 1;
        border-top: solid #00d4ff;
    }
    
    TabbedContent {
        height: 1fr;
    }
    
    TabPane {
        padding: 0;
    }
    
    Tabs {
        background: $panel;
    }
    
    Tab {
        background: $surface;
        color: #00d4ff;
    }
    
    Tab.-active {
        background: #00d4ff;
        color: #000000;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, key_display="Q"),
        Binding("s", "focus_search", "Search", show=True, key_display="S"),
        Binding("i", "install_package", "Install", show=True, key_display="I"),
        Binding("a", "add_to_managed", "Add to Managed", show=True, key_display="A"),
        Binding("r", "refresh", "Refresh", show=True, key_display="R"),
        Binding("?", "show_help", "Help", show=False, key_display="?"),
    ]

    def __init__(self):
        super().__init__()
        self.current_packages = []
        self.selected_package = None
        self.ensure_managed_flake_exists()

    def ensure_managed_flake_exists(self) -> None:
        """Ensure the managed packages flake directory and files exist"""
        MANAGED_FLAKE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy template files if they don't exist
        template_dir = Path(__file__).parent / "managed-packages"
        
        if not MANAGED_PACKAGES_FILE.exists():
            # Create default packages.nix
            MANAGED_PACKAGES_FILE.write_text("""# Managed by DeMoD Nixpkgs
# Copyright (c) 2026 DeMoD LLC
{ pkgs }:

{
  development = with pkgs; [
    # Development tools - compilers, languages, version control
  ];

  productivity = with pkgs; [
    # Productivity applications - browsers, editors, office suites
  ];

  media = with pkgs; [
    # Media applications - audio, video, graphics
  ];

  utilities = with pkgs; [
    # System utilities - terminal tools, system monitors
  ];

  custom = with pkgs; [
    # Custom packages - anything that doesn't fit above
  ];
}
""")
        
        # Copy flake.nix if it doesn't exist
        flake_file = MANAGED_FLAKE_DIR / "flake.nix"
        if not flake_file.exists():
            if template_dir.exists() and (template_dir / "flake.nix").exists():
                import shutil
                shutil.copy(template_dir / "flake.nix", flake_file)
            else:
                # Create minimal flake
                flake_file.write_text("""{
  description = "DeMoD Nixpkgs - User-managed package collection";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.\${system};
          packageSets = import ./packages.nix { inherit pkgs; };
        in {
          development = pkgs.buildEnv {
            name = "development-packages";
            paths = packageSets.development;
          };
          productivity = pkgs.buildEnv {
            name = "productivity-packages";
            paths = packageSets.productivity;
          };
          media = pkgs.buildEnv {
            name = "media-packages";
            paths = packageSets.media;
          };
          utilities = pkgs.buildEnv {
            name = "utility-packages";
            paths = packageSets.utilities;
          };
          custom = pkgs.buildEnv {
            name = "custom-packages";
            paths = packageSets.custom;
          };
          all = pkgs.buildEnv {
            name = "all-managed-packages";
            paths = packageSets.development
                 ++ packageSets.productivity
                 ++ packageSets.media
                 ++ packageSets.utilities
                 ++ packageSets.custom;
          };
        }
      );
    };
}
""")

    def add_package_to_managed(self, package_name: str, category: str = "custom") -> bool:
        """Add a package to the managed packages.nix file"""
        try:
            content = MANAGED_PACKAGES_FILE.read_text()
            
            # Find the category section
            category_pattern = rf"({category}\s*=\s*with pkgs;\s*\[)(.*?)(\];)"
            match = re.search(category_pattern, content, re.DOTALL)
            
            if not match:
                return False
            
            # Check if package already exists in this category
            packages_section = match.group(2)
            if package_name in packages_section:
                return False  # Already exists
            
            # Add the package (uncommented)
            new_packages = packages_section.rstrip() + f"\n    {package_name}"
            new_content = content[:match.start(2)] + new_packages + content[match.end(2):]
            
            MANAGED_PACKAGES_FILE.write_text(new_content)
            return True
            
        except Exception as e:
            self.notify(f"Error adding to managed packages: {str(e)}", severity="error", timeout=10)
            return False

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield BrandedHeader()

        with Container(id="search-container"):
            yield Input(
                placeholder="🔍 Search packages (e.g., python, firefox, git, rust)...",
                id="search-input",
            )

        with TabbedContent():
            with TabPane("📦 Search Results", id="search-tab"):
                yield DataTable(id="results-table", zebra_stripes=True)

            with TabPane("📋 Package Details", id="details-tab"):
                with VerticalScroll():
                    yield PackageDetails(id="details-pane")

        with Horizontal(classes="button-container"):
            yield Button("⚡ Install Now", id="install-btn", variant="primary")
            yield Button("➕ Add to Managed", id="managed-btn", variant="success")
            yield Select(
                [
                    ("💻 Development", "development"),
                    ("📊 Productivity", "productivity"),
                    ("🎨 Media", "media"),
                    ("🔧 Utilities", "utilities"),
                    ("⭐ Custom", "custom"),
                ],
                value="custom",
                id="category-select",
                allow_blank=False,
            )
            yield Button("📄 Copy Flake", id="flake-btn")
            yield Button("🗑️  Clear", id="clear-btn")

        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the data table when the app starts"""
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Package", "Version", "Description")
        table.cursor_type = "row"

        # Focus the search input
        self.query_one("#search-input", Input).focus()
        
        # Update status bar
        status = self.query_one("#status-bar", StatusBar)
        status.update_status()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search when Enter is pressed"""
        if event.input.id == "search-input":
            await self.search_packages(event.value)

    async def search_packages(self, query: str) -> None:
        """Search for packages using the NixOS search API"""
        if not query.strip():
            return

        table = self.query_one("#results-table", DataTable)
        table.clear()
        self.current_packages = []

        # Update status bar
        status = self.query_one("#status-bar", StatusBar)
        status.search_query = query

        # Show loading notification
        self.notify(f"🔍 Searching for '{query}'...", timeout=2)

        try:
            async with httpx.AsyncClient() as client:
                url = "https://search.nixos.org/backend/latest-42-nixos-unstable/_search"
                
                # Construct the search query for NixOS API
                search_body = {
                    "from": 0,
                    "size": 50,
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": [
                                            "package_attr_name^3",
                                            "package_programs^2",
                                            "package_pname^2",
                                            "package_description",
                                        ],
                                    }
                                }
                            ],
                            "filter": [{"term": {"type": {"value": "package"}}}],
                        }
                    },
                    "sort": [{"_score": "desc"}, {"package_attr_name": "asc"}],
                }

                response = await client.post(url, json=search_body, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                hits = data.get("hits", {}).get("hits", [])
                self.current_packages = [hit["_source"] for hit in hits]

                if not self.current_packages:
                    self.notify("❌ No packages found", severity="warning", timeout=3)
                    status.package_count = 0
                    return

                # Populate the table
                for pkg in self.current_packages:
                    name = pkg.get("package_attr_name", "N/A")
                    version = pkg.get("package_pversion", "N/A")
                    description = pkg.get("package_description", "")
                    # Truncate long descriptions
                    if len(description) > 60:
                        description = description[:57] + "..."

                    table.add_row(name, version, description)

                status.package_count = len(self.current_packages)
                self.notify(
                    f"✅ Found {len(self.current_packages)} packages",
                    severity="information",
                    timeout=3
                )

        except httpx.HTTPError as e:
            self.notify(f"❌ Search failed: {str(e)}", severity="error", timeout=5)
            status.package_count = 0
        except Exception as e:
            self.notify(f"❌ Error: {str(e)}", severity="error", timeout=5)
            status.package_count = 0

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in the results table"""
        if event.row_key.value is not None:
            row_index = event.row_key.value
            if 0 <= row_index < len(self.current_packages):
                self.selected_package = self.current_packages[row_index]
                
                # Update the details pane
                details_pane = self.query_one("#details-pane", PackageDetails)
                details_pane.update_package(self.selected_package)
                
                # Switch to details tab
                tabs = self.query_one(TabbedContent)
                tabs.active = "details-tab"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "install-btn":
            await self.action_install_package()
        elif event.button.id == "managed-btn":
            await self.action_add_to_managed()
        elif event.button.id == "flake-btn":
            await self.add_to_flake()
        elif event.button.id == "clear-btn":
            self.query_one("#search-input", Input).value = ""
            table = self.query_one("#results-table", DataTable)
            table.clear()
            self.current_packages = []
            status = self.query_one("#status-bar", StatusBar)
            status.search_query = ""
            status.package_count = 0

    async def action_add_to_managed(self) -> None:
        """Add the selected package to managed packages"""
        if not self.selected_package:
            self.notify("⚠️  Please select a package first", severity="warning", timeout=3)
            return

        name = self.selected_package.get("package_attr_name", "")
        pkg_name = name.split(".")[-1]  # Get the last part for pkgs.X
        
        # Get selected category
        category_select = self.query_one("#category-select", Select)
        category = str(category_select.value)
        
        # Category emoji mapping
        category_emoji = {
            "development": "💻",
            "productivity": "📊",
            "media": "🎨",
            "utilities": "🔧",
            "custom": "⭐"
        }
        emoji = category_emoji.get(category, "📦")
        
        # Add to managed packages
        if self.add_package_to_managed(pkg_name, category):
            self.notify(
                f"✅ Added {pkg_name} to {emoji} {category}\n"
                f"📁 Location: ~/{MANAGED_FLAKE_DIR.relative_to(Path.home())}",
                severity="information",
                timeout=5
            )
        else:
            self.notify(
                f"ℹ️  Package {pkg_name} already exists in {category}",
                severity="warning",
                timeout=3
            )

    async def action_install_package(self) -> None:
        """Install the selected package"""
        if not self.selected_package:
            self.notify("⚠️  Please select a package first", severity="warning", timeout=3)
            return

        name = self.selected_package.get("package_attr_name", "")
        self.notify(f"⚡ Installing {name}...", timeout=3)

        try:
            # Run nix profile install
            process = await asyncio.create_subprocess_exec(
                "nix", "profile", "install", f"nixpkgs#{name}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                self.notify(
                    f"✅ Successfully installed {name}!",
                    severity="information",
                    timeout=5
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                self.notify(
                    f"❌ Installation failed:\n{error_msg[:200]}",
                    severity="error",
                    timeout=10
                )

        except FileNotFoundError:
            self.notify(
                "❌ Nix not found. Please ensure Nix is installed.",
                severity="error",
                timeout=5
            )
        except Exception as e:
            self.notify(f"❌ Error: {str(e)}", severity="error", timeout=5)

    async def add_to_flake(self) -> None:
        """Add package to a flake.nix file"""
        if not self.selected_package:
            self.notify("⚠️  Please select a package first", severity="warning", timeout=3)
            return

        name = self.selected_package.get("package_attr_name", "")
        pkg_name = name.split(".")[-1]  # Get the last part for pkgs.X

        flake_entry = f'    pkgs.{pkg_name}  # {self.selected_package.get("package_description", "")[:50]}'
        
        # Try to copy to clipboard if xclip or wl-copy is available
        clipboard_success = False
        try:
            # Try xclip first (X11)
            process = await asyncio.create_subprocess_exec(
                "xclip", "-selection", "clipboard",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await process.communicate(flake_entry.encode())
            clipboard_success = True
        except FileNotFoundError:
            try:
                # Try wl-copy (Wayland)
                process = await asyncio.create_subprocess_exec(
                    "wl-copy",
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await process.communicate(flake_entry.encode())
                clipboard_success = True
            except FileNotFoundError:
                pass
        
        if clipboard_success:
            self.notify(
                f"✅ Copied to clipboard:\n{flake_entry}",
                severity="information",
                timeout=5
            )
        else:
            self.notify(
                f"📋 Flake entry:\n{flake_entry}\n\n"
                f"ℹ️  Install xclip or wl-clipboard for auto-copy",
                severity="information",
                timeout=8
            )

    def action_focus_search(self) -> None:
        """Focus the search input"""
        self.query_one("#search-input", Input).focus()

    def action_refresh(self) -> None:
        """Refresh the current search"""
        search_input = self.query_one("#search-input", Input)
        if search_input.value:
            asyncio.create_task(self.search_packages(search_input.value))
        else:
            self.notify("ℹ️  Enter a search query first", severity="information", timeout=2)

    def action_show_help(self) -> None:
        """Show help information"""
        help_text = f"""[bold #00d4ff]{APP_NAME} v{APP_VERSION}[/bold #00d4ff]
[dim]{APP_TAGLINE}[/dim]

[bold]Keyboard Shortcuts:[/bold]
  S - Focus search
  I - Install selected package
  A - Add to managed packages
  R - Refresh search
  Q - Quit

[bold]Copyright:[/bold]
  © 2026 DeMoD LLC
  Licensed under MIT License
"""
        self.notify(help_text, timeout=10)


def main():
    """Run the DeMoD Nixpkgs TUI application"""
    app = DeMoDNixpkgs()
    app.title = f"{APP_NAME} v{APP_VERSION}"
    app.sub_title = APP_TAGLINE
    app.run()


if __name__ == "__main__":
    main()

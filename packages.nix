# Managed by DeMoD Nixpkgs
# Copyright (c) 2026 DeMoD LLC
# This file contains package selections organized by category
# You can edit this manually or use DeMoD Nixpkgs to manage it

{ pkgs }:

{
  # Development tools - compilers, languages, version control
  development = with pkgs; [
    # git
    # python3
    # nodejs
    # rustc
    # cargo
  ];

  # Productivity - browsers, editors, office suites
  productivity = with pkgs; [
    # firefox
    # vscode
    # libreoffice
    # thunderbird
  ];

  # Media - audio, video, graphics
  media = with pkgs; [
    # vlc
    # gimp
    # inkscape
    # audacity
  ];

  # Utilities - system tools, terminal utilities
  utilities = with pkgs; [
    # htop
    # tmux
    # fzf
    # ripgrep
    # bat
  ];

  # Custom packages - anything that doesn't fit above
  custom = with pkgs; [
    # Add custom packages here
  ];
}

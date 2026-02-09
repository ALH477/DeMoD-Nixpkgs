{
  description = "DeMoD Nixpkgs - Beautiful Package Management for Nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          textual
          httpx
        ]);

        demod-nixpkgs = pkgs.writeScriptBin "demod-nixpkgs" ''
          #!${pkgs.bash}/bin/bash
          exec ${pythonEnv}/bin/python ${./demod_nixpkgs.py} "$@"
        '';

      in
      {
        # Main package output
        packages = {
          default = demod-nixpkgs;
          demod-nixpkgs = demod-nixpkgs;
        };

        # Development shell with dependencies
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            nix
            # Clipboard support (optional)
            xclip
            wl-clipboard
          ];

          shellHook = ''
            echo "╔══════════════════════════════════════════════════════╗"
            echo "║  DeMoD Nixpkgs Development Environment              ║"
            echo "║  Copyright (c) 2026 DeMoD LLC                        ║"
            echo "╚══════════════════════════════════════════════════════╝"
            echo ""
            echo "Run: python demod_nixpkgs.py"
            echo "Or:  nix run"
            echo ""
            echo "Dependencies installed:"
            echo "  Python 3 with textual and httpx"
            echo "  Nix package manager"
            echo "  Clipboard utilities"
            echo ""
          '';
        };

        # App entry point for 'nix run'
        apps.default = {
          type = "app";
          program = "${demod-nixpkgs}/bin/demod-nixpkgs";
        };
      }
    ) // {
      # NixOS module for system-wide installation
      nixosModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.programs.demod-nixpkgs;
        in
        {
          options.programs.demod-nixpkgs = {
            enable = mkEnableOption "DeMoD Nixpkgs package manager";

            package = mkOption {
              type = types.package;
              default = self.packages.${pkgs.system}.default;
              description = "The demod-nixpkgs package to use";
            };
          };

          config = mkIf cfg.enable {
            environment.systemPackages = [ cfg.package ];
          };
        };

      # Home Manager module
      homeManagerModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.programs.demod-nixpkgs;
        in
        {
          options.programs.demod-nixpkgs = {
            enable = mkEnableOption "DeMoD Nixpkgs package manager";

            package = mkOption {
              type = types.package;
              default = self.packages.${pkgs.system}.default;
              description = "The demod-nixpkgs package to use";
            };
          };

          config = mkIf cfg.enable {
            home.packages = [ cfg.package ];
          };
        };
    };
}

{
  description = "DeMoD Nixpkgs - User-managed package collection";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      # Package collections organized by category
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          
          # Import package definitions from packages.nix
          packageSets = import ./packages.nix { inherit pkgs; };
        in
        {
          # Development tools
          development = pkgs.buildEnv {
            name = "development-packages";
            paths = packageSets.development;
          };

          # Productivity tools
          productivity = pkgs.buildEnv {
            name = "productivity-packages";
            paths = packageSets.productivity;
          };

          # Media and entertainment
          media = pkgs.buildEnv {
            name = "media-packages";
            paths = packageSets.media;
          };

          # System utilities
          utilities = pkgs.buildEnv {
            name = "utility-packages";
            paths = packageSets.utilities;
          };

          # Custom packages
          custom = pkgs.buildEnv {
            name = "custom-packages";
            paths = packageSets.custom;
          };

          # All packages combined
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

      # For NixOS system integration
      nixosModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.demod-nixpkgs.managed-packages;
        in
        {
          options.demod-nixpkgs.managed-packages = {
            enable = mkEnableOption "Enable managed packages from DeMoD Nixpkgs";

            categories = mkOption {
              type = types.listOf (types.enum [ "development" "productivity" "media" "utilities" "custom" "all" ]);
              default = [ "all" ];
              description = "Which package categories to install";
            };
          };

          config = mkIf cfg.enable {
            environment.systemPackages = 
              map (category: self.packages.${pkgs.system}.${category}) cfg.categories;
          };
        };

      # For Home Manager integration
      homeManagerModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.demod-nixpkgs.managed-packages;
        in
        {
          options.demod-nixpkgs.managed-packages = {
            enable = mkEnableOption "Enable managed packages from DeMoD Nixpkgs";

            categories = mkOption {
              type = types.listOf (types.enum [ "development" "productivity" "media" "utilities" "custom" "all" ]);
              default = [ "all" ];
              description = "Which package categories to install";
            };
          };

          config = mkIf cfg.enable {
            home.packages = 
              map (category: self.packages.${pkgs.system}.${category}) cfg.categories;
          };
        };
    };
}

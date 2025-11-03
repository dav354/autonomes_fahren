{
  description = "Development environment for the JetBot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        config = {allowUnfree = true;};
      };
    in {
      devShells.default = pkgs.mkShell {
        packages = [
          pkgs.python3
          pkgs.python3Packages.jupyter
          pkgs.black
          pkgs.isort
        ];

        shellHook = ''
          echo "Welcome to the JetBot flake!"
        '';
      };
    });
}

{
  description = "Development environment for the JetBot";

  inputs = {
    nixpkgs-old.url = "github:NixOS/nixpkgs/nixos-24.11";
    nixpkgs-new.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs-old,
    nixpkgs-new,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgsOld = import nixpkgs-old {
        inherit system;
        config = {allowUnfree = true;};
      };
      pkgsNew = import nixpkgs-new {
        inherit system;
        config = {allowUnfree = true;};
      };
      pythonEnv = pkgsOld.python36.withPackages (pyPkgs:
        with pyPkgs; [
          jupyter-core
        ]);
    in {
      devShells.default = pkgsNew.mkShell {
        packages = with pkgsNew; [
          pythonEnv
          black
          isort
        ];

        shellHook = ''
          echo "Welcome to the JetBot flake!"
        '';
      };
    });
}

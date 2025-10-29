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
      pythonEnv = pkgs.python36;
    in {
      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          pythonEnv
          uv
          black
          isort
        ];

        shellHook = ''
          export UV_PROJECT_ROOT="$PWD"
          export UV_PYTHON="${pythonEnv}/bin/python"
          export UV_NO_SYNC_PROGRESS=1
          if [ ! -d .venv ]; then
            echo "[flake] Creating virtualenv via uv..."
            uv sync --python "$UV_PYTHON"
          fi
          if [ -f .venv/bin/activate ]; then
            # shellcheck disable=SC1091
            source .venv/bin/activate
          fi
        '';
      };
    });
}
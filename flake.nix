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
      pythonEnv = pkgsOld.python39;
    in {
      devShells.default = pkgsOld.mkShell {
        packages =
          (with pkgsOld; [
            pythonEnv
            black
            isort
          ])
          ++ [
            pkgsNew.uv
            pkgsNew.cmake
          ];

        shellHook = ''
          export UV_PROJECT_ROOT="$PWD"
          export UV_PYTHON="${pythonEnv}/bin/python3"
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

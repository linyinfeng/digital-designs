{
  description = "Digital Designs";

  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } (
      { lib, ... }:
      {
        imports = [
          inputs.treefmt-nix.flakeModule
        ];
        systems = [
          "x86_64-linux"
          "aarch64-linux"
        ];
        perSystem =
          { pkgs, ... }:
          {
            devShells.default = pkgs.mkShell {
              packages = with pkgs; [
                python3
                uv
                ty
              ];
              env = lib.optionalAttrs pkgs.stdenv.isLinux {
                # Python libraries often load native shared objects using dlopen(3).
                # Setting LD_LIBRARY_PATH makes the dynamic library loader aware of libraries without using RPATH for lookup.
                LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
              };

              shellHook = ''
                unset PYTHONPATH
                uv sync
                . .venv/bin/activate
              '';
            };
            treefmt = {
              projectRootFile = "flake.nix";
              programs = {
                nixfmt.enable = true;
                prettier.enable = true;
                black.enable = true;
                taplo.enable = true;
              };
            };
          };
      }
    );
}

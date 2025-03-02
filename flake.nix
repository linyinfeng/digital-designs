{
  inputs = {
    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs-lib.follows = "nixpkgs";

    nixpkgs.follows = "cq-flake/nixpkgs";

    cq-flake.url = "github:vinszent/cq-flake";
    cq-flake.inputs.flake-utils.follows = "flake-utils";

    flake-utils.url = "github:numtide/flake-utils";

    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    { flake-parts, ... }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      imports = [
        inputs.flake-parts.flakeModules.easyOverlay
        inputs.treefmt-nix.flakeModule
      ];
      flake.flatFlake = {
        allowed = [
          [
            "cq-flake"
            "nixpkgs"
          ]
        ];
      };
      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          ...
        }:
        {
          packages =
            {
            };
          overlayAttrs =
            {
            };
          checks =
            {
            };
          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              nixfmt.enable = true;
              black.enable = true;
              prettier.enable = true;
            };
          };
          devShells.default = pkgs.mkShell {
            packages = with inputs'.cq-flake.packages; [
              (python.withPackages (
                p: with p; [
                  yacv-server
                ]
              ))
              cq-editor
            ];
          };
        };
    };
}

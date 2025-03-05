{
  pkgs ? import <nixpkgs> { },
}:

let
  python = pkgs.python3;
  poetry = pkgs.poetry.withPlugins (p: with p; [
    poetry-plugin-shell
  ]);
  fhsEnv = pkgs.buildFHSEnv {
    name = "models-env";
    targetPkgs = (
      pkgs:
      [
        python
      ]
      ++ (with pkgs; [
        poetry
        black
        nixfmt-rfc-style
        fstl
      ])
      ++ pkgs.pythonManylinuxPackages.manylinux2014
    );
  };
in
fhsEnv.env

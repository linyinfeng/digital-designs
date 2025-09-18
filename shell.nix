{
  pkgs ? import <nixpkgs> { },
}:

let
  python = pkgs.python3;
  fhsEnv = pkgs.buildFHSEnv {
    name = "models-env";
    targetPkgs = (
      pkgs:
      [
        python
      ]
      ++ (with pkgs; [
        black
        nixfmt-rfc-style
        fstl
      ])
      ++ pkgs.pythonManylinuxPackages.manylinux2014
    );
  };
in
fhsEnv.env

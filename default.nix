{ pkgs ? import <nixpkgs> {} }:

let
  pyPkgs = python-packages: with python-packages; [ pygame ];
  python = pkgs.python2.withPackages pyPkgs;
in pkgs.writeScriptBin "lawn-and-order" ''
   ${python}/bin/python ${./.}/run_game.py
''

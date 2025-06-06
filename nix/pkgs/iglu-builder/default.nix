{ buildBunApplication
, python3
, nix
, cachix
}:

let
  pythonEnv = python3.withPackages (ps: with ps; [
    jinja2
    gitpython
  ]);
in
buildBunApplication {
  src = ../../..;

  nodeModuleHash = "sha256-PVa0hUP2djLIFPqu05f5VDgLr8QExlItNS+4H5LEhYo=";

  buildInputs = [
    pythonEnv
  ];

  bunScript = "prod";

  buildPhase = ''
    patchShebangs lib
  '';

  filesToInstall = [
    "index.ts"
    "routes"
    "lib"
    "schemas"
    "utils"
  ];

  extraBinPaths = [
    nix
    cachix
  ];
}

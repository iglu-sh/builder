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

  nodeModuleHash = "sha256-NKCUv7XRhEtGvUJrqEw24ugqaR0CTNH0bRS+R9ZDciA=";

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
  ];

  extraBinPaths = [
    nix
    cachix
  ];
}

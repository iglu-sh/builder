{ buildBunApplication
, python3
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

  bunScript = "prod";

  filesToInstall = [
    "index.ts"
    "routes"
    "lib"
    "schemas"
  ];

  extraBinPaths = [
    pythonEnv
  ];
}

{ buildBunApplication, nix, cachix, iglu }:

buildBunApplication {
  src = ../../..;

  nodeModuleHash = "sha256-LazStULeCFfeiMyko1AMci7yxFfz195e3huOndLA8TM=";

  buildInputs = [ iglu.dev-python ];

  bunScript = "prod";

  buildPhase = ''
    patchShebangs lib
  '';

  filesToInstall = [ "index.ts" "routes" "lib" "schemas" ];

  extraBinPaths = [ nix cachix ];
}

{ buildBunApplication, nix, cachix, iglu}:

buildBunApplication {
  src = ../../..;

  nodeModuleHash = "sha256-ky69xeAORsvjLorHIFi+oL7DGSi/qbzpYELahKCyRZ8=";

  buildInputs = [ iglu.dev-python ];

  bunScript = "prod";

  buildPhase = ''
    patchShebangs lib
  '';

  filesToInstall = [ "index.ts" "routes" "lib" "schemas" ];

  extraBinPaths = [ nix cachix ];
}

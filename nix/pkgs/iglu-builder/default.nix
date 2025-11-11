{ buildBunApplication, nix, cachix, iglu }:

buildBunApplication {
  src = ../../..;

  nodeModuleHash = "sha256-j9H6GHQl2K2hI99siY8Ya+qxnLjdfIRYsGeKCKXvZ/I=";

  buildInputs = [ iglu.dev-python ];

  bunScript = "prod";

  buildPhase = ''
    patchShebangs lib
  '';

  filesToInstall = [ "index.ts" "routes" "lib" "schemas" ];

  extraBinPaths = [ nix cachix ];
}

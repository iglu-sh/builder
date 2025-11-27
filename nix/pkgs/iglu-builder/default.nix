{ bun2nix
, nix
, cachix
, iglu
, deadnix
, nixpkgs-fmt
}:

bun2nix.writeBunApplication {
  packageJson = ../../../package.json;

  src = ../../..;

  bunDeps = bun2nix.fetchBunDeps {
    bunNix = ./bun.nix;
  };

  nativeBuildInputs = [
    deadnix
    nixpkgs-fmt
  ];

  buildInputs = [
    iglu.dev-python
    nix
    cachix
  ];

  dontUseBunBuild = true;

  startScript = "bun run prod";

  buildPhase = ''
    patchShebangs lib
  '';

}

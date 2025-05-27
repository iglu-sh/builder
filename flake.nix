{
  description = "A very basic flake";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    utils.url = "github:gytis-ivaskevicius/flake-utils-plus?ref=afcb15b845e74ac5e998358709b2b5fe42a948d1";
    iglu-flake.url = "github:iglu-api/flake?ref=d9ca6b5d77b33ce20a0906b7c1491b792777bab5";
  };

  # deadnix: skip
  outputs = inputs@{ self, nixpkgs, utils, iglu-flake }:
    utils.lib.mkFlake {
      inherit self inputs;

      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      #overlay = import ./nix/pkgs;

      sharedOverlays = [
        inputs.iglu-flake.overlays.lib
        inputs.iglu-flake.overlays.pkgs
        #self.overlay
      ];

      outputsBuilder = channels:
        let
          inherit (channels) nixpkgs;
        in
        {
          devShell = nixpkgs.mkShell {
            packages = with nixpkgs; [
              zsh
              wget
              cachix
              bun
              iglu.flakecheck
              python3
              python312Packages.gitpython
              python312Packages.jinja2
            ];
            shellHook = ''
              exec zsh
            '';
          };
          #packages = {
          #  inherit (nixpkgs.iglu) iglu-cache;
          #  inherit (nixpkgs.iglu) iglu-cache-docker;
          #};
        };
    };
}

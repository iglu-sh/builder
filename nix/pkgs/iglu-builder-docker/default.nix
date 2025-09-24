{ dockerTools
, iglu
, bash
, buildEnv
, tini
, nix
, cachix
, stdenv
, toybox
}:

let
  archType =
    if (stdenv.hostPlatform.system == "x86_64-linux") then "amd64" else "arm64";
in
dockerTools.buildImage {
  name = "iglu-builder";
  tag = "v${iglu.iglu-builder.version}-${archType}";

  copyToRoot = buildEnv {
    name = "image-root";
    paths = with dockerTools; [
      iglu.iglu-builder
      bash
      toybox
      nix
      cachix
      tini
      caCertificates
      (fakeNss.override {
        extraPasswdLines =
          [ "nixbld:x:30000:30000:Build user:/var/empty:/noshell" ];
        extraGroupLines = [ "nixbld:x:30000:nixbld" ];
      })
    ];
    pathsToLink = [ "/bin" "/etc" "/var" ];
  };

  config = {
    Env = [
      "NIX_PATH=nixpkgs=https://github.com/NixOS/nixpkgs/archive/refs/tags/25.05.tar.gz"
    ];
    ExposedPorts = { "3000/tcp" = { }; };
    Cmd = [ "/bin/tini" "--" "/bin/iglu-builder" ];
  };
}

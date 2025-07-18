{ dockerTools, iglu, bash, coreutils, buildEnv, tini, nix, cachix, stdenv }:

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
      coreutils
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
    ExposedPorts = { "3000/tcp" = { }; };
    Cmd = [ "/bin/tini" "--" "/bin/iglu-builder" ];
  };
}

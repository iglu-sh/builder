{ dockerTools
, iglu
, bash
, coreutils
, buildEnv
, tini
, cacert
, nix
, cachix
, stdenv
}:

let
  archType = if (stdenv.hostPlatform.system == "x86_64-linux") then "amd64" else "arm64";
in
dockerTools.buildImage {
  name = "iglu-builder";
  tag = "v${iglu.iglu-builder.version}-${archType}";

  copyToRoot = buildEnv {
    name = "image-root";
    paths = [
      iglu.iglu-builder
      bash
      coreutils
      nix
      cachix
      cacert
      tini
    ];
    pathsToLink = [ "/bin" "/etc" ];
  };

  config = {
    ExposedPorts = {
      "3000/tcp" = { };
    };
    Cmd = [ "/bin/tini" "--" "/bin/iglu-builder" ];
    Env = [ "SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt" ];
  };
}

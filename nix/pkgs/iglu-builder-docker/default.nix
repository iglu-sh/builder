{ dockerTools
, iglu
, bash
, buildEnv
, tini
, nix
, cachix
, stdenv
, toybox
, man
}:

let
  archType =
    if (stdenv.hostPlatform.system == "x86_64-linux") then "amd64" else "arm64";

  buildUsers = [ "nixbld:x:30000:30000:Nix build user 0:/var/empty:/noshell" ] ++ (builtins.genList
    (i:
      let
        userNum = i + 1;
        uid = 30000 + userNum;
      in
      "nixbld${toString userNum}:x:${toString uid}:30000:Nix build user ${toString userNum}:/var/empty:/noshell"
    ) 32);
  buildGroup = [
    (builtins.concatStringsSep "," ([ "nixbld:x:30000:nixbld" ] ++ (builtins.genList
      (i:
        "nixbld${toString i}"
      ) 32)))
  ];
in
dockerTools.buildImageWithNixDb {
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
      man
      (fakeNss.override {
        extraPasswdLines = buildUsers;
        extraGroupLines = buildGroup;
      })
    ];
    pathsToLink = [ "/bin" "/etc" "/var" ];
  };

  config = {
    Env = [
      "NIX_PATH=nixpkgs=https://github.com/NixOS/nixpkgs/archive/refs/tags/25.05.tar.gz"
    ];
    ExposedPorts = { "3000/tcp" = { }; };
    Cmd = [ "/bin/iglu-builder" ];
    Entrypoint = [ "/bin/tini" ];
  };
}

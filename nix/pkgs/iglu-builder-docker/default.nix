{ dockerTools
, writeTextFile
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
  nixosVersion = "25.05";
  archType =
    if (stdenv.hostPlatform.system == "x86_64-linux") then "amd64" else "arm64";

  buildUsers = [ "nixbld:x:30000:30000:Nix build user 0:/var/empty:/noshell" ] ++ (builtins.genList
    (i:
      let
        userNum = i;
        uid = 30000 + i;
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
      (writeTextFile {
        name = "nix.conf";
        destination = "/etc/nix/nix.conf";
        text = ''
          accept-flake-config = true
          experimental-features = nix-command flakes
          max-jobs = auto
        '';
      })
    ];
    pathsToLink = [ "/bin" "/etc" "/var" ];
  };

  extraCommands = ''
    # Create dir for /usr/bin/env
    mkdir usr
    ln -s ../bin usr/bin

    # Create /tmp
    mkdir -m 1777 tmp

    # create root Home
    mkdir -vp root
  '';

  config = {
    Env = [
      "NIX_BUILD_SHELL=/bin/bash"
      "NIX_PATH=nixpkgs=https://github.com/NixOS/nixpkgs/archive/refs/tags/${nixosVersion}.tar.gz"
      "PATH=/usr/bin:/bin"
      "PAGER=cat"
      "USER=root"
    ];
    ExposedPorts = { "3000/tcp" = { }; };
    Cmd = [ "/bin/iglu-builder" ];
    Entrypoint = [ "/bin/tini" ];
  };
}

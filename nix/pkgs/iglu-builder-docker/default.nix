{ dockerTools
, iglu
, bash
, stdenv
}:

let
  archType = if (stdenv.hostPlatform.system == "x86_64-linux") then "amd64" else "arm64";
in
dockerTools.buildImage {
  name = "iglu-builder-docker";
  tag = "v${iglu.iglu-builder.version}-${archType}";

  copyToRoot = [
    iglu.iglu-builder
    bash
  ];

  config = {
    ExposedPorts = {
      "3000/tcp" = { };
    };
    Cmd = [ "/bin/iglu-builder" ];
  };
}

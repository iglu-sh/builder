_: prev: {
  iglu = prev.iglu // {
    iglu-builder = prev.callPackage ./iglu-builder { };
    iglu-builder-docker = prev.callPackage ./iglu-builder-docker { };
  };
}


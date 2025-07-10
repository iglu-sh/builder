_: prev: rec {
  iglu = prev.iglu // {
    iglu-builder = prev.callPackage ./iglu-builder { };
    iglu-builder-docker = prev.callPackage ./iglu-builder-docker { };
  };

  python3Packages = prev.python3Packages.overrideScope
    (pfinal: _: (import ./python3 { inherit pfinal; }));

  python3 = prev.python3.override {
    packageOverrides = pfinal: _: (import ./python3 { inherit pfinal; });
  };
}


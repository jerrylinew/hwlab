{
  description = "OpenCV Gesture & Face Lab - Python client + Vue viewer dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python311
              pkgs.nodejs_22
            ];

            shellHook = ''
              # pip-installed binary wheels (opencv, mediapipe) are linked
              # against system libraries that NixOS doesn't put on the
              # default library path - make them available here.
              export LD_LIBRARY_PATH="${nixpkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc.lib
                pkgs.zlib
                pkgs.glib
                pkgs.libGL
                pkgs.libxcb
                pkgs.libx11
                pkgs.libxau
                pkgs.libxdmcp
                pkgs.libxext
                pkgs.libsm
                pkgs.libice
              ]}:$LD_LIBRARY_PATH"

              # Set up a Python virtualenv with OpenCV/MediaPipe/FastAPI etc.
              # (these aren't reliably packaged in nixpkgs, so we use pip).
              # MediaPipe doesn't yet ship wheels for Python 3.13, so we pin
              # the venv to Python 3.11 via python311 above.
              if [ ! -d python-client/.venv ]; then
                python3 -m venv python-client/.venv
              fi
              source python-client/.venv/bin/activate
              pip install -q -r python-client/requirements.txt

              echo ""
              echo "HW Lab dev shell ready."
              echo "  Python client: cd python-client && uvicorn main:app --reload"
              echo "  Vue client:    cd vue-client && npm install && npm run dev"
              echo ""
            '';
          };
        });
    };
}

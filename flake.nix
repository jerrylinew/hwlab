{
  description = "OpenCV Gesture & Face Lab - Python client + Vue viewer dev environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          isDarwin = pkgs.stdenv.isDarwin;
          isLinux = pkgs.stdenv.isLinux;
        in
        {
          default = pkgs.mkShell {
            packages = [
              pkgs.python311
              pkgs.nodejs_22
              pkgs.arduino-cli
            ]
            ++ pkgs.lib.optionals isLinux [
              # OpenCL runtime for GPU-accelerated CV on Linux
              pkgs.ocl-icd
              pkgs.clinfo
            ];

            shellHook = ''
              export LD_LIBRARY_PATH="${
                nixpkgs.lib.makeLibraryPath (
                  [
                    pkgs.stdenv.cc.cc.lib
                    pkgs.zlib
                    pkgs.glib
                    pkgs.libGL
                  ]
                  ++ pkgs.lib.optionals isLinux [
                    pkgs.libxcb
                    pkgs.libx11
                    pkgs.libxau
                    pkgs.libxdmcp
                    pkgs.libxext
                    pkgs.libsm
                    pkgs.libice
                    pkgs.ocl-icd
                  ]
                )
              }:$LD_LIBRARY_PATH"

              if [ ! -d python-client/.venv ]; then
                python3 -m venv python-client/.venv
              fi
              source python-client/.venv/bin/activate
              pip install -q -r python-client/requirements.txt

              echo ""
              echo "HW Lab dev shell ready."
              echo "  Python client: cd python-client && uvicorn main:app --reload"
              echo "  Vue client:    cd vue-client && npm install && npm run dev"
              echo "  XIAO flash:    cd xiao && arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C3 && arduino-cli core install esp32:esp32 && arduino-cli upload -p /dev/ttyACM0 --fqbn esp32:esp32:XIAO_ESP32C3"
              echo ""
            '';
          };
        }
      );
    };
}

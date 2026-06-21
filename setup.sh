#!/usr/bin/env bash
set -euo pipefail

REPO="KaitoTLex/hwlab"
TAG="prod"

echo "==> Fetching latest source tarball URL from GitHub release '${TAG}'..."
TARBALL_URL=$(curl -sSL "https://api.github.com/repos/${REPO}/releases/tags/${TAG}" \
  | grep '"tarball_url"' \
  | cut -d '"' -f 4)

if [ -z "$TARBALL_URL" ]; then
  echo "ERROR: Could not find release '${TAG}' at github.com/${REPO}"
  exit 1
fi

echo "==> Downloading source archive from ${TARBALL_URL}..."
curl -sSL -o hwlab-src.tar.gz "$TARBALL_URL"

echo "==> Extracting archive..."
tar xzf hwlab-src.tar.gz

EXTRACTED_DIR=$(tar tzf hwlab-src.tar.gz | head -1 | cut -d '/' -f 1)
rm hwlab-src.tar.gz

echo "==> Entering directory '${EXTRACTED_DIR}'..."
cd "$EXTRACTED_DIR"

echo "==> Starting nix develop shell..."
echo "    This will set up the full development environment via the Nix flake."
nix develop

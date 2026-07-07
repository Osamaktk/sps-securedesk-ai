#!/usr/bin/env bash
set -euo pipefail

# Rust toolchain installation with writable directories
# This is needed because tokenizers (dependency of chromadb) requires Rust compilation
# and Render's /usr/local/cargo is read-only on Python 3.14 build images.

export CARGO_HOME="${CARGO_HOME:-/opt/render/project/.cargo}"
export RUSTUP_HOME="${RUSTUP_HOME:-/opt/render/project/.rustup}"

mkdir -p "$CARGO_HOME" "$RUSTUP_HOME"

# Only install Rust if cargo is not already available
if ! command -v cargo &>/dev/null; then
    echo "Installing Rust toolchain (CARGO_HOME=$CARGO_HOME)..."
    curl -fsSL https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --no-modify-path 2>&1
    echo "Rust installed successfully."
fi

export PATH="$CARGO_HOME/bin:$PATH"

echo "Building Python dependencies..."
pip install -r requirements.txt

echo "Build complete."
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."
WHEEL_DIR="$REPO_DIR/wheels"

rm -rf "$WHEEL_DIR"
mkdir -p "$WHEEL_DIR"

export TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0;12.0+PTX"
export MAX_JOBS=$(nproc)

cd "$SCRIPT_DIR"
pixi install --frozen

export FORCE_CUDA=1

# Get CUDA version for wheel naming
CUDA_VERSION=$(pixi run python -c "import torch; print(torch.version.cuda.replace('.',''))")

# Build detectron2 wheel
pixi run pip wheel --no-deps --no-build-isolation --wheel-dir "$WHEEL_DIR" \
    "git+https://github.com/facebookresearch/detectron2.git@864913f0e57e87a75c8cc0c7d79ecbd774fc669b"

# Build OpenSeeD wheel
cd "$REPO_DIR"
pixi run --manifest-path "$SCRIPT_DIR/pixi.toml" python setup.py bdist_wheel --dist-dir "$WHEEL_DIR"

# Rename wheels to include CUDA version
for f in "$WHEEL_DIR"/*.whl; do
    new_name=$(basename "$f" | sed "s/-cp311-/+cu${CUDA_VERSION}-cp311-/")
    mv "$f" "$WHEEL_DIR/$new_name"
done

cd $SCRIPT_DIR
pixi run twine upload --repository-url https://pypi.internal.paralleldomain.com/ --username "" --password "" \
    "$WHEEL_DIR"/*.whl

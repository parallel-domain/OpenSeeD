#!/usr/bin/env bash
set -euo pipefail

export FORCE_CUDA=1
export TORCH_CUDA_ARCH_LIST="8.6;8.9;9.0;12.0+PTX"

rm -rf build dist *.egg-info dist

pip wheel --no-deps --wheel-dir dist git+https://github.com/facebookresearch/detectron2.git@864913f0e57e87a75c8cc0c7d79ecbd774fc669b
python setup.py bdist_wheel
twine upload --repository-url https://pypi.internal.paralleldomain.com/ "dist/detectron2-0.6-cp311-cp311-linux_x86_64.whl"
twine upload --repository-url https://pypi.internal.paralleldomain.com/ "dist/OpenSeeD-0.1.0-cp311-cp311-linux_x86_64.whl"

import os
import glob

import setuptools
from setuptools import find_packages

import torch
from torch.utils.cpp_extension import CUDA_HOME, CppExtension, CUDAExtension

os.environ.setdefault("TORCH_CUDA_ARCH_LIST", "8.0;8.6;8.9;9.0;12.0+PTX")

def get_deformable_attention_extensions():
    ops_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "openseed", "body", "encoder", "ops")
    extensions_dir = os.path.join(ops_dir, "src")

    main_file = glob.glob(os.path.join(extensions_dir, "*.cpp"))
    source_cpu = glob.glob(os.path.join(extensions_dir, "cpu", "*.cpp"))
    source_cuda = glob.glob(os.path.join(extensions_dir, "cuda", "*.cu"))

    sources = main_file + source_cpu
    extension = CppExtension
    extra_compile_args = {"cxx": []}
    define_macros = []

    if (os.environ.get('FORCE_CUDA') or torch.cuda.is_available()) and CUDA_HOME is not None:
        extension = CUDAExtension
        sources += source_cuda
        define_macros += [("WITH_CUDA", None)]
        extra_compile_args["nvcc"] = [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ]
    else:
        if CUDA_HOME is None:
            raise NotImplementedError('CUDA_HOME is None. Please set environment variable CUDA_HOME.')
        else:
            raise NotImplementedError('No CUDA runtime is found. Please set FORCE_CUDA=1 or test it by running torch.cuda.is_available().')

    include_dirs = [extensions_dir]
    return [
        extension(
            "MultiScaleDeformableAttention",
            sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
        )
    ]

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().split('\n')

setuptools.setup(
    name="OpenSeeD",
    version="0.1.1",
    author="Zhang, Hao and Li, Feng and Zou, Xueyan and Liu, Shilong and Li, Chunyuan and Gao, Jianfeng and Yang, Jianwei and Zhang, Lei",
    author_email="{hzhangcx, fliay}@connect.ust.hk",
    description="A Simple Framework for Open-Vocabulary Segmentation and Detection",
    url="https://github.com/parallel-domain/OpenSeeD",
    install_requires=install_requires,
    packages=find_packages(),
    ext_modules=get_deformable_attention_extensions(),
    cmdclass={"build_ext": torch.utils.cpp_extension.BuildExtension},
    extras_require={
        "dev": ["flake8", "black==22.3.0", "isort", "twine", "pytest", "wheel"],
    },
    python_requires=">=3.8",
)

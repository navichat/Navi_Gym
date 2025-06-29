"""Setup script for Navi Gym package."""

from setuptools import setup, find_packages

setup(
    name="navi_gym",
    version="0.1.0",
    description="Reinforcement Learning framework for 3D anime avatar training",
    author="Navi Gym Team",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.21.0",
        "taichi>=1.7.0",
        "gymnasium>=0.28.0",
        "websockets>=11.0.0",
        "aiohttp>=3.8.0",
        "tqdm>=4.62.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "mypy>=0.950",
            "tensorboard>=2.8.0",
            "wandb>=0.12.0",
        ],
        "full": [
            "opencv-python>=4.5.0",
            "matplotlib>=3.5.0",
            "pillow>=8.0.0",
            "trimesh>=3.15.0",
            "mmdutils>=0.1.0",
            "librosa>=0.9.0",
            "soundfile>=0.10.0",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)

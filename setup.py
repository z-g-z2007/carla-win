"""
Setup script for CarlaViz
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="carlaviz",
    version="0.1.0",
    author="CarlaViz Team",
    author_email="2906347062@qq.com",
    description="CARLA 3D Visualization Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carlaviz/carlaviz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires="=3.12",
    install_requires=[
        "pygame>=2.0",
        "numpy>=1.21",
        "Pillow>=8.0",
        "PyOpenGL>=3.1",
    ],
    extras_require={
        "web": ["flask>=2.0"],
        "dev": ["pytest", "pytest-cov", "black", "flake8"],
    },
    entry_points={
        "console_scripts": [
            "carlaviz=carlaviz.cli:main",
        ],
    },
)
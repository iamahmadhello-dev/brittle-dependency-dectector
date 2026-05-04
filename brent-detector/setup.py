"""
Setup configuration for Brent Detector package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="brent-detector",
    version="1.0.0",
    author="FYP Student",
    description="Static analysis tool for identifying critical software modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/brent-detector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Software Distribution",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
    install_requires=[
        "networkx>=3.6",
        "matplotlib>=3.10",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "brent-detector=cli.main:main",
            "brent-evaluate=cli.evaluation:main",
        ],
    },
)

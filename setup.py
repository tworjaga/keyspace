#!/usr/bin/env python3
"""
Setup script for Keyspace
"""

from setuptools import setup, find_packages
import os

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="keyspace",
    version="1.0.0",
    author="Keyspace Team",
    author_email="contact@keyspace.example.com",
    description="Advanced password cracking tool with modern GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tworjaga/keyspace",
    packages=find_packages(exclude=["tests", "tests.*", "packaging", "benchmark_results"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "keyspace=main:main",
        ],
        "gui_scripts": [
            "keyspace-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yaml", "*.yml", "*.json"],
        "templates": ["*.html"],
    },
    project_urls={
        "Bug Reports": "https://github.com/tworjaga/keyspace/issues",
        "Source": "https://github.com/tworjaga/keyspace",
        "Documentation": "https://github.com/tworjaga/keyspace/blob/main/DOCUMENTATION_INDEX.md",
        "Funding": "https://github.com/sponsors/tworjaga",
    },
    keywords="password security cracking brute-force dictionary attack security-testing penetration-testing",
    license="MIT",
    zip_safe=False,
)


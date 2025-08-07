#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Setup
Interface de linha de comando moderna e intuitiva para PRFI Protocol
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prfi-cli",
    version="2.0.0",
    author="PRFI Protocol Team",
    author_email="team@prfi.protocol",
    description="🚀 CLI moderno e intuitivo para PRFI Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prfi-protocol/prfi-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "inquirer>=3.1.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "web3>=6.0.0",
        "cryptography>=41.0.0",
        "pyyaml>=6.0",
        "toml>=0.10.2",
        "requests>=2.28.0",
        "psutil>=5.9.0",
        "watchdog>=3.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "prfi=prfi_cli.main:cli",
            "prfi-init=prfi_cli.commands.init:init_wizard",
            "prfi-dashboard=prfi_cli.commands.dashboard:start_dashboard",
        ],
    },
    include_package_data=True,
    package_data={
        "prfi_cli": [
            "templates/*.yaml",
            "templates/*.json",
            "static/*",
            "web/*",
        ],
    },
    zip_safe=False,
)

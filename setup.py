"""Setup script for Git Sniff Otter."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="git-sniff-otter",
    version="1.0.0",
    author="Git Sniff Otter Team",
    author_email="team@gitsniffotter.com",
    description="Automated Git repository analysis and reporting tool with LLM-powered insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/git-sniff-otter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "git-sniff-otter=git_sniff_otter.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

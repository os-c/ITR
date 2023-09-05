"""
    Setup file for ITR.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.5.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ITR",
    version="1.0.4",
    description="Assess the temperature alignment of current targets, commitments, and investment "
    "and lending portfolios.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ortec Finance",
    author_email="joris.cramwinckel@ortec-finance.com",
    packages=find_packages(),
    download_url="https://pypi.org/project/ITR-Temperature-Alignment-Tool/",
    url="https://github.com/os-climate/ITR",
    project_urls={
        "Bug Tracker": "https://github.com/os-climate/ITR",
        "Documentation": "https://github.com/os-climate/ITR",
        "Source Code": "https://github.com/os-climate/ITR",
    },
    keywords=["Climate", "ITR", "Finance"],
    package_data={
        "ITR": ["data/input/*.csv"],
    },
    include_package_data=True,
    install_requires=[
        "dash==2.11.1",
        "dash_bootstrap_components==1.4.2",
        "diskcache==5.6.1",
        "flask==2.2.5",
        "iam-units==2022.10.27",
        "jupyterlab==4.0.4",
        "matplotlib==3.7.2",
        "multiprocess==0.70.14",
        "numpy==1.24.3",
        "openpyxl==3.0.10",
        "openscm-units==0.5.2",
        "orca==1.8",
        "osc-ingest-tools==0.4.3",
        "pandas>=2.0.3",
        "Pint>=0.22",
        "Pint-Pandas>=0.3",
        "psutil==5.9.5",
        "pydantic==1.10.8",
        "pygithub==1.55",
        "pytest==7.3.2",
        "python-dotenv==1.0.0",
        "setuptools>=65.5.1",
        "sphinx<8,>=6",
        "sphinx-autoapi==2.0.1",
        "sphinx-autodoc-typehints==1.21.0",
        "sphinx-rtd-theme==1.3.0",
        "SQLAlchemy==1.4.48",
        "trino==0.326.0",
        "wheel>=0.41.0",
        "xlrd==2.0.1",
    ],
    python_requires=">=3.9",
    extras_require={
        "dev": [
            "nose2",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: MacOS",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
    ],
    test_suite="nose2.collector.collector",
)

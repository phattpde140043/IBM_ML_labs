from setuptools import setup, find_packages

setup(
    name="ibm-ml-labs",
    version="0.1.0",
    description="IBM ML Labs - Machine Learning Project",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
        ],
    },
)

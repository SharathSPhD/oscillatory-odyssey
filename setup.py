from setuptools import setup, find_packages

setup(
    name="oscillatory_odyssey",
    version="0.1.0",
    description="Physics simulations for oscillations, rotations, and resonance",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "sympy",
        "ipywidgets",
        "plotly",
    ],
)
from setuptools import find_packages, setup

setup(
    name="flexycon",
    version="0.0.1",
    package_dir={"": "dotfiles/src"},  # where setuptools should look
    packages=find_packages(where="src"),
)

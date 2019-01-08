from setuptools import find_packages, setup

setup(
    name="core",
    version="0.1",
    packages=find_packages(),
    package_data={"": ["data/*.csv", "data/*.json"]},
)

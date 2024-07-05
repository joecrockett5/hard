import os.path
from setuptools import setup, find_packages


def read(fname):
    ff = os.path.join(os.path.dirname(__file__), fname)
    return open(ff).read() if os.path.exists(ff) else ""


PACKAGE_NAME = "hard"

setup(
    name=PACKAGE_NAME,
    version="0.0.1",
    description="training",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        x for x in read("requirements.txt") if not x.startswith(PACKAGE_NAME)
    ],
)

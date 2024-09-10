from setuptools import setup, find_packages

setup(
    name='LogIt',
    version='0.1',
    packages=find_packages(where='app/routes'),
    package_dir={'': 'app/routes'},  # This tells it that the packages are in src/
)

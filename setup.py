from setuptools import setup, find_packages

setup(
    name='LogIt',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=3.0.0',
        'Flask-Login>=0.6.0',
        'Flask-PyMongo>=3.0.0',
        'Flask-WTF>=1.2.0',
        'pymongo>=4.0.0',
        'dnspython>=2.0.0',
        'Werkzeug>=3.0.0',
        'pytz>=2023.0',
        'python-dateutil>=2.8.0',
        'gunicorn>=21.0.0',
    ],
    python_requires='>=3.9',
)

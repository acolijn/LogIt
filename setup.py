from setuptools import setup, find_packages

setup(
    name='LogIt',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.3.0',
        'Flask-Login>=0.6.0',
        'Flask-PyMongo>=2.3.0',
        'Flask-WTF>=1.1.0',
        'Flask-Bcrypt>=1.0.0',
        'Flask-Cors>=4.0.0',
        'pymongo>=4.0.0',
        'dnspython>=2.0.0',
        'Werkzeug>=2.3.0',
        'bcrypt>=4.0.0',
        'pytz>=2023.0',
        'gunicorn>=21.0.0',
    ],
    python_requires='>=3.9',
)

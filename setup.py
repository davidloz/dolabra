from setuptools import setup, find_packages
import pathlib

VERSION = '1.0'
CURRENT_DIR = pathlib.Path(__file__).parent
README = (CURRENT_DIR / 'README.md').read_text()
PYTHON_REQUIREMENT = '>=3.7.0'

REQUIREMENTS = [
    "Jinja2==2.11.2",
    "mythril==0.23.17",
    "colorama==0.4.3",
    "pypandoc==1.5",
    "py-solc==3.2.0"
]

setup(
    name="dolabra",
    version=VERSION,
    description='Semantic EVM bytecode analyzer based on Mythril',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/davidloz/dolabra',
    author='David Loz',
    author_email='nicetry@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    python_requires=PYTHON_REQUIREMENT,
    entry_points={
        'console_scripts': [
            'dolabra=dolabra.cli.main:main',
        ],
    },
)

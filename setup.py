'''
Function:
    setup the paperdl
Author:
    Charles
微信公众号:
    Charles的皮卡丘
GitHub:
    https://github.com/CharlesPikachu/paperdl
'''
import paperdl
from setuptools import setup, find_packages


'''readme'''
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


'''setup'''
setup(
    name=paperdl.__title__,
    version=paperdl.__version__,
    description=paperdl.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ],
    author=paperdl.__author__,
    url=paperdl.__url__,
    author_email=paperdl.__email__,
    license=paperdl.__license__,
    include_package_data=True,
    entry_points={'console_scripts': ['paperdl = paperdl.paperdl:paperdlcmd']},
    install_requires=list(open('requirements.txt', 'r').readlines()),
    zip_safe=True,
    packages=find_packages()
)
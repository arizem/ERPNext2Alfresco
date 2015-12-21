# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(
    name='erpnext2alfresco',
    version=version,
    description='Export ERPNext Documents to Alfresco automatically',
    author='Arizem',
    author_email='i.o@arizem.de',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)

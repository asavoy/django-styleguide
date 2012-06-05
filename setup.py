from setuptools import setup

PACKAGE = "styleguide"
NAME = "django-styleguide"
DESCRIPTION = "Style guides automatically generated from CSS documentation"
AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=['styleguide'],
    install_requires = [
        'Django>=1.3',
        'docutils>=0.8',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    zip_safe=False,
)

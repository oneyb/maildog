#!/usr/bin/env python

DESCRIPTION = "Custom and easy automatic email replies"
LONG_DESCRIPTION = """maildog is here to help you with tedious emails.

This puppy reads your emails and replies to those which have a fitting ruleset,
using the associated ruleset.
"""

DISTNAME = 'maildog'
MAINTAINER = 'Brian J. Oney'
MAINTAINER_EMAIL = 'brian.j.oney@gmail.com'
URL = 'https://github.com/oneyb/maildog'
LICENSE = 'GPLv2'
DOWNLOAD_URL = 'https://github.com/oneyb/maildog'
VERSION = '0.1'


try:
    from setuptools import setup
    from setuptools.command.install import install as _install
    _has_setuptools = True
except ImportError:
    from distutils.core import setup


def check_dependencies():
    install_requires = []
    with open('requirements.txt', 'r') as f:
        for l in f.readlines():
            install_requires.append(l.split("==")[0])
    try:
        from nltk.corpus import stopwords
        stopwords.words('english')
    except LookupError:
        import nltk
        nltk.download("stopwords")

    return install_requires


class Install(_install):
    """Allow installation of nltk.corpus files, which are external to the nltk
    package
    """
    def run(self):
        _install.do_egg_install(self)
        import nltk
        nltk.download("stopwords")


if __name__ == "__main__":

    install_requires = check_dependencies()
    # install_requires = []

    setup(name=DISTNAME,
          cmdclass={'install': Install},
          author=MAINTAINER,
          author_email=MAINTAINER_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          install_requires=install_requires,
          setup_requires=install_requires,
          # entry_points={
          #     'console_scripts': [
          #         # 'maildog=maildog.maildog:main',
          #         'maildog=maildog:main',
          #     ]},
          packages=['maildog'],
          classifiers=[
              'Intended Audience :: Entrepreneurial/Communication',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'License :: OSI Approved :: GPLv2 License',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS'],
    )

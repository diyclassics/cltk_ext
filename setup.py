from setuptools import setup

setup(
    name='cltk_ext',
    version='0.0.1',
    packages=['cltkext'],
    url='https://github.com/diyclassics/cltk_ext',
    license='MIT License',
    author='Patrick J. Burns',
    author_email='patrick@diyclassics.org',
    description='Extensions to the Classical Language Toolkit (CLTK), e.g. wrappers for external tools.',
    install_requires=['cltk~=1.0.22',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)

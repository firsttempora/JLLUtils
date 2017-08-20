from distutils.core import setup
versionstr = '0.1'
setup(
    name='jllutils',
    packages=['jllutils'], # this must be the same as the name above for PyPI
    version=versionstr,
    description='A library of general utilities',
    author='firsttempora',
    author_email='first.tempora@gmail.com',
    url='https://github.com/firsttempora/JLLUtils', # use the URL to the github repo
    download_url='https://github.com/firsttempora/JLLUtils/tarball/{0}'.format(versionstr), # version must be a git tag
    keywords=['utility', 'general'],
    classifiers=[],
    scripts=['jllutils/datecompare.py', 'jllutils/hashcheck.py']
)

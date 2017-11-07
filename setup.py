from setuptools import setup
import os

def version():
    setupDir = os.path.dirname(os.path.realpath(__file__))
    versionFile = open(os.path.join(setupDir, 'tRep', 'VERSION'))
    return versionFile.read().strip()

setup(name='tRep',
      version=version(),
      description='Taxonomy of microbial genomes',
      url='https://github.com/MrOlm/tRep',
      author='Matt Olm',
      author_email='mattolm@berkeley.edu',
      license='MIT',
      package_data={'tRep': ['VERSION']},
      packages=['tRep'],
      scripts=['bin/quickTaxonomy.py', 'bin/make_Tdb.py'],
      install_requires=[
          'halo',
          'pandas',
          'ete3',
          'drep'
      ],
      zip_safe=False)

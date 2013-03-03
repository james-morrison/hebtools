from setuptools import setup
setup(name='hebtools',
      version='0.1',
      author='James Morrison',
      author_email='james.morrison@gmail.com',
      url='http://jamesmorrison.bitbucket.org',
      license='MIT',
      description='Tools for processing Datawell Waverider raw files',
      packages=['hebtools', 'hebtools/awac', 'hebtools/dwr', 'hebtools/common'],
      requires=['matplotlib','pandas',]
      )
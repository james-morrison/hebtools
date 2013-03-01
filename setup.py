from distutils.core import setup
setup(name='heb_tools',
      version='0.1',
      author='James Morrison',
      author_email='james.morrison@gmail.com',
      url='http://jamesmorrison.bitbucket.org',
      license='MIT',
      description='Tools for processing Datawell Waverider raw files',
      packages=['heb_tools', 'heb_tools/awac', 'heb_tools/dwr'],
      requires=['matplotlib','pandas',]
      )
from setuptools import setup, find_packages
import os

test_data_files = []
test_dir = 'hebtools\\test\\data'
for paths,dirs,files in os.walk(test_dir):
  test_data_files += [[paths, [os.path.join(paths,directory) for directory in files]]]
  
setup(name='hebtools',
      version='0.1',
      author='James Morrison',
      author_email='james.morrison@gmail.com',
      url='http://jamesmorrison.bitbucket.org',
      license='MIT',
      description='Tools for processing Datawell Waverider raw files',
      packages=['hebtools', 'hebtools/awac', 'hebtools/dwr', 'hebtools/common',
                'hebtools/test', 'hebtools/test/data/awac', 'hebtools/test/data/waverider'],
      requires=['matplotlib','pandas'],
      data_files = test_data_files,
      include_package_data=True
      )

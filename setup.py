from setuptools import setup
setup(name='puzzle',
  version   = '1.0',
  description   = 'Classes implementing detection based puzzle solving pipelines.', 
  url       = "https://github.com/ivapylibs/puzzle_solver",
  author    = 'IVALab',
  package_dir   = {"":"puzzle"},
  packages  = ['puzzle','puzzle/piece']
  #packages=setuptools.find_packages(where="puzzle")
)

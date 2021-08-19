from setuptools import setup
setup(name='puzzle',
  version   = '1.0',
  description   = 'Classes implementing detection based puzzle solving pipelines.', 
  url       = "https://github.com/ivapylibs/puzzle_solver",
  author    = 'IVALab',
  packages  = ['puzzle'],
  install_requires=['numpy', 'scipy', 'matplotlib','opencv-python','scikit-image','scikit-learn','functools']
)

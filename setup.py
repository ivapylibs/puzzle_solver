from setuptools import setup, find_packages

<<<<<<< HEAD
setup(
    name    = "puzzle",
    version = "1.1.1",
    description = "Classes implementing detection based puzzle solving pipelines.",
    url     = "https://github.com/ivapylibs/puzzle_solver",
    author  = "IVALab",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy>=1.8.1",
        "matplotlib",
        "opencv-contrib-python",
        "scikit-image",
        "scikit-learn",
        "similaritymeasures",
        "pygame",
        "Lie @ git+https://github.com/ivapylibs/Lie.git",
        "ivapy @ git+https://github.com/ivapylibs/ivapy.git",
        "improcessor @ git+https://github.com/ivapylibs/improcessor.git",
        "trackpointer @ git+https://github.com/ivapylibs/trackpointer.git",
        "detector @ git+https://github.com/ivapylibs/detector.git",
        "perceiver @ git+https://github.com/ivapylibs/perceiver.git",
    ]
)

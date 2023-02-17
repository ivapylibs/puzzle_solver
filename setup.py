from setuptools import setup, find_packages

setup(
    name="puzzle",
    version="1.0.1",
    description="Classes implementing detection based puzzle solving pipelines.",
    url="https://github.com/ivapylibs/puzzle_solver",
    author="IVALab",
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
        "improcessor @ git+https://github.com/ivapylibs/improcessor.git",
        "trackpointer @ git+https://github.com/ivapylibs/trackpointer.git",
        "detector @ git+https://github.com/ivapylibs/detector.git",
    ],
)

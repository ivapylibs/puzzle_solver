# puzzle_solver

Shape-based puzzle solving algorithms, including shape matching and rotation matching

## installation instruction

```
git clone git@github.com:ivapylibs/puzzle_solver.git
pip3 install -e puzzle_solver/
```

The test files are shell command line executable and should work when invoked, presuming that pip installation has been
performed. If no modifications to the source code will be performed then the ``-e`` flag is not necessary (e.g., use the
flag if the underlying code will be modified).

This repo is also backed up by several other libraries from our group:

```
git clone git@github.com:ivapylibs/trackpointer.git
pip3 install -e trackpointer/
git clone git@github.com:ivapylibs/detector.git
pip3 install -e detector/
git clone git@github.com:ivapylibs/improcessor.git
pip3 install -e improcessor/
git clone git@github.com:ivapylibs/Lie.git
pip3 install -e Lie/
git clone git@github.com:ADCLab/puzzleSolvers.git
pip3 install -e puzzleSolvers/
```

## Dependencies

Requires the installation of the following python packages:

- ```numpy```
- ```matplotlib```
- ```scipy```
- ```scikit-learn```
- ```scikit-image```
- ```opencv-python >= 4.0.0.21```
- ```similaritymeasures```
- ```pygame```



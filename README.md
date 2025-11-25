Forked version of the mcm model that allow to call the python wrapper on array instead of single value. By reducing the number of init call, it improves the speed for multiple model calls.

# SWAMI MCM Model

See the original repository for any information

Requirements:
* gfortran
* python >3.5
* libnetcdff-dev


### Python wrapper
Inside the repository:
* Compile the Fortran binary by running `./src/swami//make_wrapper.sh`
* Install the python library `pip install .` in a dedicated environment (`python3 -m venv newEnv`, `source newEnv/bin/activate`)



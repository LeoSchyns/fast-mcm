Forked version of the mcm model that allow to call the python wrapper on array instead of single value. By reducing the number of init call, it improves the speed for multiple model calls.

- The wrapper is rewritten to call the init only once if an array is provided as input which allow an important speed gain.
- It is also rewritten to use stdin/out instead of temporary file (marginal gain)

Provided as it, not widely tested, any bug report is welcomed
  

# SWAMI MCM Model
See the original repository for any information

  
Requirements:

* gfortran

* python >3.5

* libnetcdff-dev

* numpy

  
  

## Python wrapper

Inside the repository:

* Compile the Fortran binary by running `./make_wrapper.sh`

* Install the python library `pip install .` in a dedicated environment (`python3 -m venv newEnv`, `source newEnv/bin/activate`)

## Benchmark
A small benchmark on the wrapper examples from the original repository
| Example | Original |fast-mcm |
|--|--| --|
|Single point| 0.14 s | 0.11 s | 
|Altitude profile| 3.47 s | 0.12 s | 
|Temperature and density| 17.19 s | 0.17 s | 
|Winds| 17.95 s | 0.25 s | 

## New examples
The original examples are still functional and can be reused without any issue. But now the possibility to feed arrays as input exists.
All the input must be an array of the same size except the boolean input that stay single value.

### Single point
No change

### Altitude profile: temperature and density
```python
altitudes  =  np.arange(0.0, 300, 10)

out  =  mcm.run(
	altitude=altitudes,
	latitude=np.full_like(altitudes, 3),
	longitude=np.full_like(altitudes, 15),
	local_time=np.full_like(altitudes, 12),
	day_of_year=np.full_like(altitudes, 53),
	f107=np.full_like(altitudes, 70),
	f107m=np.full_like(altitudes, 69),
	kp1=np.full_like(altitudes, 1),
	kp2=np.full_like(altitudes, 1),
)

dens  =  out.dens
temp  =  out.temp
```

### Temperature and density at 160 km

```python 
lati  =  np.arange(-90, 90, 10)
loct  =  np.arange(0, 24, 3)
latGrid,ltGrid  =  np.meshgrid(lati,loct,indexing='ij')
lat  =  latGrid.flatten()
lt  =  ltGrid.flatten()

out  =  mcm.run(
	altitude=np.full_like(lat,160),
	latitude=lat,
	longitude=np.full_like(lat,15),
	local_time=lt,
	day_of_year=np.full_like(lat,53),
	f107=np.full_like(lat,70),
	f107m=np.full_like(lat,69),
	kp1=np.full_like(lat,1),
	kp2=np.full_like(lat,1),
)

dens  =  np.array(out.dens).reshape(latGrid.shape)
temp  =  np.array(out.temp).reshape(latGrid.shape)
```

### Winds at 80 km

```python 
lati  =  np.arange(-90, 90, 10)
loct  =  np.arange(0, 24, 3)
latGrid,ltGrid  =  np.meshgrid(lati,loct,indexing='ij')
lat  =  latGrid.flatten()
lt  =  ltGrid.flatten()

out  =  mcm.run(
	altitude=np.full_like(lat,80),
	latitude=lat,
	longitude=np.full_like(lat,15),
	local_time=lt,
	day_of_year=np.full_like(lat,53),
	f107=np.full_like(lat,70),
	f107m=np.full_like(lat,69),
	kp1=np.full_like(lat,1),
	kp2=np.full_like(lat,1),
	get_winds=True
)

xwind  =  np.array(out.xwind).reshape(latGrid.shape)
ywind  =  np.array(out.ywind).reshape(latGrid.shape)
```

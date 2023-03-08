# All firm technologies project 

Using PyPSA with [table input interface](https://github.com/carnegie/clab_pypsa)

#
## Installation/setup

1. [Install PyPSA](https://pypsa.readthedocs.io/en/latest/installation.html) with

   ```conda install -c conda-forge pypsa```

   or 

   ```pip install pypsa```


2. Clone this repository with --recursive (this clones clab_pypsa and PyPSA as submodules), for example

   ```git clone https://github.com/carnegie/clab_all_firm --recursive```


3. Install Gurobi

   Follow [installation instructions](https://www.gurobi.com/documentation/10.0/quickstart_windows/cs_python_installation_opt.html) to install Gurobi. Free licenses for academics are available.


#
## Data input files

The data input files are in the Carnegie storage `data`. The data files are in the format of csv files. The data directory is:

```/carnegie/data/Shared/Labs/Caldeira Lab/Everyone/energy_demand_capacity_data/test_case_solar_wind_demand```

#
## Run PyPSA

To run PyPSA, you need to have a case input file and data input files.

pyPSA is run with the command

```python clab_pypsa/run_pypsa.py -f all_firm_case.xlsx```

where `all_firm_case.xlsx` is the case input file.

## Update submodules when changes were made with

```git submodule update --remote --recursive```

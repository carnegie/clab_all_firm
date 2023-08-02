# All firm technologies project 

Using PyPSA with [table input interface](https://github.com/carnegie/clab_pypsa) to produce series of least-cost energy systems with all firm technologies, removing the most valuable technology consecutively.

#
## Installation/setup

### Clone this repository with --recursive to get the submodules

   ```git clone https://github.com/carnegie/clab_all_firm --recursive```

### Set up the environment

   ```cd clab_all_firm```

   ```conda env create -f clab_pypsa/env.yml```

   ```conda activate pypsa_table```


### Install Gurobi

   Follow [installation instructions](https://www.gurobi.com/documentation/10.0/quickstart_windows/cs_python_installation_opt.html) to install Gurobi. Free licenses for academics are available.


#
## Data input files

The data input files are in the Carnegie storage `data`. The data files are in the format of csv files. The data directory is:

```/carnegie/data/Shared/Labs/Caldeira Lab/Everyone/energy_demand_capacity_data/US_solar_wind_demand```

#
## Run PyPSA to recreate the series outputs

The script ```component_removal.py``` runs the optimization, determines the most valuable technology and removes it from the system which is the reoptimized. This process continues until only wind and solar generators are in the system. The script is run with the following command:

```python component_removal.py  -c _case_all_stores --order most --dont_remove_SW```

where the options are:
   - ```-c _case_all_stores```: the name of the case file
   - ```--order most```: the order in which the components are removed, either most valuable or least valuable
   - ```--dont_remove_SW```: if this option is not used, the script will also remove solar and wind generators from the system

The outputs are stored in the ```output_data``` directory in a subdirectory describing the case.

## Plotting the results

The results are plotted with the interactive jupyter notebook ```plot_results.ipynb```. The notebook is run with the following command:

```jupyter notebook plot_results.ipynb```

and plots the results in the ```output_data/*case*/plotting``` directory.



# All firm technologies project 

Using PyPSA with [table input interface](https://github.com/carnegie/clab_pypsa) to produce series of least-cost energy systems with all firm technologies, removing the most valuable technology consecutively.

#
## Installation/setup

### Clone this repository with --recursive to get the submodules

   ```git clone https://github.com/carnegie/clab_all_firm --recursive```

### Set up the environment

   ```cd clab_all_firm```

   ```conda env create -f clab_pypsa/env.yaml```

   ```conda activate pypsa_table```


### Install Gurobi

   Follow [installation instructions](https://www.gurobi.com/documentation/10.0/quickstart_windows/cs_python_installation_opt.html) to install Gurobi. Free licenses for academics are available.


#
## Data input files

The data input files are stored in ```input_data```. It contains solar and wind capacity factors and demand data for the contiguous United States as well as cost input data.

#
## Run PyPSA to recreate the series outputs

The script ```component_removal.py``` runs the optimization, determines the most valuable technology and removes it from the system which is the reoptimized. This process continues until only wind and solar generators are in the system. The script is run with the following command:

```python component_removal.py --order most --dont_remove_SW```

where the options are:
   - ```-c```: the name of the case file, default is ```_case``` which runs the main case file ```all_firm_case.xlsx```
   - ```--order most```: the order in which the components are removed, either most valuable or least valuable
   - ```--dont_remove_SW```: if this option is not used, the script will also remove solar and wind generators from the system

The outputs are stored in the ```output_data``` directory in a subdirectory describing the case.

## Plotting the results

The results are plotted with the interactive jupyter notebook ```plot_results.ipynb```. The notebook is run with the following command:

```jupyter notebook plot_results.ipynb```

and plots the results in the ```figures/``` directory.



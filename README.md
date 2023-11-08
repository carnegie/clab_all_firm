# All firm technologies project 

Using [PyPSA](https://github.com/PyPSA/pypsa) with [table input interface](https://github.com/carnegie/clab_pypsa) to produce series of least-cost energy systems with all firm technologies, removing the most valuable technology consecutively.

#
## Installation/setup

### Clone this repository with --recursive to get the submodules

   ```git clone https://github.com/carnegie/clab_all_firm --recursive```

### Set up the environment

The setup described below uses [conda](https://docs.conda.io/en/latest/miniconda.html) for easy package management.

   ```cd clab_all_firm```

   ```conda env create -f clab_pypsa/env.yaml```

   ```conda activate pypsa_table```


### Install Gurobi

   Follow [installation instructions](https://www.gurobi.com/documentation/10.0/quickstart_windows/cs_python_installation_opt.html) to install Gurobi. Free licenses for academics are available.

If you already have Gurobi installed on your computer, you may find it useful to execute the following commands in the pypsa_table environment:

   ```conda config --add channels https://conda.anaconda.org/gurobi```

   ```conda install gurobi```


#
## Data input files

The data input files are stored in ```input_data``` including the main excel file that defines the electricity network ```input_data/all_firm_case.xlsx```. It also contains wind and solar capacity factors and demand data for the contiguous United States as well as cost input data.

#
## Run PyPSA to recreate the series outputs

The script ```component_removal.py``` runs the optimization, determines the most valuable technology and removes it from the system which is then reoptimized. This process continues until only wind and solar generators are in the system. The script is run in the pypsa_table environment with the following command:

```python component_removal.py --order most --dont_remove_SW```

where the options are:

   - ```--order most```: the order in which the components are removed, either most valuable or least valuable
   - ```--dont_remove_SW```: if this option is not used, the script will also remove solar and wind generators from the system

   - *```-c```: the name of the case file, default is ```_case``` which runs the main case file ```all_firm_case.xlsx```*


The outputs are stored in the ```output_data``` directory in a subdirectory named accoring to the case.

## Plotting the results

The results are plotted with the interactive jupyter notebook ```plot_results.ipynb```. The notebook is run with the following command:

```jupyter notebook plot_results.ipynb```

and plots the results in the ```figures/``` directory.


[![DOI](https://www.zenodo.org/badge/DOI/10.5281/zenodo.8436430.svg)](https://www.doi.org/10.5281/zenodo.8436430)



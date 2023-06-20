import os
import numpy as np
import pickle

def get_values(component_results, parameter):
    # Get values, set nan to zero
    results = component_results[parameter].values
    results[np.isnan(results)] = 0
    return results

def read_component_results(results_dir, pickle_file):
    # Read in the data from pickle file
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        component_results = results['component results']
        # Drop Load from component results
        component_results = component_results.drop(['Load'], level=0)
        # Drop Link with the same name as a Generator
        links = component_results[component_results.index.get_level_values(0) == 'Link'].index.get_level_values(1)
        for link in links:
            if link in component_results[component_results.index.get_level_values(0) == 'Generator'].index.get_level_values(1):
                component_results = component_results.drop(("Link", link))
        component_results = component_results.drop([x for x in component_results.index.get_level_values(1) if 'co2' in x], level=1)
        # Add values of same carrier
        component_results = component_results.groupby(level=1).sum()
    return component_results

def read_objective_value(results_dir, pickle_file):
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        objective_value = results['case results']['objective [€]'].values[0]
    return objective_value

def get_result(component_results, tot_hours, parameter):
    # Get values, set nan to zero
    if parameter == 'cost':
        opex = get_values(component_results, 'Operational Expenditure')
        capex = get_values(component_results, 'Capital Expenditure')
        results = tot_hours * opex + capex
    else:
        results = get_values(component_results, 'Optimal Capacity')
    result_dict = dict(zip(component_results.index, results))
    return result_dict

def get_colors(component_results):
    # 20 colors mapped to all components, no duplicates
    technolgies = ['battery storage', 'beccs', 'CO2 storage tank', 'direct air capture', 'geothermal', 'hydro', 
                    'hydrogen', 'load shedding', 'load shifting backward', 'load shifting forward', 'natgas', 'natgas_wCCS', 'nuclear', 
                    'onwind', 'phs', 'solar-utility']
    colors = ['blue', 'green', 'brown', 'black', 'red', 'cyan', 'pink', 'lime', 'purple', 'magenta', 'gray', 'teal', 'orange', 
              'lightblue',  'darkblue', 'yellow']    

    color_dict = dict(zip(technolgies, colors))
    return color_dict

def get_demand(results_dir, pickle_file):
    # Read in the data from pickle file
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        component_results = results['component results']
        # Get demand
        demand = component_results[component_results.index.get_level_values(0) == 'Load']['Withdrawal'].values[0]
        # Get total hours
        tot_hours = 8784
        demand *= tot_hours
    return demand

def get_abbreviation(key):
    abbreviation_dict = {'battery storage': 'btry', 'beccs': 'beccs', 'CO2 storage tank': 'co2tank', 'direct air capture': 'dac', 
                         'geothermal': 'geo', 'hydro': 'hyd', 'hydrogen': 'h2', 'load shedding': 'll', 
                         'load shifting backward': 'lsb', 'load shifting forward': 'lsf', 'natgas': 'ng', 
                         'natgas_wCCS': 'ng_ccs', 'nuclear': 'nuc', 'onwind': 'wind', 'phs': 'phs', 'solar-utility': 'sol'}
    return abbreviation_dict[key]

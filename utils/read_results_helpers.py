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
        objective_col = [x for x in results['case results'].columns if 'objective' in x]
        objective_value = results['case results'][objective_col[0]].values[0]
    return objective_value  

def get_result(component_results, tot_hours, parameter):
    # Get values, set nan to zero
    if parameter == 'cost':
        opex_col = [x for x in component_results.columns if 'Operational Expenditure' in x]
        opex = get_values(component_results, opex_col[0])
        capex_col = [x for x in component_results.columns if 'Capital Expenditure' in x]
        capex = get_values(component_results, capex_col[0])

        results = opex + capex
    else:
        capacity_col = [x for x in component_results.columns if 'Optimal Capacity' in x]
        results = get_values(component_results, capacity_col[0])
    result_dict = dict(zip(component_results.index, results))
    return result_dict


def get_demand(results_dir, pickle_file):
    # Read in the data from pickle file
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        component_results = results['component results']
        # Get demand
        withdrawal_col = [x for x in component_results.columns if 'Withdrawal' in x]
        demand = component_results[component_results.index.get_level_values(0) == 'Load'][withdrawal_col[0]].values[0]
        # Get total hours
        tot_hours = 8784
        # demand *= tot_hours
    return demand

def calculate_mean_cost_comp_list(results_dir, files_sorted, technologies, total_hours, poi):
    """
    Calculate mean of results for each component
    """
    # Initialize dictionaries to store sum and count for each component keeping the structure of technologies
    sum_dict = {comp_type: {comp: 0 for comp in technologies[comp_type]} for comp_type in technologies}
    count_dict = {comp_type: {comp: 0 for comp in technologies[comp_type]} for comp_type in technologies}

    for case_file in files_sorted:
            
            component_results = read_component_results(results_dir, case_file)
            # Calculate results
            results = get_result(component_results, total_hours, poi)
    
            for comp_type in sum_dict:
                for comp in results:
                    if comp in technologies[comp_type]:
                        sum_dict[comp_type][comp] += results[comp]
                        count_dict[comp_type][comp] += 1
    
    # Calculate mean_dict
    mean_dict = {comp_type: {comp: sum_dict[comp_type][comp]/count_dict[comp_type][comp] if count_dict[comp_type][comp] != 0 else 0 for comp in sum_dict[comp_type]} for comp_type in sum_dict}
    # Sort components based on mean_dict before plotting
    for comp_type in mean_dict:
        mean_dict[comp_type] = dict(sorted(mean_dict[comp_type].items(), key=lambda item: item[1], reverse=True))

    # Flatten dictionary to list
    mean_cost_comp_list = []
    sorted_techs = {}
    for comp_type in mean_dict:
        comps = []
        for comp in mean_dict[comp_type]:
            mean_cost_comp_list.append(comp)
            comps.append(comp)
        sorted_techs[comp_type] = comps

    # Move solar utility to the second position
    mean_cost_comp_list.insert(1, mean_cost_comp_list.pop(mean_cost_comp_list.index('solar-utility')))
    sorted_techs['generators'].insert(1, sorted_techs['generators'].pop(sorted_techs['generators'].index('solar-utility')))

    return mean_cost_comp_list, sorted_techs
import os
import numpy as np
import pickle


def get_values(component_results, parameter):
    """
    Get values, set nan to zero
    """
    results = component_results[parameter].values
    results[np.isnan(results)] = 0
    return results


def read_component_results(results_dir, pickle_file):
    """
    Read in the data from pickle file
    """
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
    """
    Read the objective value from pickle file
    """
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        objective_col = [x for x in results['case results'].columns if 'objective' in x]
        objective_value = results['case results'][objective_col[0]].values[0]
    return objective_value  

def get_result(component_results, parameter, generators=None):
    """
    Get values for parameter
    """
    if parameter == 'cost':
        opex_col = [x for x in component_results.columns if 'Operational Expenditure' in x]
        opex = get_values(component_results, opex_col[0])
        capex_col = [x for x in component_results.columns if 'Capital Expenditure' in x]
        capex = get_values(component_results, capex_col[0])

        results = opex + capex
    elif parameter == 'capacity' or parameter == 'dispatch':
        capacity_col = [x for x in component_results.columns if 'Optimal Capacity' in x]
        capacities = get_values(component_results, capacity_col[0])
        if parameter == 'capacity':
            results = capacities

        else:
            dispatch_col = [x for x in component_results.columns if 'Dispatch' in x]
            results = get_values(component_results, dispatch_col[0])
            # Curtailment is directly calculated for variable generators
            curtailment_col = [x for x in component_results.columns if 'Curtailment' in x]
            curtailment = get_values(component_results, curtailment_col[0])

            unutilized_capacity = capacities*8487 - results
            # Set rows that have a curtailment value to zero
            unutilized_capacity[curtailment != 0] = 0
            # Set rows to zero that have a component name not in generator
            unutilized_capacity[~component_results.index.isin(generators)] = 0
            # Add unutilized capacity to curtailment
            curtailment += unutilized_capacity

            tot_curtailment = np.sum(curtailment)

    else:
        raise ValueError('Parameter not recognized: {0}'.format(parameter))

    result_dict = dict(zip(component_results.index, results))
    if parameter == 'dispatch':
        result_dict['curtailment'] = tot_curtailment
    return result_dict


def get_demand(results_dir, pickle_file):
    """
    Get data from pickle file
    """
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        component_results = results['component results']
        # Get demand
        withdrawal_col = [x for x in component_results.columns if 'Withdrawal' in x]
        demand = component_results[component_results.index.get_level_values(0) == 'Load'][withdrawal_col[0]].values[0]
    return demand


def calculate_mean_cost_comp_list(technologies, passed_results):
    """
    Calculate mean of results for each component
    """
    # Initialize dictionaries to store sum and count for each component keeping the structure of technologies
    sum_dict = {comp_type: {comp: 0 for comp in technologies[comp_type]} for comp_type in technologies}
    count_dict = {comp_type: {comp: 0 for comp in technologies[comp_type]} for comp_type in technologies}

    for results in passed_results:

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

    # Get sorted technologies, sorted by mean cost
    sorted_techs = {comp_type: list(mean_dict[comp_type].keys()) for comp_type in mean_dict}

    # Move solar utility to the second position
    sorted_techs['generators'].insert(1, sorted_techs['generators'].pop(sorted_techs['generators'].index('solar-utility')))

    return sorted_techs


def get_files(res_dir):
    """
    Get all pickle files in res_dir and sort them by order in which components were removed
    """
    files = [f for f in os.listdir(res_dir) if f.endswith('.pickle')]
    files.pop(files.index('all_firm_all.pickle'))
    files_sort = sorted(files, key=lambda x: int(x.split('_')[2]))
    files_sort = list(files_sort)
    files_sort.insert(0, 'all_firm_all.pickle')
    return files_sort


def compute_results(res_dir, poi, files_sorted, firm_gens, pass_results=[]):
    """
    Compute results to be plotted for all case pickle files in all_firm_case folder
    """
    if poi != 'normalized_cost' and not pass_results:
        all_results = []
        for case_file in files_sorted:
            # Load results
            component_results = read_component_results(res_dir, case_file)
            # Calculate results
            results = get_result(component_results, poi, generators=firm_gens)

            all_results.append(results)       
    
    # Calculate the normalized cost from the cost results
    elif poi == 'normalized_cost' and pass_results != []:
        total_demand = abs(get_demand(res_dir, 'all_firm_all.pickle'))
        all_results = [{} for i in range(len(pass_results))]
        for i,case in enumerate(pass_results):
            for comp in case:
                all_results[i][comp] = case[comp]/total_demand

    else:
        raise ValueError("Couldn't compute results for {0}".format(poi))

    return all_results
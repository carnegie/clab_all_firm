# Plotting script for results

import os
import matplotlib.pyplot as plt
import numpy as np
import pickle


def get_cost(results_dir, pickle_file):
    # Read in the data from pickle file
    with open(os.path.join(results_dir, pickle_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        component_results = results['component results']
        # Drop Load and phs_power from component results
        component_results = component_results.drop(['Load', 'Link'], level=0)

        # Get values of Operational Expenditure and Capital Expenditure, set nan to zero
        opex = component_results['Operational Expenditure'].values
        capex = component_results['Capital Expenditure'].values
        opex[np.isnan(opex)] = 0
        capex[np.isnan(capex)] = 0
        total_cost = 8760 * opex + capex
    return total_cost, component_results
def get_colors(component_results):
    # Colors for the bar plot for length of total_cost
    all_components = component_results.index.droplevel(0)
    colors = plt.cm.jet(np.linspace(0, 1, len(all_components)))
    color_dict = dict(zip(all_components, colors))
    return all_components, color_dict
def plot_results(results_dir):
    # Loop over all case pickle files in all_firm_case folder
    for case_file in os.listdir(results_dir):
        # Skip if not pickle file
        if not case_file.endswith('.pickle'):
            continue

        # Load results
        total_cost, component_results = get_cost(results_dir, case_file)

        if case_file == 'all_firm_all.pickle':
            all_components, color_dict = get_colors(component_results)

        # Stacked bar plot of total cost, width half of the width of the plot
        for i in range(len(total_cost)):
            component = component_results.index.droplevel(0)[i]
            plt.bar(case_file.replace('all_firm_','').replace('.pickle',''), total_cost[i], width=0.2, color=color_dict[component], bottom=np.sum(total_cost[:i]))

    # Plot legend, label with second part of index of component_results
    plt.legend(all_components, loc='upper left')

    # Plot labels
    plt.xlabel('Case')
    plt.ylabel('Total cost [$]')
    plt.title('Total cost of all cases')

    # Width of the bars half of the width of the plot
    plt.xlim(-0.5, 1.5)

    # Show plot
    plt.show()

def main():
    # Plotting results
    plot_results('output_data/all_firm_case')

if __name__ == '__main__':
    main()
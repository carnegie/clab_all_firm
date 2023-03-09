# Plotting script for results

import os
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Loop over all cqse pickle files in all_firm_case folder
case_index = 0
for case_file in os.listdir('output_data/all_firm_case'):
    # Skip if not pickle file
    if not case_file.endswith('.pickle'):
        continue

    # Read in the data from pickle file
    with open(os.path.join('output_data/all_firm_case',case_file), 'rb') as f:
        results = pickle.load(f)
        # Get results dictionaries
        case_results = results['case results']
        component_results = results['component results']

        # Get values of Operational Expenditure and Capital Expenditure, set nan to zero
        opex = component_results['Operational Expenditure'].values
        capex = component_results['Capital Expenditure'].values
        opex[np.isnan(opex)] = 0
        capex[np.isnan(capex)] = 0
        total_cost = 8760*opex+capex
        # Colors for the bar plot for length of total_cost
        len_total_cost = len(total_cost)
        colors = plt.cm.jet(np.linspace(0, 1, len_total_cost))

        # Stacked bar plot of total cost, width half of the width of the plot
        for i in range(len(total_cost)):
            print(case_index)
            plt.bar(case_index, total_cost[i], width=0.2, color=colors[i], bottom=np.sum(total_cost[:i]))

    case_index += 1

# Plot legend, label with second part of index of component_results
plt.legend(component_results.index.droplevel(0), loc='upper left')

# Plot labels
plt.xlabel('Case')
plt.ylabel('Total cost [$]')
plt.title('Total cost of all cases')

# Width of the bars half of the width of the plot
plt.xlim(-0.5, 1.5)

# Show plot
plt.show()
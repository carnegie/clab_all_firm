from read_results_helpers import *
from clab_pypsa.run_pypsa import build_network, run_pypsa
import pypsa
import logging
import os
logging.basicConfig(level=logging.INFO)

# Set paths
case_name = "_case"
input_file_name = "all_firm" + case_name
results_dir = "output_data/all_firm_case_cost_increase"
suffix = "_all"

# Build network from file and run PyPSA for full network if it doesn't exist yet
network_all, case_dict, component_list, comp_attributes = build_network(input_file_name+".xlsx")
if not os.path.exists(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".pickle")):
    run_pypsa(network_all, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    network_all.export_to_netcdf(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"))
    logging.info("Saved network to {}".format(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc")))
else:
    network_all = pypsa.Network(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"), override_component_attrs=comp_attributes) 
    logging.info("Loaded network from {}".format(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc")))

# counter = 0
# # Consecutively remove technology with largest total cost and rerun optimization
# keep_removing = True
# while keep_removing == True: 

# Identify technology with largest total cost
result_file_name = input_file_name.replace(case_name, suffix)
# Load results
component_results = read_component_results(results_dir, result_file_name+".pickle")

# If only wind and solar are left, stop
if len(component_results) == 2:
    keep_removing = False

# Calculate total costs
costs = get_result(component_results, case_dict["total_hours"], "cost")
# Sort technologies by total cost and remove technology with largest total cost that is not wind or solar
cost_sorted = sorted(costs.items(), key=lambda x: x[1], reverse=True)
costs_non_zero = [x for x in cost_sorted if x[1] != 0]
print(costs_non_zero)
found_max = False

    # for i in range(len(cost_sorted)):
    #     if found_max == False:
    #         if not any(x in cost_sorted[i][0] for x in ["wind", "solar", "co2_emissions"]):
    #             max_key = cost_sorted[i][0]
    #             found_max = True


for cost_contributor in costs_non_zero:
    print(cost_contributor)
    remove_key = cost_contributor[0]
    print(remove_key)
    # Copy network_all
    network = network_all.copy()
    for component in component_results:

        buses_max, bus_still_in_use = [], []
        # Remove technology with largest total cost from network
        for component_class in network.iterate_components():
            # Get method to get component carriers
            components = getattr(network, component_class[1])
            if hasattr(components, "carrier"):
                for carrier in components.carrier:
                    if carrier == remove_key or (remove_key == "direct_air_capture" and carrier == "CO2 storage tank"):
                        # Get component name of component with this carrier
                        remove_key_component_name = components[components.carrier == carrier].index[0]
                        logging.info("Component name to be removed: {}".format(remove_key_component_name))
                        # Get busses connected to this component
                        for i in ["", "0", "1", "2"]:
                            if hasattr(components, "bus"+i) and getattr(components, "bus"+i).at[remove_key_component_name] != "":
                                logging.info("Bus of component to be removed: {}".format(getattr(components, "bus"+i).at[remove_key_component_name]))
                                if not getattr(components, "bus"+i).at[remove_key_component_name] in buses_max:
                                    buses_max.append(getattr(components, "bus"+i).at[remove_key_component_name])
                        # Remove component
                        network.remove(component_class[0], remove_key_component_name)
                        logging.info("Removed component class: {}".format(component_class[0]))
            
        # Remove bus if no components are connected to it anymore
        for comp in network.iterate_components():
            comps = getattr(network, comp[1])
            for ib,bus_max in enumerate(buses_max):
                bus_still_in_use.append(False)
                for i in ["", "0", "1", "2"]:
                    if hasattr(comps, "bus"+i):
                        if any(getattr(comps, "bus"+i) == bus_max):
                            logging.info("Bus {0} still in use by component {1}".format(bus_max, comps[getattr(comps, "bus"+i) == bus_max].index[0]))
                            bus_still_in_use[ib] = True

        if buses_max != []:
            print("Buses to be removed: {}".format(buses_max))
            for ibrm,bus_rm in enumerate(buses_max):
                if bus_still_in_use[ibrm] == False:
                    network.remove("Bus", bus_rm)
                    logging.info("Removed bus: {} because no components are connected to it anymore".format(bus_rm))

    # Rerun optimization
    abbr = get_abbreviation(remove_key)
    suffix = "_remove_" + abbr
    run_pypsa(network, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
    # counter += 1
   
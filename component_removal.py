from read_results_helpers import *
from clab_pypsa.run_pypsa import build_network, run_pypsa
import pypsa
import logging
import os
import itertools
logging.basicConfig(level=logging.INFO)

# Set paths
case_name = "_case"
input_file_name = "all_firm" + case_name
results_dir = "output_data/all_firm_case_cost_removal_no_geo_hydro"
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

result_file_name = input_file_name.replace(case_name, suffix)


# Consecutively remove technology that leads to largest total cost and rerun optimization
counter = 0
keep_removing = True
while keep_removing == True: 

    # Copy results file to plotting folder
    if not os.path.exists(os.path.join(results_dir, "plotting/")):
        os.makedirs(os.path.join(results_dir, "plotting/"))
    os.system("cp {0} {1}".format(os.path.join(results_dir, result_file_name+".pickle"), os.path.join(results_dir, "plotting/")))        
    os.system("cp {0} {1}".format(os.path.join(results_dir, result_file_name+".xlsx"), os.path.join(results_dir, "plotting/")))

    # Load results
    component_results = read_component_results(results_dir, result_file_name+".pickle")

    # If only wind and solar are left, stop
    # print(component_results)
    # if len(component_results) == 2:
    #     keep_removing = False

    # Calculate total costs
    costs = get_result(component_results, case_dict["total_hours"], "cost")
    c = [comp for comp in costs.keys() if costs[comp] > 0.] 
    if len(costs) == 1 or objectives[results_dir+result_file_name+".pickle"] == 0:
        keep_removing = False
    # Sort technologies by total cost and remove technology with largest total cost that is not wind or solar
    # cost_sorted = sorted(costs.items(), key=lambda x: x[1], reverse=True)
    #costs_non_zero = [x for x in cost_sorted if x[1] != 0 and not any(y in x[0] for y in ["wind", "solar", "co2_emissions"])]
    # print(costs_non_zero)
    # if len(costs_non_zero) == 0:
    #     keep_removing = False

    # found_max = False
    # for i in range(len(cost_sorted)):
    #     if found_max == False:
    #         if not any(x in cost_sorted[i][0] for x in ["wind", "solar", "co2_emissions"]):
    #             max_key = cost_sorted[i][0]
    #             found_max = True


    objectives = {}

    for contributor in c:
        print(contributor)
        remove_key = contributor

        # Copy network_all
        network = network_all.copy()

        buses_max, bus_still_in_use = [], []
        # Remove technology with largest total cost from network
        for component_class in network.iterate_components():
            if component_class[0] == "Load" or component_class[0] == "Bus":
                continue
            # Get method to get component carriers
            components = getattr(network, component_class[1])
            if hasattr(components, "carrier"):
                for carrier in components.carrier:
                    if carrier == remove_key or (remove_key == "direct_air_capture" and carrier == "CO2 storage tank") or (remove_key == "CO2 storage tank" and carrier == "direct_air_capture"):
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
        suffix = "_{0}_".format(counter) + remove_key.replace(" ", "_")
        run_pypsa(network, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
        if hasattr(network, "objective"):
            network.export_to_netcdf(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"))

            # Read objective value
            out_file = "all_firm"+suffix+".pickle"
            print("reading objective value from file:")
            print (results_dir, out_file)
            objectives[out_file] = read_objective_value(results_dir, out_file)
        else:
            print("No objective value found for {}".format(remove_key))
            objectives[out_file] = 0

    # Sort objectives dictionary by objective value
    objectives_sorted = dict(sorted(objectives.items(), key=lambda x: x[1], reverse=True))
    print("\nObjectives: {}".format(objectives))
    print("\nObjectives sorted: {}".format(objectives_sorted))
    result_file_name = list(objectives_sorted.keys())[0].replace(".pickle", "")
    print("Result file name with largest objective: {}".format(result_file_name))
    network_all = pypsa.Network(os.path.join(results_dir, result_file_name+".nc"), override_component_attrs=comp_attributes)
    counter += 1

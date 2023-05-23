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
results_dir = "output_data/all_firm_case_combinations_3"
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
# counter = 0
# keep_removing = True
# while keep_removing == True: 

#     # Copy results file to plotting folder
#     if not os.path.exists(os.path.join(results_dir, "plotting/")):
#         os.makedirs(os.path.join(results_dir, "plotting/"))
#     os.system("cp {0} {1}".format(os.path.join(results_dir, result_file_name+".pickle"), os.path.join(results_dir, "plotting/")))        
#     os.system("cp {0} {1}".format(os.path.join(results_dir, result_file_name+".xlsx"), os.path.join(results_dir, "plotting/")))

# Load results
component_results = read_component_results(results_dir, result_file_name+".pickle")

    # If only wind and solar are left, stop
    # print(component_results)
    # if len(component_results) == 2:
    #     keep_removing = False

# Calculate total costs
costs = get_result(component_results, case_dict["total_hours"], "cost")
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

# All combinations of 5 choices of costs_sorted keys
firm_components = [x for x in costs.keys() if not any(y in x for y in ["wind", "solar", "co2_emissions", "CO2 storage tank"])]
combinations = list(itertools.combinations(firm_components, 3))
print("Number of components: {}".format(len(firm_components)))
print("Number of combinations: {}".format(len(combinations)))
co2_producing = ["natgas", "natgas_wCCS", "geothermal"]
co2_reducing = ["direct air capture", "beccs"]
drop = []
for comb in combinations:
    if any(x in co2_producing for x in comb) and not any(x in co2_reducing for x in comb):
        drop.append(comb)
    if any(x in co2_reducing for x in comb) and not any(x in co2_producing for x in comb):
        drop.append(comb)
combinations = [x for x in combinations if x not in drop]
print("Number of combinations after dropping: {}".format(len(combinations)))
for c in combinations[:10]:
        print("\n",c)

    # objectives = {}

    # for contributor in c:
        # print(contributor)
        # remove_key = contributor
        # print(remove_key)
        # Copy network_all
        network = network_all.copy()
        # for component in component_results:
        #     print(component)

        buses_max, bus_still_in_use = [], []
        # Remove technology with largest total cost from network
        for component_class in network.iterate_components():
            if component_class[0] == "Load" or component_class[0] == "Bus":
                continue
            # Get method to get component carriers
            components = getattr(network, component_class[1])
            if hasattr(components, "carrier"):
                for carrier in components.carrier:
                    # if carrier == remove_key or (remove_key == "direct_air_capture" and carrier == "CO2 storage tank"):
                    if not carrier in c:
                        if carrier == "CO2 storage tank" and "direct air capture" in c:
                            continue
                        if carrier == "direct air capture" and "CO2 storage tank" in c:
                            continue
                        if carrier == "co2 atmosphere" or carrier == "solar-utility" or carrier == "onwind":
                            continue
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
        suffix = ""
        for comp in c:
            abbr = get_abbreviation(comp)
            suffix += "_"+abbr
        # suffix = "_{0}_".format(counter) + remove_key.replace(" ", "_")
        run_pypsa(network, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
        # network.export_to_netcdf(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"))

    #     # Read objective value
    #     out_file = "all_firm"+suffix+".pickle"
    #     objectives[out_file] = read_objective_value(results_dir, out_file)

    # # Sort objectives dictionary by objective value
    # objectives_sorted = dict(sorted(objectives.items(), key=lambda x: x[1], reverse=True))
    # print("Objectives sorted: {}".format(objectives_sorted))
    # result_file_name = list(objectives_sorted.keys())[0].replace(".pickle", "")
    # print("Result file name with largest objective: {}".format(result_file_name))
    # network_all = pypsa.Network(os.path.join(results_dir, result_file_name+".nc"), override_component_attrs=comp_attributes)
    # counter += 1
    # if len(objectives_sorted) == 1:
    #     keep_removing = False

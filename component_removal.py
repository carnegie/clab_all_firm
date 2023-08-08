from utils.read_results_helpers import read_component_results, read_objective_value, get_result
from clab_pypsa.run_pypsa import build_network, run_pypsa
import pypsa
import logging
import os
logging.basicConfig(level=logging.INFO)
import argparse
from sys import exit


def remove_component(network, remove_key):
    """
    Remove component from network
    """
    buses_max = []
    for component_class in network.iterate_components():
        if component_class[0] == "Load" or component_class[0] == "Bus":
            continue
        
        # Remove technology from network with name remove_key and collect buses that are connected to it
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

    return network, buses_max


def remove_empty_buses(network, buses_all):
    """
    Remove buses that are not connected to any component anymore
    """
    bus_still_in_use = []
    # Remove bus if no components are connected to it anymore
    for comp in network.iterate_components():
        comps = getattr(network, comp[1])
        for ib,bus_max in enumerate(buses_all):
            bus_still_in_use.append(False)
            for i in ["", "0", "1", "2"]:
                if hasattr(comps, "bus"+i):
                    if any(getattr(comps, "bus"+i) == bus_max):
                        logging.info("Bus {0} still in use by component {1}".format(bus_max, comps[getattr(comps, "bus"+i) == bus_max].index[0]))
                        bus_still_in_use[ib] = True

    if buses_all != []:
        print("Buses to be removed: {}".format(buses_all))
        for ibrm,bus_rm in enumerate(buses_all):
            if bus_still_in_use[ibrm] == False:
                network.remove("Bus", bus_rm)
                logging.info("Removed bus: {} because no components are connected to it anymore".format(bus_rm))
    
    return network



def main(args):
    """
    Consecutively remove the most valuable technology (i.e. leads to largest total cost increase when removed) and rerun optimization
    """

    # Parsed arguments
    case_name = args.case_name
    order = args.order
    dont_remove_SW = args.dont_remove_SW

    input_file_name = "all_firm" + case_name
    results_dir = "output_data/" + input_file_name + "_" + order + "/"
    suffix = "_all"

    # Build network from file and run PyPSA for full network if it doesn't exist yet
    network_all, case_dict, component_list, comp_attributes = build_network("input_data/"+input_file_name+".xlsx")
    # Overwrite the case name in the input file
    case_dict["case_name"] = "all_firm" + case_name + "_" + order
    if not os.path.exists(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".pickle")):
        run_pypsa(network_all, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        network_all.export_to_netcdf(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"))
        logging.info("Saved network to {}".format(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc")))
    else:
        network_all = pypsa.Network(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"), override_component_attrs=comp_attributes) 
        logging.info("Loaded network from {}".format(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc")))
        print("\n")
        logging.warning("Network all_firm_all already exists, rerunning optimization will overwrite results. Do you want to continue? (y/n)")
        print("\n")
        answer = input()
        if answer == "n":
            exit()

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

        # Calculate total costs
        costs = get_result(component_results, case_dict["total_hours"], "cost")
        c = [comp for comp in costs.keys() if costs[comp] > 0.] 
        if not counter == 0:
            if len(costs) == 1 or objectives[result_file_name+".pickle"] == 0:
                keep_removing = False

        objectives = {}

        # Loop over all contributors to total costs and remove them one by one
        for contributor in c:

            remove_key = contributor
            print("Removing technology: {}".format(remove_key))

            # Don't remove solar/wind if specified
            if dont_remove_SW == True:
                if any(x in remove_key for x in ["wind", "solar"]):
                    continue

            # Copy network_all
            network = network_all.copy()

            # Remove technology from network
            network, buses_max = remove_component(network, remove_key)

            network = remove_empty_buses(network, buses_max)    

            # Rerun optimization
            suffix = "_{0}_".format(counter) + remove_key.replace(" ", "_")
            run_pypsa(network, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)
            if hasattr(network, "objective"):
                network.export_to_netcdf(os.path.join(results_dir, input_file_name.replace(case_name, suffix)+".nc"))

                # Read objective value
                out_file = "all_firm"+suffix+".pickle"
                objectives[out_file] = read_objective_value(results_dir, out_file)
            else:
                objectives[out_file] = 0

        # Sort objectives dictionary by objective value
        # order "most" ("least") means that the most (least) valuable technology is removed
        if order == "least":
            reverse_input = False
        else:
            reverse_input = True

        if objectives == {}:
            keep_removing = False
            break
        objectives_sorted = dict(sorted(objectives.items(), key=lambda x: x[1], reverse=reverse_input))
        result_file_name = list(objectives_sorted.keys())[0].replace(".pickle", "")
        print("Result file name with largest objective: {}".format(result_file_name))
        network_all = pypsa.Network(os.path.join(results_dir, result_file_name+".nc"), override_component_attrs=comp_attributes)
        counter += 1

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--case_name", help="Name of the case to be run, starts with _case", default="_case")
    parser.add_argument("--order", choices=["least", "most"], default="least", help="Order in which technologies are removed, either by increasing cost the least or the most, default least")
    parser.add_argument("--dont_remove_SW", action="store_true", help="Don't remove solar/wind from network")
    arguments = parser.parse_args()
    main(arguments)
from clab_pypsa.run_pypsa import build_network, run_pypsa
import pypsa
import logging
import os
logging.basicConfig(level=logging.INFO)

price_factors = [1., 1.25, 1.5, 1.75, 2.,]

input_file_name = "all_firm_case_natgas_ccs_price"
suffix = ""

network_all, case_dict, component_list, comp_attributes = build_network(input_file_name+".xlsx")

for price_factor in price_factors:
    network_all.generators.loc[network_all.generators.carrier == "natgas_wCCS", "marginal_cost"] = network_all.generators.loc[network_all.generators.carrier == "natgas_wCCS", "marginal_cost"] * price_factor
    network_all.generators.loc[network_all.generators.carrier == "natgas_wCCS", "capital_cost"] = network_all.generators.loc[network_all.generators.carrier == "natgas_wCCS", "capital_cost"] * price_factor
    network_all.links.loc[network_all.links.carrier == "direct air capture", "marginal_cost"] = network_all.links.loc[network_all.links.carrier == "direct air capture", "marginal_cost"] * price_factor
    network_all.links.loc[network_all.links.carrier == "direct air capture", "capital_cost"] = network_all.links.loc[network_all.links.carrier == "direct air capture", "capital_cost"] * price_factor
    
    suffix = "_" + str(price_factor).replace(".", "p")
    run_pypsa(network_all, input_file_name+".xlsx", case_dict, component_list, outfile_suffix=suffix)

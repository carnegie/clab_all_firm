import matplotlib.pyplot as plt


def get_hatching_color(component, technologies, color_dict):
    """
    Get hatching for each component
    """
    if component in technologies['generators']:
        if component == 'onwind':
            fill_color = hatch_color = 'lightblue'
        elif component == 'solar-utility':
            fill_color = hatch_color = 'yellow'
        else:
            index = technologies['generators'].index(component)  - 2
            fill_color = hatch_color = color_dict[index]
        hatched = ''
    elif component in technologies['storage_unconstrained']:
        index = technologies['storage_unconstrained'].index(component)
        hatched = '///'
        fill_color = 'white'
        hatch_color = color_dict[index]
    elif component in technologies['storage_constrained']:
        index = technologies['storage_constrained'].index(component)
        hatched = 'ooo'
        fill_color = 'white'
        hatch_color = color_dict[index]
    else:
        index = technologies['demand_handling'].index(component)
        hatched = '+++'
        fill_color = 'white'
        hatch_color = color_dict[index]
    return hatched, fill_color, hatch_color

def set_title(outfile_suffix, ax):
    """
    Set title for plot
    """
    if "most" in outfile_suffix:
        large_small = 'Largest'
    else:
        large_small = 'Smallest'
    if "no_generators" in outfile_suffix:
        add = ', no firm generators'
    else:
        add = ''
    ax.set_title('{0} cost increase{1}'.format(large_small, add))
    # Set title size and position
    ax.title.set_size(14)
    ax.title.set_position([.5, 1.3])
    plt.setp(ax.get_xticklabels(), rotation=40, ha='right', rotation_mode='anchor', fontsize=8)
    return ax

def set_x_y_labels(outfile_suffix, poi, ax):
    """
    Set x and y labels
    """
    if "most" in outfile_suffix:
        most_leat = 'most'
    else:
        most_leat = 'least'
    ax.set_xlabel('Firm technology that increases total cost {0} when removed'.format(most_leat))

    if poi == 'cost':
        unit = '€'
    elif poi == 'capacity':
        unit = 'MW (or tCo2 for CO2 storage)'
    elif poi == 'normalized_cost':
        unit = '€/MWh covered demand'
    else:
        print('No unit defined for {0}'.format(poi))
        unit =  ''
    ax.set_ylabel('Total {0} [{1}]'.format(poi.replace('_',' '), unit))
    return ax

def get_colors():
    """
    Get colors for each component
    """
    
    # Colors for length of technologies
    colors = ['mediumturquoise', 'orange', 'green', 'grey', 'lightgrey', 'indianred']
    import seaborn as sns
    colors += sns.color_palette("hls", 9)[1:]
    
    return colors
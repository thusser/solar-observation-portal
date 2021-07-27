from math import radians, cos, sin, sqrt
from copy import deepcopy


def expand_dither_pattern(expansion_details):

    '''
    Takes in a valid configuration and valid set of dither parameters, and expands the instrument_configs within the
    configuration with offsets to fit the dither pattern details specified.
    :param expansion_details: a valid dictionary containing the `configuration`, and a number of pattern expansion
                           parameters such as `num_points`, `pattern`, `point_spacing` and others.
    :return: Configuration with expanded list of instrument_configurations.
    '''
    configuration_dict = expansion_details.get('configuration', {})
    offsets = []
    final_instrument_configs = []
    instrument_configs = configuration_dict.get('instrument_configs', [])

    offsets = expand_pattern(expansion_details)

    for offset in offsets:
        for instrument_config in instrument_configs:
            instrument_config_copy = deepcopy(instrument_config)
            if 'extra_params' not in instrument_config_copy:
                instrument_config_copy['extra_params'] = {}
            instrument_config_copy['extra_params']['offset_ra'] = round(offset[0], 3)
            instrument_config_copy['extra_params']['offset_dec'] = round(offset[1], 3)
            final_instrument_configs.append(instrument_config_copy)

    configuration_dict['instrument_configs'] = final_instrument_configs
    return configuration_dict


def expand_mosaic_pattern(expansion_details):
    '''
    Takes in a valid request with one configuration and valid set of mosaic parameters,
    and expands the configuration within the request with new targets using offsets to fit the
    mosaic pattern details specified.
    :param expansion_details: a valid dictionary containing the `request`, and a number of pattern expansion
                           parameters such as `num_points`, `pattern`, `point_spacing` and others.
    :return: Request with expanded list of configurations with different targets following pattern.
    '''
    request_dict = expansion_details.get('request', {})
    offsets = []
    configurations = []
    configuration = request_dict.get('configurations', [{}])[0]

    offsets = expand_pattern(expansion_details)

    for offset in offsets:
        configuration_copy = deepcopy(configuration)
        configuration_copy['target']['ra'] += (offset[0] / 3600.0)
        configuration_copy['target']['dec'] += (offset[1] / 3600.0)
        configurations.append(configuration_copy)

    request_dict['configurations'] = configurations
    return request_dict


def expand_pattern(expansion_details):
    '''
    Takes in just a set of pattern expansion parameters and returns a set of ra/dec offsets following
    the pattern parameters provided
    :param expansion_details: a valide dictionary containing a number of pattern expansion
                           parameters such as `num_points`, `pattern`, `point_spacing` and others.
    :return: list of x/y (ra/dec) offset tuples
    '''
    pattern = expansion_details.get('pattern')
    if pattern == 'line':
        offsets = calc_line_offsets(expansion_details.get('num_points'), expansion_details.get('point_spacing'), expansion_details.get('orientation'),
                                    expansion_details.get('center'))
    elif pattern == 'spiral':
        offsets = calc_spiral_offsets(expansion_details.get('num_points'), expansion_details.get('point_spacing'))
    elif pattern == 'grid':
        offsets = calc_grid_offsets(expansion_details.get('num_rows'), expansion_details.get('num_columns'), expansion_details.get('point_spacing'),
                                    expansion_details.get('line_spacing'), expansion_details.get('orientation'), expansion_details.get('center'))

    return offsets

def calc_line_offsets(num_points, point_spacing, orient, center):
    """Calculate offsets for a LINE dither pattern with <num_points> spaced
    <point_spacing> arcseconds apart along a line of <orient> degrees East of North
    (clockwise from North through East)
    Returns a list of tuples for the offsets"""

    offsets = []

    sino = sin(radians(orient))
    coso = cos(radians(orient))
    # A centered line pattern has the midpoint of the line with 0 offset
    distance_offset = -((num_points-1)*point_spacing) / 2.0 if center else 0.0

    for i in range(0, max(num_points, 0)):
        distance = i*point_spacing + distance_offset
        # Angles measured clockwise from North ("y-axis") rather than anti-clockwise
        # from East ("x-axis")
        x_offset = (distance * -sino)
        y_offset = (distance * coso)
        offsets.append((x_offset, y_offset))
    return offsets


def calc_spiral_offsets(num_points, point_spacing):
    """ Calculates offsets for a spiral pattern spaced <point_spacing> arcseconds apart and spiraling outward
        from the origin until <num_points> is reached. Points are calculated using this equation:
        https://math.stackexchange.com/questions/2335055/placing-points-equidistantly-along-an-archimedean-spiral-from-parametric-equatio
    """
    offsets = [(0,0),]

    n = 1
    r = 1  # This is a parameter related to size of spirals. It seems like distance between spirals is roughly r * point_spacing

    while len(offsets) < num_points:
        root_dist = sqrt(2*point_spacing*n / r)
        x = r * root_dist * cos(root_dist)
        y = r * root_dist * sin(root_dist)
        offsets.append((x, y))
        n += 1

    return offsets


def calc_grid_offsets(num_rows, num_columns, point_spacing, line_spacing, orient=90, center=False):
    """Calculates offsets for a grid of <num_points> (must be a square number
    if scalar or a tuple of (n_columns x n_rows) grid points) with <point_spacing>
    arcseconds apart vertically and <line_spacing> arcseconds apart horizontally at 0 orientation,
    orientated with rows increasing along <orient> degrees East of North
    (clockwise from North through East)
    """
    offsets = []

    # A centered grid pattern has the middle of the grid corresponding with an offset of 0
    row_distance_offset = -(point_spacing * (num_rows-1)) / 2.0 if center else 0.0
    col_distance_offset = -(line_spacing * (num_columns-1)) / 2.0 if center else 0.0
    sino = sin(radians(orient))
    coso = cos(radians(orient))
    rotated_x_offset = coso * col_distance_offset - sino * row_distance_offset
    rotated_y_offset = sino * col_distance_offset + coso * row_distance_offset

    for column in range(0, num_columns):
        if (column % 2) == 0:
            rows = range(0, num_rows)
        else:
            rows = reversed(range(0, num_rows))
        for row in rows:
            # Angles measured clockwise from North ("y-axis") rather than anti-clockwise
            # from East ("x-axis")
            base_x = column * line_spacing
            base_y = row * point_spacing
            x_offset = base_x * coso + base_y * -sino + rotated_x_offset
            y_offset = base_x * sino + base_y * coso + rotated_y_offset
            offsets.append((x_offset, y_offset))

    return offsets

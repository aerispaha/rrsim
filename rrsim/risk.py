from hhcalcs import hydraulics as h
#functions for completing risk related analyses on infrastructure data

def high_risk_fraction(sewer_df):
    """
    return a fraction that represents the proportion of assets that have a "high"
    risk of failure, based on the age and useful life of each segment. Logic for
    now on what constitutes high risk current is whether pipe has negative RUL
    """

    risky_length = sewer_df.loc[sewer_df.RemainingLife < 0, 'Length'].sum()
    total_length = sewer_df.Length.sum()

    return risky_length / total_length


def replacement_cost(asset):
    """
    cost to replace inkind each asset in the dataframe with a hydraulically
    equivalent new asset.
    """

    d = asset.Diameter
    h = asset.Height
    w = asset.Width

    if d is not None:
        replacement_size = max(18, d) #min val of 18"

    if (h and w) is not None:
        if h > 96:
            #replce with box


    # #find equivalent replacements
    # print 'diameter={}, slope={}, height={}, width={}, shape={}'.format(
    #     asset.Diameter, asset.Slope, asset.Height, asset.Width, asset.PIPESHAPE
    # )
    #
    # slope = 0.5#asset.Slope
    # if slope is None:
    #     slope = 0.5
    # existing_capacity = h.manningsCapacity(diameter=asset.Diameter,
    #                                        slope=slope,
    #                                        height=asset.Height,
    #                                        shape=asset.PIPESHAPE,
    #                                        width=asset.Width,
    #                                        )
    #
    # replacement_size = h.minimumEquivalentCircularPipe(existing_capacity, slope)
    # print 'existing_capacity={}'.format(existing_capacity)
    # print 'replacement_size={}'.format(replacement_size)
    # replacement_cap = h.manningsCapacity(diameter=replacement_size,
    #                                        shape=asset.PIPESHAPE, slope=slope
    #                                        )
    #
    # #compute the cost
    # print 'existing_capacity={}, replacement_size={}, replacement_cap={}'.format(
    #     existing_capacity, replacement_size, replacement_cap)

    return replacement_size


def failure_expected_value(sewer_df):
    """
    sum of the cost to replace each asset in the dataframe that is expected to
    fail in a given year. Each asset should be replaced with a new asset that is
    hydraulically equivalent.
    """
    pass

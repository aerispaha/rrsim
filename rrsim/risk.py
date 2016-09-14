#functions for completing risk related analyses on infrastructure data

def high_failure_risk_fraction(sewer_df):
    """
    return a fraction that represents the proportion of assets that have a "high"
    risk of failure, based on the age and useful life of each segment. Logic for
    now on what constitutes high risk current is whether pipe has negative RUL
    """



    pass


def replacement_cost(sewer_df):
    """
    cost to replace inkind each asset in the dataframe with a hydraulically
    equivalent new asset.
    """

    #find equivalent replacements

    #compute the cost

    pass


def failure_expected_value(sewer_df):
    """
    sum of the cost to replace each asset in the dataframe that is expected to
    fail in a given year. Each asset should be replaced with a new asset that is
    hydraulically equivalent.
    """
    pass

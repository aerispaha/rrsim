import pandas as pd
import sewer_report_utils as sru
import math

lifespans = {'Brick':150, 'Concrete':150, 'Clay':150, 'Metal':150, 'Polymer':150, 'Unkown/Other':150}
lifespan_std = {'Brick':10, 'Concrete':10, 'Clay':10, 'Metal':10, 'Polymer':10, 'Unkown/Other':10}

def project_failure_from_investment_profile(investment_prof):

    """
    given an annual invesment profile, this function returns a dataframe holding
    the end of life (failure) projects given each assets characteristics. Uses
    normal dist about the mean of the lifespan.
    """

    cohorts = sru.cohortorder

    projections = [] #array of dataframes
    for cohort in cohorts:

        df = investment_prof[[cohort]] #work with one column at a time

        #apply the normal dist to each year with its mileage installed
        arr = df.index.map(lambda x: normdist_failures_from_year(int(x), cohort, df.loc[x, cohort]))
        dfbig = pd.concat(arr, axis=1) #combines into one dataframe with year as index
        totaldf = pd.DataFrame({cohort:dfbig.sum(axis=1)})

        #hold on to the total row
        projections.append(totaldf)


    all_projections = pd.concat(projections, axis=1)
    all_projections['Total'] = all_projections.sum(axis=1)

    return all_projections


def normdist_failures_from_year(installyear, cohort, miles_installed):

    """
    returns a dataframe with years as the index and Miles Failed as the single column
    based on a normal distribution of expected miles failed. Inputs are the install year,
    miles installed, and pipe cohort.
    """

    lifespan = lifespans[cohort]
    std = lifespan_std[cohort] #standard deviation of lifespan
    failyear = installyear + lifespan

    dist_range = list(range(failyear-50, failyear+50)) #100 years about the mean
    key = '{}mi Installed {}'.format(round(miles_installed), installyear)
    d = {'Year':dist_range, key:0}
    df = pd.DataFrame(d)

    #compute probability distribution function (normal dist) multiplied by the
    #miles installed. failyear here is analogous to the mean.
    df[key] = df.apply(
                        lambda x: normpdf(x['Year'], failyear, std)*miles_installed,
                        axis=1
                        )

    return df.set_index(['Year'])


def normpdf(x, mean, sd):
    """
    Normal Probability Distribution Function

    return the probability based on a normal distribution
    guassian curve, given the x value, mean, and standard deviation.
    """
    #this because i can't get scipy to install
    var = float(sd)**2
    pi = 3.1415926
    denom = (2*pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

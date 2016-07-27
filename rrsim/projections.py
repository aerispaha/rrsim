import pandas as pd
import utils as sru
import math


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
                        lambda x: sru.normpdf(x['Year'], failyear, std)*miles_installed,
                        axis=1
                        )

    return df.set_index(['Year'])




def sewer_age_projection(sewerdf, trend_period, projected_year=2065):
    """
    given a sewer data frame, a sample period with which to base the project on
    and a year in the future, and estimate of the expected average sewer age is
    returned.
    """
    age_deriv_df = sewer_age_deriv(sewerdf, startyear=trend_period[0], endyear=trend_period[1])

    avg_age_rate = age_deriv_df.AgeRate.mean()
    period_end_age = age_deriv_df.loc[age_deriv_df.Year == trend_period[1]].Age
    years_until_target = projected_year - trend_period[1]

    projected_age = period_end_age + (years_until_target * avg_age_rate)

    print 'Avg rate of aging between {} and {} = {}'.format(trend_period[0], trend_period[1], avg_age_rate)
    print 'Assuming the avg age is {} in {}, the projected age in {} will be {}'.format(
                period_end_age, trend_period[1], projected_year, projected_age
            )

    return projected_age

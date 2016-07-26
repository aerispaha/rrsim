import pandas as pd
import sewer_report_utils as sru
import projections as proj
from datetime import datetime


def run_rr_simulation(sewer_df, annual_replacements, startdate):

    sewers = sewer_df[:]
    print 'Total Miles = {}'.format(sewers.Length.sum()/5280)

    #prep data: assume that sewers with 9999 or UNK install year installed at 1900
    sewers['Year'] = sewers.Year.fillna(1900)
    sewers.loc[sewers.Year > 9000, 'Year'] = 1900

    #calculate the remaining useful years for each assets
    sewers['RemainingLife'] = sewers.apply(lambda x: remaining_life_span(x, startdate), axis=1)

    #sewers['Year'] = sewers.Year.replace( [9952., 9973., 9974., 9983., 9999.], 1900)
    #create Dataframe to hold result for each year
    res_columns = ['Year', 'AvgAge', 'AvgRemainingLife', 'MinRemainingLife', '75thPercRemLife', '25thPercRemLife', 'AvgAgeOfReplaced', 'OldestReplaced', 'CumulativeMiles']
    results_df = pd.DataFrame(columns=res_columns, data=None)

    snapshots = {}
    date = startdate
    cumulative_miles = 0.0
    for miles in annual_replacements:

        #measure this years stats before making improvements
        avg_age = sru.average_sewer_age(sewers, datetime(date,1,1))
        min_rem_life = sewers.RemainingLife.min()
        percentile75 = sewers.RemainingLife.quantile(0.75)
        percentile25 = sewers.RemainingLife.quantile(0.25)
        #length weighted avg remaining useful life
        avg_rem_life = (sewers.RemainingLife * sewers.Length).sum() / sewers.Length.sum()

        #find candidates, and replace
        repl = find_replacement_candidates(sewers, miles, date)
        sewers = apply_replacements(sewers, repl, date)

        #snapshots.update({date:repl}) #hold on to snapshots of each year
        avg_age_replaced = sru.average_sewer_age(repl, datetime(date,1,1))
        oldestreplaced = repl.Year.min()

        #compute and record this year's results
        res = [date, avg_age, avg_rem_life, min_rem_life, percentile75, percentile25, avg_age_replaced, oldestreplaced, cumulative_miles]
        results_df = results_df.append(pd.DataFrame(columns = res_columns, data = [res]))

        #increment the year that is currently being modeled and age each sewer segment
        date += 1
        sewers['RemainingLife'] = sewers['RemainingLife'] - 1
        cumulative_miles += repl.Length.sum() / 5280.0



    return {'results':results_df, 'snapshots':snapshots, 'sewersfinal':sewers}


def remaining_life_span(asset, replacement_year):

    lifespan = proj.lifespans.get(asset.Material, 150) #assume 150 if not found
    age = replacement_year - asset.Year
    remaininglife = lifespan - age

    if not pd.isnull(asset.LinerDate):
        lifespan = 50
        age = replacement_year - asset.LinerDate
        remaininglife = lifespan - age

    return remaininglife

def find_replacement_candidates(sewer_df, replacement_miles, replacement_year):
    """
    Given the raw sewer data and a desired number of miles to replace,
    a dataframe is retured including the top candidates for replacement.
    Candidates are selected based on their remaining life span based on their
    age, cohort life span, and lining history (if any).
    """

    #compute the remaining life for each  asset
    #simply increment the remaning life down a year if the col exists
    if 'RemainingLife' not in sewer_df.columns:
        sewer_df['RemainingLife'] = sewer_df.apply(lambda x: remaining_life_span(x, replacement_year), axis=1)

    #sort on the remaining life, then add a cumulative length column
    df = sewer_df.sort_values('RemainingLife')
    df['CumulativeLength'] = df.Length.cumsum() / 5280.0 #conver to miles

    #return a slice of the dataframe where the total length equals
    #the targetted replacement miles
    df = df.loc[df.CumulativeLength <= replacement_miles]

    return df.drop('CumulativeLength', axis=1)


def apply_replacements(orig_sewers, replaced_sewers, replacement_year):
    """
    given the original data set, a subset to be replaced, and the year of the
    replacement, a dataframe is return of the entire dataset with the replacements
    applied.
    """
    #create replacement sewer data
    def replace_asset(asset, replacement_year):

        asset.Material = 'Concrete'
        asset.RemainingLife = proj.lifespans[asset.Material]
        asset.Year = replacement_year
        asset.LinerDate = None
        return asset

    #data will now reflect a new asset (new install date, modern material, etc)
    replaced_assets = replaced_sewers.apply(lambda x: replace_asset(x, replacement_year), axis=1)

    #drops assets from original data set based on the index (OBJECTID)
    #then appends the new assets
    sewers_with_replacements = orig_sewers.drop(replaced_assets.index).append(replaced_assets)


    return sewers_with_replacements

import pandas as pd
import utils as sru
import defs
import projections as fp
from datetime import datetime
import os


def run_rr_simulation(sewer_df, annual_replacements, startdate,
                      results_dir = None, return_snapshot=False, sample=None):

    """
    Given a dataframe of sewer segments (presumably from GIS/DataConv), simulate
    a replacement program by replacing the oldest sewers up to a certain
    annual replacement amount. A dataframe is returned by default including key
    performance indicators related to the overall health of the sewer system at
    each year in the future included in the simulation.
    """

    #copy the dataframe
    sewers = sewer_df[:]
    if sample:
        #scale the scope
        sewers=sewers.sample(frac = sample)
        annual_replacements = [sample * x for x in annual_replacements]

    #prep data: assume that sewers with 9999 or UNK install year installed at 1900
    sewers.loc[pd.isnull(sewers.Year), 'Year'] = 1900
    sewers.loc[sewers.Year > 9000, 'Year'] = 1900

    #calculate the remaining useful years for each assets
    sewers['RemainingLife'] = sewers.apply(lambda x: remaining_life_span(x, startdate), axis=1)

    #create Dataframe to hold result for each year
    res_columns = ['Year', 'AvgAge', 'AvgRemainingLife', 'AvgAgeOfReplaced',
                   'riskymiles', 'riskyfraction']

    results_df = pd.DataFrame(columns=res_columns, data=None)

    if results_dir:
        xlpath = os.path.join(results_dir, '{}_{}.xlsx'.format(annual_replacements[0], startdate))
        excelwriter = pd.ExcelWriter(xlpath)
        #save the initial data set to the first sheet
        sewers.sort_values('RemainingLife').to_excel(excelwriter, 'existing_assets')

    #snapshots = {}
    date = startdate
    cumulative_miles = 0.0
    for miles in annual_replacements:
        #simulate the annual replacement milage in each year provided

        if results_dir:
            #save a snapshot of the data if a results_dir is provided
            sheetname = '{}'.format(date)
            sewers.sort_values('RemainingLife').to_excel(excelwriter, sheetname)

        #measure this years stats before making improvements
        avg_age = sru.average_sewer_age(sewers, datetime(date,1,1))
        # min_rem_life = sewers.RemainingLife.min()
        # percentile75 = sewers.RemainingLife.quantile(0.75)
        # percentile25 = sewers.RemainingLife.quantile(0.25)
        riskymiles = sewers.loc[sewers.RemainingLife < 0, 'Length'].sum() / 5280.0
        riskyfraction = sewers.loc[sewers.RemainingLife < 0, 'Length'].sum() / sewers.Length.sum()

        #length weighted avg remaining useful life
        avg_rem_life = (sewers.RemainingLife * sewers.Length).sum() / sewers.Length.sum()

        #find candidates, and replace
        repl = find_replacement_candidates(sewers, miles, date)
        sewers = apply_replacements(sewers, repl, date)

        #snapshots.update({date:repl}) #hold on to snapshots of each year
        avg_age_replaced = sru.average_sewer_age(repl, datetime(date,1,1))
        oldestreplaced = repl.Year.min()

        #compute and record this year's results
        res = [date, avg_age, avg_rem_life, avg_age_replaced, riskymiles, riskyfraction]
        results_df = results_df.append(pd.DataFrame(columns = res_columns, data = [res]))

        #increment the year that is currently being modeled and age each sewer segment
        date += 1
        sewers['RemainingLife'] = sewers['RemainingLife'] - 1
        cumulative_miles += repl.Length.sum() / 5280.0


    #compute the rate of aging (of the weighted average age of whole system)
    results_df['AgeRate'] = results_df['AvgAge'].diff()
    if results_dir:
        excelwriter.save()
    if return_snapshot:
        return sewers
    else:
        return results_df.set_index('Year')


def remaining_life_span(asset, replacement_year):

    lifespan = defs.lifespans.get(asset.Material, 150) #assume 150 if not found
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

        asset.Material = 'NEWConcrete'
        asset.RemainingLife = defs.lifespans[asset.Material]
        asset.Year = replacement_year
        asset.LinerDate = None
        asset.MonthDay_Installed = '1_1'
        return asset

    #data will now reflect a new asset (new install date, modern material, etc)
    replaced_assets = replaced_sewers.apply(lambda x: replace_asset(x, replacement_year), axis=1)

    #drops assets from original data set based on the index (OBJECTID)
    #then appends the new assets
    sewers_with_replacements = orig_sewers.drop(replaced_assets.index).append(replaced_assets)


    return sewers_with_replacements

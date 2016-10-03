import pandas as pd
from datetime import datetime
import defs

def read_data(filepath=r'C:\Data\Code\SewerReport\data\sewers_active.csv',
                dbconnection=None, sql_query=None, group_materials=True,
                unique_id_col = 'OBJECTID'):
    """
    convenience function for reading an sql query or csv into dataframe. Note,
    group_materials changes the data labels according to defs.cohortmap
    """
    if dbconnection and sql_query:
        #access the database directly
        sewers = pd.read_sql_query(sql_query, dbconnection, index_col=unique_id_col)
    else:
        sewers = pd.read_csv(filepath) #local csv data

    if group_materials:
        group_materials_from_abbreviations(sewers)

    return sewers

def group_materials_from_abbreviations(sewerdf, cohortmap=defs.cohortmap):

    #first check to see if we should add materials not in my list
    #should not add anything if we've comprehensively defined everything
    uniqs = sewerdf.Material.unique()
    definedcohorts = [item for sublist in [x['abbrevs'] for x in cohortmap] for item in sublist]
    undefined = filter(None, set(uniqs) - set(definedcohorts)) #should be none
    othercohorts = [{'material':x, 'abbrevs':x} for x in undefined] #ones i missed (should be none)
    cohortmap += othercohorts
    cohortorder = [k['material'] for k in cohortmap]

    #cohortmap.append(othercohorts)
    for cohort in cohortmap:
        #groups the cohort abbrevations with clear names
        sewerdf.Material.replace(cohort['abbrevs'], cohort['material'], inplace=True)

def average_sewer_age(sewerdf, snapshot_date=None):
    """
    caculates the length-weighted average age of the assets in the input dataset.
    Snapshot dates allows the returned age to be at a given point in time.
    """
    if not snapshot_date:
        snapshot_date = datetime.now()

    #subset the dataframe to the snapshot date
    subset_sewers = sewerdf.loc[(sewerdf.Year <= snapshot_date.year)]
    #subset_sewers = sewerdf.loc[(sewerdf.index <= snapshot_date.year)]
    subset_length = subset_sewers['Length'].sum()
    if subset_length > 0:
        subset_ages = snapshot_date.year - subset_sewers.Year
        weighted_avg = (subset_ages * subset_sewers.Length).sum() / subset_length

        return weighted_avg

    else:
        return 0


def annual_asset_investment(sewerdf, decade=False, drange=[1820, 2020],
                            indexcol='Year', cohort_col='Material'):
    """
    the takes the entire asset data set and returns the total mileage per install year
    (or whatever the indexcol param is set to), with seprate columns for each cohort.
    """

    if len(sewerdf.index) == 0:
        return None

    sewers = sewerdf[[indexcol, cohort_col, 'Length']]

    #split the data into a table with cols for each material
    #index = Year and aggfunc = sum aggregates sewer length per year
    df = sewers.pivot_table(index=[indexcol], columns=cohort_col,
                                            aggfunc= lambda x: sum(x))
    #remove the multi-level 'header?', or something
    df.columns = df.columns.droplevel()
    df = df.fillna(0) #so things add properly
    df = df.loc[(df.index >= drange[0]) & (df.index <= drange[1])]
    #reorders the cohorts to desired, list comp handles subsets of cohorts
    df = df[[c for c in defs.cohortorder if c in df.columns]]

    if decade:
        #aggregate the data into totals per decade
        df = df.groupby((df.index//10)*10).sum()

    output = (df/5280)#.round(3) #convert to miles, round to 0.1

    return  output



def sewer_age_deriv(sewerdf, startyear=1990, endyear = None):

    if not endyear:
        endyear = datetime.now().year

    yearlist = list(range(startyear-1, endyear+1))
    d = {'Year':yearlist, 'Age':None}
    years = pd.DataFrame(d)
    years['Age'] = years.apply(lambda x: average_sewer_age(sewerdf, datetime(x['Year'], 1, 1)), axis=1)
    years['AgeRate'] = years['Age'].diff().round(2).fillna(0)
    years['Age'] = years['Age'].round(1)
    return years.loc[years.Year > startyear-1]

def sewer_age_overtime(sewerdf, since=1990):
    #return a list with average age per year of a given pipe cohort

    #returns major cohorts miles per year
    yearlist = list(range(since, datetime.now().year+1))
    d = {'Year':yearlist, 'Age':None}
    years = pd.DataFrame(d)
    years['Age'] = years.apply(lambda x: average_sewer_age(sewerdf, datetime(x['Year'], 1, 1)), axis=1)
    years['AgeRate'] = years['Age'].diff().round(2).fillna(0)
    years['Age'] = years['Age'].round(1)

    return years

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

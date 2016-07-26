#sewer report utils
#sys.path.append(r'C:\Data\Code\SewerReport\python')
from flask import url_for
import pandas as pd
import numpy as np
import pygal
from pygal.style import Style
from datetime import datetime
from datetime import timedelta
APPLICATION_ROOT = "http://127.0.0.1:5000"
#constaints
cohortmap = [
    {'material':'Brick', 'abbrevs':['BMP'], 'lifespan':150, 'stand_dev':10},
    {'material':'Concrete', 'abbrevs':['RCP', 'RCPP', 'CC', 'PCC'], 'lifespan':150, 'stand_dev':10},
    {'material':'Clay', 'abbrevs':['VCP','TCP'], 'lifespan':150, 'stand_dev':10},
    {'material':'Metal', 'abbrevs':['CI', 'CMP', 'DI', 'STL'], 'lifespan':150, 'stand_dev':10},
    {'material':'Polymer', 'abbrevs':['PPVC', 'PVC', 'HDPE'], 'lifespan':150, 'stand_dev':10},
    {'material':'Unkown/Other', 'abbrevs':['UNK','WD', 'POR'], 'lifespan':150, 'stand_dev':10},
    #{'material':'Other', 'abbrevs':['WD', 'POR']},
]






cohortorder = [k['material'] for k in cohortmap] #control of cohorts for graphics
def read_data(filepath=r'C:\Data\Code\SewerReport\data\sewers_active.csv',
                dbconnection=None, sql_query=None, group_materials=True):

    if dbconnection and sql_query:
        #access the database directly
        sewers = pd.read_sql_query(sql_query, dbconnection)
    else:
        sewers = pd.read_csv(filepath) #local csv data

    if group_materials:
        group_materials_from_abbreviations(sewers)

    return sewers

def group_materials_from_abbreviations(sewerdf, cohortmap=cohortmap):

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

#CURRENT GOAL - Trends: show age of subsets of pipe cohorts, flask url variable

def material_type_barchart (sewerdf, chart_title=None, plot=False):
    if len(sewerdf.index) == 0:
        return None

    df = sewerdf[['Length',  'Material']]
    #df = df.pivot_table(index=['Material'], columns='PIPE_TYPE',
    #                                        aggfunc= lambda x: sum(x)/5280)
    df = df.groupby('Material').sum()/5280
    #df.columns = df.columns.droplevel()
    df = df.fillna(0)

    return barchart(df, title=chart_title, x_labels=None)

def annual_sewer_investment(sewerdf, chart_title=None, decade=False,
                            html=False, plot=False, drange=[1820, 2020],
                            indexcol='Year'):
    #aggregates milage per year

    if len(sewerdf.index) == 0:
        return None

    sewers = sewerdf[[indexcol, 'Material', 'Length']]

    #split the data into a table with cols for each material
    #index = Year and aggfunc = sum aggregates sewer length per year
    df = sewers.pivot_table(index=[indexcol], columns='Material',
                                            aggfunc= lambda x: sum(x))
    #remove the multi-level 'header?', or something
    df.columns = df.columns.droplevel()
    df = df.fillna(0) #so things add properly
    df = df.loc[(df.index >= drange[0]) & (df.index <= drange[1])]
    #reorders the cohorts to desired, list comp handles subsets of cohorts
    df = df[[c for c in cohortorder if c in df.columns]]

    if decade:
        #aggregate the data into totals per decade
        df = df.groupby((df.index//10)*10).sum()

    output = (df/5280)#.round(3) #convert to miles, round to 0.1

    if html:
        output = output.to_html()
    elif plot:

        #create pygal stacked bar chart
        bar_chart = pygal.StackedBar(width=800, height=500,
                      legend_at_bottom=True, human_readable=True,
                      title=chart_title,
                      y_title='Sewer Miles'
                      )

        #clean up the x labels to be strings, and shorten format if numerous
        if decade:
            bar_chart.x_labels = [str(int(x)) for x in output.index]
        else:
            #truncats to the 10s year (e.g. '87, '99)
            bar_chart.x_labels = ["'" + str(int(x))[2:] for x in output.index]

        #populate the chart data
        for cohort in output:
            title = {
                    'title':cohort,
                    'xlink':{
                        'href':APPLICATION_ROOT + url_for('historical', cohort=cohort),
                        'target': '_top'
                        }
                    }

            bar_chart.add(title, output[cohort])
            bar_chart.value_formatter =  lambda x:"%.3f" % x if x < 1 else "%.1f" % x

        output = bar_chart.render_data_uri()
    return  output#convert to miles
    #return sewers.groupby('Year').sum()/5280

def barchart(df, title=None, x_labels=None, y_title = 'Sewer Miles', print_values=False, label=True ):

    bar_chart = pygal.Bar(width=800, height=500,
                  legend_at_bottom=True, human_readable=True,
                  title=title,
                  y_title='Sewer Miles',
                  x_labels = x_labels,
                  print_values=print_values
                  )

    for item, data in df.iterrows():
        bar_chart.add(item, data)
        #format numbers less than 1 to have more decimals
        bar_chart.value_formatter =  lambda x:"%.3f" % x if x < 1 else "%.1f" % x

    return bar_chart.render_data_uri()

def piechart(df, title=None, print_values=True, label=True):
    piechart = pygal.Bar(title=title, print_values=print_values, print_labels=label)
    for cohort, data in df.iterrows():
        piechart.add(cohort, data)
        piechart.value_formatter =  lambda x:"%.3f" % x if x < 1 else "%.0f" % x

    return piechart.render_data_uri()

def sewer_distribution(sewerdf, plot=True):

    #create a pie chart with total milage per cohort
    sewers = sewerdf[['Material', 'Length']].dropna()
    totals_df = (sewers.groupby('Material').sum()/5280)#.round(1)
    output = totals_df.reindex(cohortorder)

    if plot:
        output = piechart(output, 'Active Sewer Distribution by Material (miles)')

    return output

def liner_distribution(sewerdf, plot=True):

    #create a pie chart with total milage per cohort of sewer lined
    liners = sewerdf[["Length", "Material", "LinerDate"]].dropna() #remove non lined
    liners  = liners[["Length", "Material"]].dropna()
    totals_df = (liners.groupby('Material').sum()/5280)#.round(1)#group_materials(liners)

    output = totals_df
    if plot:
        output = piechart(totals_df, 'Sewer Lining Distribution by Lined Material (miles)')

    return output

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

    #yearseries =

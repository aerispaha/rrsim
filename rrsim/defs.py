

#MAP OF COHORT abbrevations FROM THE DATABASE
cohortmap = [
    {'material':'Brick', 'abbrevs':['BMP'], 'lifespan':150, 'stand_dev':10},
    {'material':'Concrete', 'abbrevs':['RCP', 'RCPP', 'CC', 'PCC'], 'lifespan':150, 'stand_dev':10},
    {'material':'Clay', 'abbrevs':['VCP','TCP'], 'lifespan':150, 'stand_dev':10},
    {'material':'Metal', 'abbrevs':['CI', 'CMP', 'DI', 'STL'], 'lifespan':150, 'stand_dev':10},
    {'material':'Polymer', 'abbrevs':['PPVC', 'PVC', 'HDPE'], 'lifespan':150, 'stand_dev':10},
    {'material':'Unkown/Other', 'abbrevs':['UNK','WD', 'POR'], 'lifespan':150, 'stand_dev':10},
    #{'material':'Other', 'abbrevs':['WD', 'POR']},
]
cohortorder = [k['material'] for k in cohortmap] #control of cohorts order for graphics

lifespans = {'Brick':150, 'Concrete':150, 'Clay':150, 'Metal':150, 'Polymer':150, 'Unkown/Other':150, 'NEWConcrete':150}
lifespan_std = {'Brick':10, 'Concrete':10, 'Clay':10, 'Metal':10, 'Polymer':10, 'Unkown/Other':10}

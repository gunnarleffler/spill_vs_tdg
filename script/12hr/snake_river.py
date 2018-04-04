# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 12:01:06 2018

@author: G0PDWJPT
"""

import pandas as pd
from collections import OrderedDict
from datetime import datetime, timedelta
from get_avgs import washington_method
import numpy as np
from cwms_read.cwms_read import get_cwms
now = datetime.now() + timedelta(hours = 8)
#start_date = (2017, 6, 1)
#end_date = (2017, 8, 2)
start_date = (2018, 4, 1)
end_date = (now.year, now. month, now.day-1)
start_index = '-'.join([str(x) for x in start_date])

tuples = [
    
    ('Lower Granite', 'Spill Cap', 'Starting → Change', 'kcfs'),
    ('Lower Granite', 'Actual Spill', 'Daily Average', 'kcfs'),
    ('Lower Granite', 'TW', 'LGNW', '% sat' ),
    ('Lower Granite', 'd/s FB', 'LGSA', '% sat'),
    
    ('Little Goose', 'Spill Cap', 'Starting → Change', 'kcfs'),
    ('Little Goose', 'Actual Spill', 'Daily Average', 'kcfs'),
    ('Little Goose', 'TW', 'LGSW', '% sat' ),
    ('Little Goose', 'd/s FB', 'LMNA', '% sat'),
    
    ('Lower Monumental', 'Spill Cap', 'Starting → Change', 'kcfs'),
    ('Lower Monumental', 'Actual Spill', 'Daily Average', 'kcfs'),
    ('Lower Monumental', 'TW', 'LMNW', '% sat' ),
    ('Lower Monumental', 'd/s FB', ' IHRA ', '% sat'),
    
    ('Ice Harbor', 'Spill Cap', 'Starting → Change', 'kcfs'),
    ('Ice Harbor', 'Actual Spill', 'Daily Average', 'kcfs'),
    ('Ice Harbor', 'TW', 'IDSW', '% sat' ),
    ('Ice Harbor', 'Pasco', 'PAQW', '% sat' ),
    ('Ice Harbor', 'd/s FB', 'MCNA', '% sat'),
]

columns = pd.MultiIndex.from_tuples(tuples, names = ['Project','','','units'])

paths = [
    
        'LWG.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB', 
        'LWG.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',
        'LGNW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        'LGSA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        
        'LGS.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB', 
        'LGS.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',
        'LGSW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        'LMNA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
         
        'LMN.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB', 
        'LMN.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',
        'LMNW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        'IHRA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
    
        'IHR.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB', 
        'IHR.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',
        'IDSW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        'PAQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV',
        'MCNA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-WAmethod-REV',
        
        ]


index = pd.date_range(start='-'.join([str(x) for x in start_date]), end='-'.join([str(x) for x in end_date]),  freq='D', name='date')
df = pd.DataFrame(columns = columns, data = np.nan, index = index)
meta = {}
for path, column in zip(paths, tuples):
    data = get_cwms(path, start_date = start_date, end_date = end_date, public = True, fill = False)
    if isinstance(data,pd.DataFrame):
        meta.update(data.__dict__['metadata'])
        data = data.groupby(pd.Grouper(freq = 'D')).mean()
        df[column] = data.iloc[:,0]
    else: continue
df = df.round(0)


"""
Questionable data is defined as values that are missing 1/3 or more data for calculation


"""



column_dict = {
                'LGNW': ('Lower Granite','TW'),
                'LGSA': ('Lower Granite', 'd/s FB'),
                'LGSW': ('Little Goose', 'TW'),
                'LMNA': ('Little Goose', 'd/s FB'),
                'LMNW': ('Lower Monumental', 'TW'), 
                'IHRA': ('Lower Monumental', 'd/s FB'),
                'IDSW': ('Ice Harbor', 'TW'),
                'PAQW': ('Ice Harbor','Pasco'),
                'MCNA': ('Ice Harbor', 'd/s FB'),
              }


site_list = list(column_dict.keys())
path = '.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV '
site_list = [x+path for x in site_list]
questionable = pd.DataFrame(index = df.index, columns = df.columns, data = False)
wash_start = datetime(*start_date) - timedelta(days = 10)
wash_start = (wash_start.year, wash_start.month, wash_start.day)
wash_end = (end_date[0], end_date[1], end_date[2] +1)
for key, value in column_dict.items():
    p = key+path
    data = get_cwms(p, start_date=wash_start, end_date=wash_end, public = True, fill = False)
    if isinstance(data, pd.DataFrame):
        series = data.iloc[:,0]
        wash = series.pipe(washington_method)
        wash.index = [x.replace(hour = 0, minute = 0, second = 0) for x in wash.index]
        wash.index.name = 'date'
        wash = wash.loc[df.index]
        quality = wash['wa_quality'] != True
        questionable[value] = quality 
        
        
        
"""
Get the meta dictionary keys match the column names so can be used below

"""

paths.insert(-1,'PAQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-RAW')
p = []
for path in paths:
    column_name = '_'.join(path.split('.')[:2])
    column_name = '_'.join(column_name.split('-'))
    p.append(column_name)
    
meta_col_dict = {key:value for key,value in zip(p, list(df.columns))}
temp_meta = {}
for key, value in meta.items():
    
    try:
        temp_meta.update({meta_col_dict[key]: value})
    except KeyError:
        continue
        
meta.update(temp_meta)




"""
Lack of Load or involuntary spill: 6 hours of 24 hours that the project is spilling above the voluntary spill cap
This will be the asteriks on the actual spill columns



From the urban dictionary: asteriks
Incorrect pronounciation of the word 'asterisk'. Use of the word 'asteriks' is a result of the USA's substandard education system.
Jim: Hey Lou, what's that star thingy called that you get from pressing SHIFT + 8? 

Lou: an asteriks 

Jim: Aha! I knew you were a dumbass.


"""
site_dict = OrderedDict([
            ('Lower Granite',['LWG']),
            ('Little Goose',['LGS']),
            ('Lower Monumental', ['LMN']),
            ('Ice Harbor', ['IHR'])
          ])

column_dict = {
    'LWG': 'Lower Granite',
    'LGS': 'Little Goose',
    'LMN': 'Lower Monumental',
    'IHR': 'Ice Harbor'
    
}

# Collecting the daily spill caps to compare against the hourly spill
site_list = list(sum(site_dict.values(), []))
spill_cap_path = '.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'
spill_cap_list = [x+spill_cap_path for x in site_list]

spill_cap = get_cwms(spill_cap_list, public = True, fill = False, start_date=start_date, end_date=end_date, timezone = 'PST')
if isinstance(spill_cap, pd.DataFrame):
    spill_cap.columns = [x.split('_')[0] for x in spill_cap.columns]
    spill_cap.rename(columns = column_dict, inplace = True)


    # Collecting the hourly spill to compare against the daily spill caps
    spill_path = '.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'
    spill_list = [x+spill_path for x in site_list]

    spill = get_cwms(spill_list, public = True, start_date=start_date, end_date=end_date, timezone = 'PST', fill = False)
    spill.columns = [x.split('_')[0] for x in spill.columns]
    spill.rename(columns = column_dict, inplace = True)

    # Group the data by day to check if the project was in involuntary spill
    sg = spill.groupby(pd.Grouper(level='date', freq='D'))
    scg = spill_cap.groupby(pd.Grouper(level='date', freq='D')).mean().groupby(pd.Grouper(level='date', freq='D'))
    date = list(scg.groups.keys())
    inv_spill = pd.DataFrame(index = date, columns = spill.columns)
    for group, value in scg:
        g = sg.get_group(group)
        s = value.iloc[0]
        inv_spill.loc[group] = g.apply(lambda x: x.gt(s), axis = 1).sum()>5

    """
    Create boolean df for asterik
    """    


    projects = list(set(df.columns.get_level_values(0).tolist()))
    inv_spill_bool = pd.DataFrame(data = False,index = df.index, columns = df.columns)
    for project in projects:
        inv_spill_bool.loc[:,(project, 'Actual Spill')] = inv_spill[project]

    inv_spill_bool.fillna(value = False, inplace = True)
else: inv_spill_bool = False

"""
Minimum Generation: at least 6 hours of 24 that the project is at minimum generation
This will be the green on the actual spill columns
"""
min_gen_dict_kcfs = OrderedDict([
            ('Lower Granite',13.2),
            ('Little Goose',12.0),
            ('Lower Monumental', 12.5),
            ('Ice Harbor', 10.0)
          ])

min_gen_kcfs = pd.Series(min_gen_dict_kcfs)

# Collecting the daily generation flow to compare against the minimum generation flow, group by day
site_list = list(sum(site_dict.values(), []))
gen_flow_path = '.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'
gen_flow_list = [x+gen_flow_path for x in site_list]
gen_flow = get_cwms(gen_flow_list, public = True, start_date=start_date, end_date=end_date, timezone = 'PST', fill = False)
gen_flow.columns = [x.split('_')[0] for x in gen_flow.columns]
gen_flow.rename(columns = column_dict, inplace = True)
gen_flow_grouped = gen_flow.groupby(pd.Grouper(level='date', freq='D'))
 
    
# Creat a df fill with min gen data as dummy data
date = list(gen_flow_grouped.groups.keys())
min_gen = pd.DataFrame(index = date)
for key, value in min_gen_kcfs.items():
    min_gen[key] = value

#check if proj in min generation for the day and fill min_gen with result  
min_gen.index.rename('date', inplace = True)
min_gen_grouped = min_gen.groupby(pd.Grouper(level='date', freq='D'))
for group, value in gen_flow_grouped:
    min_gen.loc[group] = value.apply(lambda x: x <= min_gen_kcfs, axis = 1).sum()>5

"""
Create boolean df for css
"""    
    
    
projects = list(set(df.columns.get_level_values(0).tolist()))
min_gen_bool = pd.DataFrame(data = False,index = df.index, columns = df.columns)
for project in projects:
    min_gen_bool.loc[:,(project, 'Actual Spill')] = min_gen[project]


"""
Not Meeting TDG Gas Cap Tailwater: defined as combined OR WA value > 120.5
Not Meeting TDG Gas Cap Forebay: defined as combined OR WA value > 115.5
This will be the blue on the TW and downstream forebay columns
"""
idx = pd.IndexSlice
gas_cap_exceeds = df.copy()
tw = gas_cap_exceeds.sort_index(axis = 1).loc[:,pd.IndexSlice[:,'TW']]
fb = gas_cap_exceeds.sort_index(axis = 1).loc[:,pd.IndexSlice[:,'d/s FB']]
gas_cap_exceeds[tw.columns] = tw.applymap(lambda x: x > 120.5)
gas_cap_exceeds[fb.columns] = fb.applymap(lambda x: x > 115.5)
gas_cap_exceeds = gas_cap_exceeds.sort_index(axis=1)[df.columns]
gas_cap_exceeds = gas_cap_exceeds.applymap(lambda x: x if type(x) == bool else False)
gas_cap_exceeds.head()

"""
Combine gas cap by project: If true in one gauge, true for all project, except Ice Harbor special case
"""

gas_cap_by_gauge =  pd.DataFrame(data = False,index = gas_cap_exceeds.index, columns = gas_cap_exceeds.columns)
projects = list(set(df.columns.get_level_values(0).tolist()))
for project in projects:
    data = gas_cap_exceeds.loc[:,project].sort_index(axis=1).loc[idx[:,['TW', 'd/s FB']]]
    gas_cap_by_gauge.loc[:,(project, 'TW')] = data.apply(lambda x: x.any(),axis = 1)
    gas_cap_by_gauge.loc[:,(project, 'd/s FB')] = data.apply(lambda x: x.any(),axis = 1)
gas_cap_by_gauge['Ice Harbor'] = gas_cap_exceeds['Ice Harbor']


"""
Most restrictive gauge defined as:

Bold tailrace if:
(Tailrace TDG -120) > (ds Forebay -115)
Else:
Bold ds Forebay

Bold regardless of TDG value (above or below target).


This is the updated bold bold 

"""

idx = pd.IndexSlice
most_restrictive_gauge = df.copy()
tw = most_restrictive_gauge.sort_index(axis = 1).loc[:,pd.IndexSlice[:,'TW']]
fb = most_restrictive_gauge.sort_index(axis = 1).loc[:,pd.IndexSlice[:,'d/s FB']]



most_restrictive_gauge[tw.columns] = (tw - 120).values > (fb - 115).values
most_restrictive_gauge[fb.columns] = (tw - 120).values < (fb - 115).values


most_restrictive_gauge = most_restrictive_gauge.sort_index(axis=1)[df.columns]
most_restrictive_gauge = most_restrictive_gauge.applymap(lambda x: x if type(x) == bool else False)



"""
Convert the dataframe to string because it displays better, remove decimals, add the asterik, and format the index to be date only (no time), for all dataframes.  
If index not formated for all df's the styling will not work
"""

df_string = df.copy().round(0).astype(str).applymap(lambda x: x.replace('.0', ''))
if isinstance(inv_spill_bool, pd.DataFrame):
    df_string[inv_spill_bool] = df_string[inv_spill_bool] + '*'
df_string.replace('nan', '--', inplace = True)




spill_cap = df_string.sort_index(axis = 1).loc[:,pd.IndexSlice[:,'Spill Cap']].copy()
for column in spill_cap.columns:
    series = spill_cap[column]
    for index,value in enumerate(series[1:]):
        previous_value = series[index]
        if value != previous_value:
            df_string[column][index+1] = ('{}{}{}'.format(str(previous_value), '→', str(value)))




for dataframe in [df_string,gas_cap_by_gauge,min_gen_bool, most_restrictive_gauge, questionable]:
    dataframe.index = dataframe.index.strftime('%Y-%m-%d')



"""
Custom css
"""


def hover(hover_color="#ffff99"):
    return dict(selector="tbody tr:hover",
                props=[("background-color", "%s" % hover_color)])

styles = [
    
   
]




"""
table key
"""

blue = '#7194da'
green = '#cfff95'

def highlight(value):
    return table_css.applymap(lambda x: x)
key_list =[
            'Most restrictive gauge used to determine spill cap',
            'Project spilling above the voluntary spill cap for 6 or more hours',
            'At least one TDG value exceeds max limit',
            'Project operating at minimum generation for 6 or more hours',
            '1/3 of data or more missing for value calculation',
            'No data'
        ]
table_key = pd.DataFrame({'Table Key':key_list })                         
table_key.set_index('Table Key', inplace = True)
table_key['value']=['value','*','','','value', '--']
table_css = pd.DataFrame({'Table Key':key_list,'value':['font-weight: 900',\
                                                        '',\
                                                        'background-color: ' + blue,\
                                                        'background-color: '+ green, \
                                                        'color: red',
                                                        '']})
table_css.set_index('Table Key', inplace = True)
table_key.style.apply(highlight, axis = None)


hide_index = [{'selector': '.row_heading, .blank', 'props': [('display', 'none;')]}]
key_styles = styles # + hide_index
key_html = (table_key.style)
key_html.apply(highlight,axis = None).set_uuid('key')



"""
Adding table styles
"""

def tbl_css(value,css,df):
    return df.applymap(lambda x: css if x else '')

s = df_string.style

table_styles = styles + [hover()]

html = (
          s.set_table_styles(table_styles)
          .set_caption("Spill Cap changes occur at 16:00 PST.")
       )

html \
.apply(tbl_css, css = 'font-weight: 900', df = most_restrictive_gauge, axis = None) \
.apply(tbl_css, css = 'background-color: #7194da', df = gas_cap_by_gauge, axis = None) \
.apply(tbl_css, css = 'background-color: #cfff95', df = min_gen_bool, axis = None)\
.apply(tbl_css, css = 'color: red', df = questionable, axis = None) \
.set_uuid('data_table')

pd.DataFrame().style.set_table_styles(table_styles).set_uuid('header-fixed')

print(
html \
.apply(tbl_css, css = 'font-weight: 900', df = most_restrictive_gauge, axis = None) \
.apply(tbl_css, css = 'background-color: #7194da', df = gas_cap_by_gauge, axis = None) \
.apply(tbl_css, css = 'background-color: #cfff95', df = min_gen_bool, axis = None)\
.apply(tbl_css, css = 'color: red', df = questionable, axis = None) \
.set_uuid('data_table').render())

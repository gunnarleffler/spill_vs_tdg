#!/usr/bin/python3
# -*- coding: utf-8 -*-
helpstr = '''
get_avgs v1.0.0
2/20/2018
This program calculates the 12 hour averages in both the Oregon and Washington 
methods and also combines the two methods for the most restrictive of the two 
methods.
POC: Jeff Tilton
FORMATTING
==========
configuration file example
--------------------------
CHJ:
  path: GOES-COMPUTED
  methods:  ['or', 'wa', 'combined']
Output
------
Output of this program is timeseries data in "instapost" YAML format
PARAMETERS
==========
'''

import sys
import argparse
import json
import yaml
import pandas as pd
from cwms_read.cwms_read import get_cwms, reindex
from datetime import timedelta, datetime
import numpy as np
import math

def loadConfig(path, verbose = True):
  if verbose:
    sys.stderr.write("loading config file...")
  output = yaml.safe_load(open(path))
  if verbose:
    sys.stderr.write(" %d entries found.\n" % (len(output)))
  return output

def set_time_index(ts_index, hour_int = 0, minute_int = 0, second_int = 0):
    return [x.replace(hour = hour_int, minute = minute_int, second = second_int) for x in ts_index]

    
                
def oregon_method(series):
    """
    Args:
        df: a pd.core.DataFrame of percent TDG saturation
        
    Returns:
        orgn: The return value. the 12 hour average of TDG data as described below
        
    Oregon Method:
        The Oregon method computes an average using the highest 12 hours TDG 
        readings of the day, then stores it as a daily time series.  The 12 hours
        do not need to be consecutive.
        
        12 hour values that have 8 or more hours of missing hourly data are 
        flagged as questionable
    """
    
    orgn = series \
        .groupby(pd.Grouper(level='date', freq='D')) \
        .aggregate(lambda x: x.sort_values(ascending = False) \
        .reset_index(drop = True).iloc[:12].mean()) \
        .round(decimals = 2)
    #orgn.fillna(0,inplace = True)    
    
    
    high_quality = series \
                            .groupby(pd.Grouper(level='date', freq='D')) \
                            .aggregate(lambda x: pd.Series(x).dropna().count())>16
    
    
    #set time to 1200 PST in GMT
    for s in [orgn, high_quality]:
        s.index = set_time_index(s.index, hour_int = 20)
        s.index.name = 'date'
    
    result = pd.DataFrame(index = orgn.index)
    result['oregon'] = orgn
    result['orgn_quality'] = high_quality
    result.dropna(inplace = True)
    return result



def washington_method(series):
    """
    Args:
        df: a pd.core.DataFrame of percent TDG saturation
        
    Returns:
        wa_daily_max: The return value. the 12 hour average of TDG data as described below
        
    Washington Method:
        Use a rolling average to measure 12 consecutive hours. The highest 12 hour
        average in 24 hours is reported on the calendar day (ending at midnight) of the final
        measurement.
        - The first averaging period of each calendar day begins with the first
          hourly measurement at 1:00 a.m. This hour is averaged with the
          previous day’s last 11 hourly measurements.
        - Each subsequent hourly measure is averaged with the previous 11 hours
          until there are 24 averages for the day.
        - From the 24 hour averages, the highest average is reported for the
          calendar day.
        - Round 12 hour average to nearest whole number.
    
    individual values that have 4 or more hours of missing hourly data are flagged 
    as questionable
    

    """
    #subtracting 1 minute from the index so the 01:00 value is the first value of the day
    index = [pd.Timestamp(x) - timedelta(minutes=1)  for x in series.index.values]
    series.index = index
    series.index.name = 'date'
    roll = series.rolling(window = 12, min_periods = 1, axis = 0)      
    roll_mean = roll.mean()
    wa_daily_max = roll_mean. \
                            loc[roll_mean.groupby(pd.Grouper(level='date', freq='D')).idxmax()] \
                            .dropna() \
                            .round(decimals = 2)
    high_quality = roll.count() > 8
    high_quality = high_quality.loc[wa_daily_max.index]
    
    #set time to 1200 PST in GMT
    for s in [wa_daily_max, high_quality]:
        s.index = set_time_index(s.index, hour_int = 20)
        s.index.name = 'date'

    result = pd.DataFrame(index = wa_daily_max.index)
    result['washington'] = wa_daily_max
    result['wa_quality'] = high_quality
    result.index.name = 'date'
    result.dropna(inplace = True)
    return result 
    

def combine(orgn, wa, start_date, end_date):
    """

    Args:
        orgn: a pd.core.DataFrame of the 12 hour average of TDG data computed by 
              the oregon_method
              
        wa: a pd.core.DataFrame of the 12 hour average of TDG data computed by 
              the washington_method
    Returns:
        combined: The return value. the 12 hour average of TDG data as described below
        
    Combined Method:
        The Combined method takes the higher TDG average between the Oregon and 
        Washington methods and stores it as a daily time series.  If a value's
        quality is rated questionable and the other is not, the non-questionable 
        data is chosen regardless of which value is higher.
        
        

    """
    
    wa = wa.pipe(reindex, start_date, end_date, 'D')
    
    orgn = orgn.pipe(reindex, start_date, end_date, 'D')
  
    combined = orgn.join(wa)
    
    
    
    
    def get_value(or_value, or_quality, wa_value, wa_quality):
    
        if not or_quality and not wa_quality and not or_value and not wa_value:
            return np.nan
        if math.isnan(or_value) and math.isnan(wa_value):
            return np.nan
        if  or_quality and not wa_quality:
            return or_value
        elif wa_quality and not or_quality:
            return wa_value
        elif or_value > wa_value:
            return or_value
        else:
            return wa_value
    
    
    def get_quality(or_value, or_quality, wa_value, wa_quality):
    
        if not or_quality and not wa_quality and not or_value and not wa_value:
            return False
        if  or_quality and not wa_quality:
            return or_quality
        elif wa_quality and not or_quality:
            return wa_quality
        elif or_value > wa_value:
            return or_quality
        else:
            return wa_quality
    
    value = combined.apply(lambda x: get_value(x['oregon'], x['orgn_quality'], x['washington'], x['wa_quality']), axis = 1)
    quality = combined.apply(lambda x: get_quality(x['oregon'], x['orgn_quality'], x['washington'], x['wa_quality']), axis = 1)
    result = pd.DataFrame(index = combined.index)
    result['value'] = value
    result['quality'] = quality
    result.dropna(inplace = True)
    return result


def pd_df_to_instapost(value_df, pathname, units):
    """
    Args:
        series: a pd.core.Series time series with a time stamp index 
              
        pathname: pathname the data is to be stored at
        
        units: the units the data is in
        
        timezone: the timestamp timezone
        
    Returns:
        result: Dictionary in instapost format
    """
    result = {}
    
    
    timeseries_dict = {}
    
    for timestamp, value, quality in zip(value_df.index, value_df.iloc[:,0], value_df.iloc[:,1]):
        if math.isnan(value):
            continue
        loop_dict = {str(timestamp):
                            {'value':float(value)}
                    }
        if not quality:
            loop_dict[str(timestamp)].update({'qual':'QUESTIONABLE'})
        timeseries_dict.update(loop_dict)    
        
    result.update(
                        {pathname:{
                                    
                                    'units': units,
                                    'timezone':'GMT',
                                    'timeseries':timeseries_dict
                                    
                                    }
                                })
    return result


 #--------------------------------------------------------------------------------
# main()
#--------------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=helpstr, 
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('config', help='YAML formatted Configuration file')
    p.add_argument('-l', '--lookback', help='Lookback a number of days')
    p.add_argument('-v', '--verbose', action='store_true', help='Work verbosely')
    p.add_argument('-rj', '--rawJSON', action='store_true', help='Output JSON')
    args = p.parse_args()

    verbose = args.verbose
    rawJSON = args.rawJSON
    config = args.config
    
    
    
    if args.lookback:
        lookback = int(args.lookback) 
    else:
        lookback = 1
    now = datetime.now()
    
    #because the wa method is a rolling avg I want to lookback further than the
    #given lookback so I have enough data to calculate the desired date plus an overlap
    start = now - timedelta(days = lookback + 3)
    start_date = (start.year, start.month, start.day)
    index_start = now - timedelta(days = lookback + 1)
    index_start = '-'.join([str(index_start.year), str("%02d" % (index_start.month,)), str("%02d" % (index_start.day,))])
    end_date = (now.year, now.month, now.day)
    
    
    
    config_dict = loadConfig(config, verbose = verbose)
    
    
    #create the base pathname for each project.  The pathnames are not consistent
    #in the last section of the pathname.  This will also be done to both the 
    # raw and revised data so 2 separate pathname lists are made for each
    
    path = '.%-Saturation-TDG.Inst.1Hour.0.'
    paths = []
    for key, value in config_dict.items():
        path_end = value['path']
        paths.append('{}{}{}'.format(key, path, path_end))
    
    df = get_cwms(paths, lookback = lookback + 3, fill = True, public = True, timezone = 'PST')
    meta = df.__dict__['metadata']


    for column in df.columns:
        series = df[column].copy()
        units = meta[series.name]['units']
        new_pathname = '.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-'
        name = series.name.split('_')[0] 
        end_name = meta[series.name]['path'].split('-')[-1]
        oregon_pathname = '{}{}{}{}'.format(name, new_pathname, 'ORmethod-', end_name)
        washington_pathname = '{}{}{}{}'.format(name, new_pathname, 'WAmethod-', end_name)
        combined_pathname = '{}{}{}{}'.format(name, new_pathname, 'Combined-', end_name)
        orgn = series.pipe(oregon_method)
        wa = series.pipe(washington_method)
        combined = combine(orgn, wa, start_date = start_date, end_date = end_date)
        for data in [(combined, combined_pathname), (orgn, oregon_pathname), (wa, washington_pathname)]:
            dataframe,pathname = data
            dataframe = dataframe[index_start:]
            instapost = pd_df_to_instapost(dataframe, pathname, units)

            if rawJSON:print(json.dumps(instapost)+"\n---")
            else:print(yaml.dump(instapost))
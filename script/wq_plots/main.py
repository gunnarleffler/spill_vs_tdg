#!/usr/local/bin/python
# -*- coding: utf-8 -*-
helpstr = '''
get_ndfd v1.0.0
2/20/2018
This program creates html plots using the bokeh plotting library.
POC: Jeff Tilton
FORMATTING
==========
configuration file example
--------------------------
Lower Granite:
    flow:
        Total Flow:
            'LWG.Flow-Out.Ave.1Hour.1Hour.CBT-REV'
        Forecast Flow:
            'LWG.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'
        Spill:
            'LWG.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'
        Generation:
            'LWG.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'
        Spill Cap:
            'LWG.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB' 
    tdg:
        Upstream Forebay TDG:
            'LWG.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'
Output
------
html document
==========
'''

import yaml
from cwms_read.cwms_read import get_cwms
from datetime import datetime, timedelta
from checkbox import create_plot
from bokeh.layouts import layout
from bokeh.models import CheckboxGroup
from bokeh.io import curdoc
import pandas as pd
from theme import theme
from bokeh.models.widgets import Panel, Tabs
from bokeh.plotting import show, output_file, save
from collections import OrderedDict
import argparse, sys





def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# usage example:
#snake = ordered_load(open('snake.yml'), yaml.SafeLoader)

def create_tabs(config_file, title = '', start_date = (), end_date = (), verbose = True):
    if not start_date:
        lookback = 7
        now = datetime.now()
        start = now - timedelta(days = lookback)
        start_date  = (start.year, start.month, start.day)
        end_date = (now.year, now.month, now.day)
    dictionary = ordered_load(open(config_file), yaml.SafeLoader)
    units = yaml.safe_load(open('units.yml'))
    if not title: title = 'tabs'
    output_file(title +".html", title=title.replace('_', ' '))
    
    #get all the data for plots
    for key,value in dictionary.items():
        for k,v in value.items():
            for label, path in v.items():
                if verbose:
                    sys.stdout.write('\nCollecting %s\n' % path)
                df = get_cwms(path, start_date = start_date, end_date = end_date, fill = False)
                df.columns = [label]
                dictionary[key][k][label] = df
    #consolidate data to feed checkbox.py  
    for key,value in dictionary.items():
        for k,v in value.items():
            dictionary[key][k] = [ df for label, df in v.items()]
    #create all plots       
    for key,value in dictionary.items():
        for k,v in value.items():
            unit = units[k]
            if verbose:
                    sys.stdout.write('\nCreating %s plots.\n' % k)
            dictionary[key][k] = (create_plot(unit,dictionary[key][k]))
    #link the plots on the first plot so share the same x axis
    for key, value in dictionary.items():
        children = []
        link = []
        i=0
        for k,v in value.items():
            checkbox, p = v
            if i==0:
                link.append(p)
                i=1
            else:
                p.x_range = link[0].x_range
            count = 0
            # check to see how many lines are on the plot
            #it doesn't make sense to turn line off on single line
            #so will add a blank checkboxgroup instead
            for renderer in p.to_json(False)['renderers']:
                if renderer['type'] == 'GlyphRenderer':
                    count+=1
            if count<2: children.append([CheckboxGroup(width=200),p])
            else: children.append([checkbox, p])
        p = layout(children) 
        dictionary[key] =  p
    #create and save tabs as html doc
    tabs = []
    for k,v in dictionary.items():
        t = Panel(child = v, title = k)
        tabs.append(t)
    tabs = Tabs(tabs=tabs)
    doc = curdoc()
    doc.theme = theme
    doc.add_root(tabs)
    if verbose:
        sys.stdout.write('\nSaving html document')
    save(tabs)



if __name__ == "__main__":
    p = argparse.ArgumentParser(description=helpstr, 
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('config', help='YAML formatted Configuration file')
    p.add_argument('-t','--title', help='title for html document')
    p.add_argument('-v', '--verbose', action='store_true', help='Work verbosely')
    args = p.parse_args()
    
    if args.title:
        title = args.title
    else: 
        title = ''
    if args.verbose:
        verbose = args.verbose
    else: verbose = True
    
    config = args.config
    create_tabs(config, title = title, start_date = (), end_date = (), verbose = verbose)
    
    
    
    
    


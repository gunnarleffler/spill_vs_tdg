# -*- coding: utf-8 -*-


from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.models import CheckboxGroup, CustomJS
from bokeh.models import Legend, ColumnDataSource
import pandas as pd
from bokeh.models import HoverTool

def create_plot(units,df_list):
    tools = "pan,box_zoom,reset"
    p = figure(x_axis_type = 'datetime', tools = tools)
    p.toolbar.logo = None
    p.yaxis[0].ticker.desired_num_ticks = 4
    p.yaxis.axis_label = units
    props = dict(line_width=4, line_alpha=0.7, hover_line_alpha=1.0)
    colors = Category10[10]
    glyph_dict = {}
    labels = []
    active = []
    items = []
    sources = []
    names = 'abcdefghijklmnopqrstuvwxyz'
    callback_string = '{}.visible = {} in checkbox.active;'
    code_string = ''
    i = 0
    
    for df in df_list:
        legend = df.columns[0]
        series = df.iloc[:,0]
        labels.append(legend)
        x = series.index
        y = series.values.round(2)
        source =ColumnDataSource(data = {'x':x,'y':y, 'date': [str(x) for x in x]})
        sources.append(source)
        line = p.line('x', 'y', color=colors[i], hover_color = colors[i], source = sources[i], **props)
        items.append((legend, [line]))
        name = names[i]
        line.name = name
        code_string += callback_string.format(name, str(i))
        glyph_dict.update({name:line})
        active.append(i)
        i+=1
    l = Legend(items=items,location=(0, 0), orientation = 'horizontal',
               border_line_color = None)
    p.add_layout(l, 'below')
    hover = HoverTool(tooltips=[('date', '@date'),('value', '@y{0.2f}')])
    p.add_tools(hover)
    checkbox = CheckboxGroup(labels=labels, active=active, width=200)
    glyph_dict.update({'checkbox':checkbox})
    checkbox.callback = CustomJS.from_coffeescript(args=glyph_dict, code=code_string)
    return checkbox, p



#from bokeh.layouts import row
#
#c,p = create_plot('kcfs',df_list)
#r=row([c,p])
##doc = curdoc()
##doc.theme = theme
##doc.add_root(r)  
##
#show(r)
##
# -*- coding: utf-8 -*-
from bokeh.themes import Theme
theme = Theme(json={
    'attrs': {
        'Figure': {
            'background_fill_color': 'white',
            'border_fill_color': 'white',
            'outline_line_color': 'gray',
            'outline_line_width' : 1,
            'outline_line_alpha' : .75,
            'width':1500,
            'height':200,
            },
        'Axis': {
            'axis_line_color': "gray",
            'axis_label_text_color': "gray",
            'axis_label_standoff':30,
            'axis_label_text_font_size': '15pt',
            'axis_label_text_font_style': 'bold',
            'major_label_text_color': "gray",
            'major_label_text_font_size': '10pt',
            'major_label_text_font_style' : 'bold',
            'major_tick_line_color': None,
            'minor_tick_line_color': None,
            
            },
        
        }
    })



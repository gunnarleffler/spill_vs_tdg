#!/usr/bin/python3
from datetime import datetime, timedelta
import numpy as np
from bokeh.plotting import figure, output_file, save, ColumnDataSource, reset_output, show
from bokeh.models import HoverTool, Legend
from bokeh.layouts import column
import urllib.request, urllib.error, urllib.parse
from dateutil.parser import parse

#function to call webservice and return data
def get_data(url):
    try:
        data = urllib.request.urlopen(url).read()
    except urllib.error.HTTPError as e:
        print("HTTP error: %d" % e.code)
        data = False
    except urllib.error.URLError as e:
        print("Network error: %s" % e.reason.args[1])
        data = False
    return data

#function to take csv file from USACE and format into dictionary.
def format_USACE_to_dictionary(csv_input, delimitor = ',', min_threshold = -1e6, max_threshold = 1e6, print_errors = True):
    print(min_threshold, max_threshold)
    site_data_split = csv_input.splitlines()
    site_dict = {}
    header = site_data_split[0].split(delimitor)
    for row in site_data_split[1:]:
        line = row.split(delimitor)
        try:
            dt = parse(line[0], fuzzy=True)
        except ValueError:
            if print_errors == True:
                print('Invalid Date, row = ', row)
            continue
        try:
            meas = float(line[1])
        except:
            if print_errors == True:
                print('Invalid Result, row = ', row)
            continue
        if meas < min_threshold:
            site_dict[dt] = np.nan
        elif meas > max_threshold:
            site_dict[dt] = np.nan
        else:
            site_dict[dt] = meas
    return site_dict

#function to take a dictionary[dates] = result and format into two lists, sorted by date, for plotting.
def format_dict_date_to_list_for_plot(indict, ignore = [], print_errors = True):
    dates = list(indict.keys())
    dates.sort()
    new_dates = []
    meas = []
    for date in dates:
        try:
            result = float(indict[date])
            if result in ignore: continue #skips to next loop if value in ignore list
            meas.append(result)
            new_dates.append(date)
        except ValueError:
            if print_errors == True:
                print('Value Error, row = ', date, indict[date])
            continue
    return new_dates, meas

projects = ['LWG','LGS', 'LMN', 'IHR', 'MCN', 'JDA', 'TDA', 'BON']
#projects = ['LGS']

print('Start project operations and downstream TDG')
outdir = r'C:\spill_eval_local\\'
#outdir = r'../data/'
lag_days = 18
forecast_days = 6
now = datetime.now() + timedelta(1)
end = now.strftime("%m/%d/%Y")
past = now - timedelta(lag_days)
start = past.strftime("%m/%d/%Y")

SiteInfo = {}

SiteInfo['DWR'] = {'Qtotal':{'file':'DWR.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill':{'file':'DWR.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'TDG_ds_TW':{'file':'DWQI.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'PEKI.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'plot_title':'Dworshak'
                     }

SiteInfo['LWG'] = {'Qtotal':{'file':'LWG.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                    'Qtotal_fcst':{'file':'LWG.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'},\
                     'Qspill':{'file':'LWG.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'LWG.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'LWG.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'LWG.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'LGNW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'LGSA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'LGNW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'LGSA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'LGNW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'LWG.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'LGNW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'LGSA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'SILW.Speed-Wind.Inst.1Hour.0.USBR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'SILW.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'SILW.Temp-Air.Inst.1Hour.0.USBR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'SILW.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'Lower Granite'
                     }

SiteInfo['LGS'] = {'Qtotal':{'file':'LGS.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                    'Qtotal_fcst':{'file':'LGS.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'},\
                     'Qspill':{'file':'LGS.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'LGS.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'LGS.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'LGSA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'LGSW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'LMNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'LGSW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'LMNA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'LGSW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'LGSA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'LGSW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'LMNA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'LBRW.Speed-Wind.Inst.1Hour.0.USBR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'LBRW.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'LBRW.Temp-Air.Inst.1Hour.0.USBR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'LBRW.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'Little Goose'
                     }

SiteInfo['LMN'] = {'Qtotal':{'file':'LMN.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                    'Qtotal_fcst':{'file':'LMN.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'},\
                     'Qspill':{'file':'LMN.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'LMN.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'LMN.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'LMNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'LMNW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'IHRA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'LMNW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'IHRA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'LMNW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'LMNA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'LMNW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'IHRA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'PSCW.Speed-Wind.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'PSCW.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'PSCW.Temp-Air.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'PSCW.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'Lower Monumental'
                     }

SiteInfo['IHR'] = {'Qtotal':{'file':'IHR.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                    'Qtotal_fcst':{'file':'IHR.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'},\
                     'Qspill':{'file':'IHR.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'IHR.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'IHR.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'IHRA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'IDSW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'MCNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'IDSW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'MCNA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'IDSW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'IHRA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'IDSW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'MCNA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'PSCW.Speed-Wind.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'PSCW.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'PSCW.Temp-Air.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'PSCW.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'Ice Harbor'
                     }

SiteInfo['MCN'] = {'Qtotal':{'file':'MCN.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                    'Qtotal_fcst':{'file':'MCN.Flow-Out.Inst.~6Hours.0.MODEL-STP-FCST'},\
                     'Qspill':{'file':'MCN.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'MCN.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'MCN.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'MCNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'MCPW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'JDY.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'MCPW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'JDY.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'MCPW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'MCNA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'MCPW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'JDY.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'HERO.Speed-Wind.Ave.15Minutes.15Minutes.MIXED-REV'},\
                     'Wind_fcst':{'file':'HERO.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'HERO.Temp-Air.Inst.0.0.MIXED-REV'},\
                     'Temp_air_fcst':{'file':'HERO.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'McNary'
                     }

SiteInfo['JDA'] = {'Qtotal':{'file':'JDA.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qtotal_fcst':{'file':'JDA.Flow-In.Inst.~6Hours.0.RFC-FCST'},\
                     'Qspill':{'file':'JDA.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'JDA.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'JDA.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'JDY.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'JHAW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'TDA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'JHAW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'TDA.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'JHAW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'JDY.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'JHAW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'TDA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'DLS.Speed-Wind.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'DLS.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'DLS.Temp-Air.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'DLS.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'John Day'
                     }

SiteInfo['TDA'] = {'Qtotal':{'file':'TDA.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qtotal_fcst':{'file':'TDA.Flow-In.Inst.~6Hours.0.RFC-FCST'},\
                     'Qspill':{'file':'TDA.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'TDA.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'TDA.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
                     'TDG_us_FB':{'file':'TDA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'TDDO.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'BON.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'TDDO.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'TDG_ds_FB_12hr_c':{'file':'BON.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
                     'Pres_Air_ds_TW':{'file':'TDDO.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'TDA.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'TDDO.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'TDDO.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'DLS.Speed-Wind.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'DLS.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'DLS.Temp-Air.Inst.1Hour.0.METAR-COMPUTED-REV'},\
                     'Temp_air_fcst':{'file':'DLS.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'The Dalles'
                     }

SiteInfo['BON'] = {'Qtotal':{'file':'BON.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qtotal_fcst':{'file':'BON.Flow-In.Inst.~6Hours.0.RFC-FCST'},\
                     'Qspill':{'file':'BON.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qpower':{'file':'BON.Flow-Gen.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill_cap':{'file':'BON.Flow-Spill-Cap-Fish.Inst.~1Day.0.CENWDP-COMPUTED-PUB'},\
#                     'TDG_in1':{'file':'WRNO.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_us_FB':{'file':'BON.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'CCIW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
#                     'TDG_ds_FB':{'file':'CWMW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW_12hr_c':{'file':'CCIW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\
#                     'TDG_ds_FB_12hr_c':{'file':'CWMW.%-Saturation-TDG.Ave.~1Day.12Hours.CENWDP-COMPUTED-Combined-REV'},\                     
                     'Pres_Air_ds_TW':{'file':'CCIW.Pres-Air.Inst.1Hour.0.GOES-REV'},\
                     'Temp_us_FB':{'file':'BON.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_TW':{'file':'TDDO.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Temp_ds_FB':{'file':'CWMW.Temp-Water.Inst.1Hour.0.GOES-REV'},\
                     'Wind_obs':{'file':'BNDW.Speed-Wind.Inst.1Hour.0.USBR-COMPUTED-REV'},\
                     'Wind_fcst':{'file':'BNDW.Speed-Wind.Inst.~3Hours.0.NOAA-FCST'},\
                     'Temp_air_obs':{'file':'BNDW.Temp-Air.Inst.15Minutes.0.USBR-RAW'},\
                     'Temp_air_fcst':{'file':'BNDW.Temp-Air.Inst.~3Hours.0.NOAA-FCST'},\
                     'plot_title':'Bonneville'
                     }

SiteInfo['CHJ'] = {'Qtotal':{'file':'CHJ.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill':{'file':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'TDG_us_FB':{'file':'CHJ.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'CHQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'WEL.%-Saturation-TDG.Inst.1Hour.0.CBT-COMPUTED-RAW'},\
                     'plot_title':'Chief Joseph'
                     }


SiteInfo['GCL'] = {'Qtotal':{'file':'GCL.Flow-Out.Ave.1Hour.1Hour.CBT-REV'},\
                     'Qspill':{'file':'GCL.Flow-Spill.Ave.1Hour.1Hour.CBT-REV'},\
                     'TDG_us_FB':{'file':'FDRW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_TW':{'file':'GCGW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'TDG_ds_FB':{'file':'CHJ.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV'},\
                     'plot_title':'Grand Coulee'
                     }

plot_info = {'Qspill_percent':{'color':'black','style':'--', 'bokeh_style':'dotted', 'label':'spill (%)', 'lw':1},\
               'Qtotal':{'color':'red', 'style':'-', 'bokeh_style':'solid', 'label':'Total', 'lw':1},\
               'Qtotal_fcst':{'color':'red', 'style':':', 'bokeh_style':'dotted', 'label':'Total, forecast', 'lw':1},\
               'Qpower':{'color':'blue', 'style':'-', 'bokeh_style':'solid', 'label':'Powerhouse', 'lw':1},\
              'Qspill':{'color':'black', 'style':'-', 'bokeh_style':'solid', 'label':'Spill', 'lw':1},\
              'Qspill_cap':{'color':'black', 'style':':', 'bokeh_style':'dashed', 'label':'Spill Cap', 'lw':1},\
              'TDG_ds_TW':{'color':'DarkCyan','style':'-', 'bokeh_style':'solid','label':'TDG Tailwater', 'lw':1},\
              'TDG_ds_FB':{'color':'Indigo', 'style':'--', 'bokeh_style':'solid','label':'TDG d/s Forebay', 'lw':1},\
              'TDG_us_FB':{'color':'grey', 'style':':', 'bokeh_style':'solid','label':'TDG u/s Forebay', 'lw':1},\
              'TDG_in1':{'color':'green', 'style':':', 'bokeh_style':'dotted','label':'TDG inflow', 'lw':1},\
              'TDG_in2':{'color':'purple', 'style':':', 'bokeh_style':'dotted','label':'TDG inflow', 'lw':1},\
              'TDG115':{'color':'Indigo', 'style':'--', 'bokeh_style':'dotted','label':'Forebay Crit.', 'lw':2},\
              'TDG120':{'color':'DarkCyan', 'style':'--', 'bokeh_style':'dotted','label':'Tailrace Crit.', 'lw':2},\
              'TDG_ds_TW_12hr_c':{'color':'DarkCyan', 'style':'--', 'bokeh_style':'solid','label':'Tailrace Crit.', 'lw':4, 'alpha':0.33},\
              'TDG_ds_FB_12hr_c':{'color':'Indigo', 'style':'--', 'bokeh_style':'solid','label':'Tailrace Crit.', 'lw':4, 'alpha':0.25},\
              'Temp_ds_FB':{'color':'black', 'style':'-', 'bokeh_style':'solid','label':'d/s Forebay', 'lw':1},\
              'Temp_ds_TW':{'color':'red', 'style':'-', 'bokeh_style':'solid','label':'d/s Tailrace', 'lw':1},\
              'Temp_us_FB':{'color':'blue', 'style':'-', 'bokeh_style':'solid','label':'u/s Forebay', 'lw':1},\
              'Temp_air_obs':{'color':'green', 'style':'-', 'bokeh_style':'solid','label':'Air Temp., measured', 'lw':1},\
              'Temp_air_fcst':{'color':'green', 'style':':', 'bokeh_style':'dotted','label':'Air Temp., forecast', 'lw':1},\
              'Wind_obs':{'color':'purple', 'style':'-', 'bokeh_style':'solid','label':'Wind Speed, measured', 'lw':1},\
              'Wind_fcst':{'color':'purple', 'style':':', 'bokeh_style':'dotted','label':'Wind Speed, forecast', 'lw':1},\
              'Pres_Air_ds_TW':{'color':'purple', 'style':'-', 'bokeh_style':'solid','label':'Barometric Pressure', 'lw':1},\
            }
line_width=2

#Start generic
for site in projects:
    project = site
    plt_name = project + '_spill_TDG_TS'
    #Information needed to build a url for the web service
    #Things like data range and units are embedded and format (i.e. csv)
#    base_url1 = 'http://nwp-wmlocal2.nwp.usace.army.mil/common/web_service/webexec/csv?id='
    base_url1 = 'http://www.nwd-wc.usace.army.mil/dd/common/web_service/webexec/csv?id='
    data_dict = {}
    gage_dict = {}
    
    for flow_site in ['Qtotal', 'Qspill' , 'Qpower', 'Qspill_cap']:
        gage = SiteInfo[project][flow_site]['file']
        units = ':units=kcfs'
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start, end)
        site_data = get_data(url).decode()
        # gage_dict[gage][dt] = meas
        gage_dict[flow_site] = format_USACE_to_dictionary(site_data)
    
    for TDG_site in ['TDG_us_FB', 'TDG_ds_TW', 'TDG_ds_FB', 'TDG_in1', 'TDG_in2']:
        if TDG_site not in SiteInfo[project]: continue
        gage = SiteInfo[project][TDG_site]['file']
        units = ''
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start, end)
        site_data = get_data(url).decode()
        gage_dict[TDG_site] = format_USACE_to_dictionary(site_data)

    for TDG_site in ['TDG_ds_TW_12hr_c', 'TDG_ds_FB_12hr_c']:
        if TDG_site not in SiteInfo[project]: continue
        gage = SiteInfo[project][TDG_site]['file']
        units = ''
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start, end)
        site_data = get_data(url).decode()
        dict_aaa = format_USACE_to_dictionary(site_data)
        dict_bbb = {}
        for dt, value in dict_aaa.items():
            dt1 = datetime(dt.year, dt.month, dt.day, 0, 0)
            dt2 = datetime(dt.year, dt.month, dt.day, 23, 59)
            dict_bbb[dt1] = value
            dict_bbb[dt2] = value
        gage_dict[TDG_site] = dict_bbb
        
    for Temp_site in ['Temp_us_FB', 'Temp_ds_TW', 'Temp_ds_FB', 'Wind_obs', 'Pres_Air_ds_TW',  'Temp_air_obs']:
        if Temp_site not in SiteInfo[project]: continue
        gage = SiteInfo[project][Temp_site]['file']
        units = ''
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start, end)
        site_data = get_data(url).decode()
        gage_dict[Temp_site] = format_USACE_to_dictionary(site_data)
    for Fcst_site in ['Wind_fcst', 'Temp_air_fcst']:
        if Fcst_site not in SiteInfo[project]: continue
        gage = SiteInfo[project][Fcst_site]['file']
        units = ''
        now2 = datetime.now() + timedelta(-2)
        start2 = now2.strftime("%m/%d/%Y")
        end2 = (now + timedelta(forecast_days)).strftime("%m/%d/%Y")
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start2, end2)
        site_data = get_data(url).decode()
        #Need a plus 7 hour time adjustment on these forecasts
#        temp_dict = format_USACE_to_dictionary(site_data)
#        temp_dict2 = {}
#        for dt, value in temp_dict.items():
#            dt2 = dt + timedelta(hours=7)
#            temp_dict2[dt2] = value
#        gage_dict[Fcst_site] = temp_dict2        
        gage_dict[Fcst_site] = format_USACE_to_dictionary(site_data)
    for Fcst_site in ['Qtotal_fcst']:
        if Fcst_site not in SiteInfo[project]: continue
        gage = SiteInfo[project][Fcst_site]['file']
        units = ''
        now2 = datetime.now() + timedelta(-1)
        start2 = now2.strftime("%m/%d/%Y")
        end2 = (now + timedelta(forecast_days)).strftime("%m/%d/%Y")
        url = '%s%s%s&startdate=%s&enddate=%s&timezone=MST&headers=true' % (base_url1, gage, units, start2, end2)
        site_data = get_data(url).decode()
        gage_dict[Fcst_site] = format_USACE_to_dictionary(site_data)
    
    
    #Calculate percent spill
    gage_dict['Qspill_percent'] = {}
    for dt, spill in gage_dict['Qspill'].items():
        try:
            gage_dict['Qspill_percent'][dt] = spill/gage_dict['Qtotal'][dt]*100
        except:
            continue
    
    #format into lists for ploting
    gage_lists = {}
    for gage in gage_dict:
        gage_lists[gage] = {}
        gage_lists[gage]["dates"], gage_lists[gage]["meas"] = format_dict_date_to_list_for_plot(gage_dict[gage], print_errors = False)
        if gage == 'Qspill_cap':
            new_dates = []
            new_meas = []
            for i, date in enumerate(gage_lists[gage]["dates"]):
                if i+1 == len(gage_lists[gage]["dates"]):
                    new_dates += [date, date + timedelta(1)]
                    new_meas += [gage_lists[gage]["meas"][i], gage_lists[gage]["meas"][i]]
                    continue
                new_dates += [date, gage_lists[gage]["dates"][i+1]]
                new_meas += [gage_lists[gage]["meas"][i], gage_lists[gage]["meas"][i]]
            gage_lists[gage]["dates"], gage_lists[gage]["meas"] = new_dates, new_meas
        gage_lists[gage]["dates_bokeh_TZbug"] = [dt - timedelta(hours = 7) for dt in gage_lists[gage]["dates"]]
    
    start_dt = datetime.strptime(start, '%m/%d/%Y')
    end_dt = datetime.strptime(end, '%m/%d/%Y')
    
    ###########################################  BOKEH ###########################################################################
    #-------- bokey html plot------------------------------------
    # output to static HTML file
    output_file(outdir + plt_name + ".html", title = project + ' TDG ts')
    # create a new plot with a title and axis labels
    hover = HoverTool(
            tooltips=[
                ("index", "$index"),
                ("(x,y)", "($x, $y)"),
                ("desc", "@desc"),
            ]
        )
    TOOLS = 'box_zoom,box_select,reset,hover, pan'
    title1 = SiteInfo[project]['plot_title']
    s1 = figure(plot_width=900, plot_height=400, title=title1,  x_axis_type='datetime', x_axis_label=str(start_dt.year),
                y_axis_label='outlet flow (kcfs)', toolbar_location="above", tools = TOOLS, toolbar_sticky=False)
    s1.xgrid.grid_line_color = 'white'
    s1.ygrid.grid_line_color = 'white'
    
    myLegendList = []
    
    for gage in ['Qspill', 'Qspill_cap', 'Qtotal', 'Qpower', 'Qtotal_fcst']:
        if gage not in gage_lists: continue
        label_sting = plot_info[gage]['label']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s1.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = 1.0, line_dash = plot_info[gage]['bokeh_style'])
        myLegendList.append((label_sting,[l]))
        circle = s1.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)


    hover = s1.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    
    legend = Legend(items = myLegendList, location = (40,0))
    
    s1.add_layout(legend, 'above')
    s1.legend.orientation = "horizontal"
    
    #TDG plot
    dates = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    dates2 = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    gage_lists['TDG115'] = {'dates_bokeh_TZbug':dates2, 'meas':[115]*len(dates), 'dates' : dates}
    gage_lists['TDG120'] = {'dates_bokeh_TZbug':dates2, 'meas':[120]*len(dates), 'dates' : dates}
    myLegendList = []
    s2 = figure(plot_width=900, plot_height=400, x_range=s1.x_range, title=title1,  x_axis_type='datetime',
                x_axis_label=str(start_dt.year), y_axis_label='TDG (% saturation)', tools=TOOLS)
    s2.xgrid.grid_line_color = 'white'
    s2.ygrid.grid_line_color = 'white'
    for gage in ['TDG_us_FB', 'TDG_ds_TW', 'TDG_ds_FB', 'TDG_in1', 'TDG_in2', 'TDG115','TDG120']:
        if gage not in gage_lists: continue
        if gage in SiteInfo[project]:
            label_sting = SiteInfo[project][gage]['file'].split('.')[0] + ' '  + plot_info[gage]['label']
        else:
            label_sting = plot_info[gage]['label']
        if 'alpha' not in plot_info[gage]:
            alpha1 = 1.0
        else:
            alpha1 = plot_info[gage]['alpha']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s2.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = alpha1, line_dash = plot_info[gage]['bokeh_style'], line_width = plot_info[gage]['lw'])
        myLegendList.append((label_sting,[l]))
        circle = s2.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)
    hover = s2.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    legend = Legend(items = myLegendList, location = (40,0))
    s2.add_layout(legend, 'above')
    s2.legend.orientation = "horizontal"

    #Wind plot
    dates = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    dates2 = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    myLegendList = []
    s3 = figure(plot_width=900, plot_height=400, x_range=s1.x_range, title=title1,  x_axis_type='datetime',
                x_axis_label=str(start_dt.year), y_axis_label='Wind Speed (mph)', tools=TOOLS)
    s3.xgrid.grid_line_color = 'white'
    s3.ygrid.grid_line_color = 'white'
    
    for gage in ['Wind_obs', 'Wind_fcst']:
        if gage not in gage_lists: continue
        if gage in SiteInfo[project]:
            label_sting = SiteInfo[project][gage]['file'].split('.')[0] + ' '  + plot_info[gage]['label']
        else:
            label_sting = plot_info[gage]['label']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s3.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = 1.0, line_dash = plot_info[gage]['bokeh_style'], line_width = plot_info[gage]['lw'])
        myLegendList.append((label_sting,[l]))
        circle = s3.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)
    hover = s3.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    legend = Legend(items = myLegendList, location = (40,0))
    s3.add_layout(legend, 'above')
    s3.legend.orientation = "horizontal"

    #Temperature plot
    dates = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    dates2 = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    myLegendList = []
    s4 = figure(plot_width=900, plot_height=400, x_range=s1.x_range, title=title1,  x_axis_type='datetime',
                x_axis_label=str(start_dt.year), y_axis_label='Temperature (deg F)', tools=TOOLS)
    s4.xgrid.grid_line_color = 'white'
    s4.ygrid.grid_line_color = 'white'
    
    for gage in ['Temp_us_FB', 'Temp_ds_TW', 'Temp_ds_FB', 'Temp_air_obs', 'Temp_air_fcst']:
        if gage not in gage_lists: continue
        if gage in SiteInfo[project]:
            label_sting = SiteInfo[project][gage]['file'].split('.')[0] + ' '  + plot_info[gage]['label']
        else:
            label_sting = plot_info[gage]['label']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s4.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = 1.0, line_dash = plot_info[gage]['bokeh_style'], line_width = plot_info[gage]['lw'])
        myLegendList.append((label_sting,[l]))
        circle = s4.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)
    hover = s4.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    legend = Legend(items = myLegendList, location = (40,0))
    s4.add_layout(legend, 'above')
    s4.legend.orientation = "horizontal"

    #barometric plot
    dates = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    dates2 = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    myLegendList = []
    s5 = figure(plot_width=900, plot_height=400, x_range=s1.x_range, title=title1,  x_axis_type='datetime',
                x_axis_label=str(start_dt.year), y_axis_label='Barometric Pressure (mm-Hg)', tools=TOOLS)
    s5.xgrid.grid_line_color = 'white'
    s5.ygrid.grid_line_color = 'white'
    
    for gage in ['Pres_Air_ds_TW']:
        if gage not in gage_lists: continue
        if gage in SiteInfo[project]:
            label_sting = SiteInfo[project][gage]['file'].split('.')[0] + ' '  + plot_info[gage]['label']
        else:
            label_sting = plot_info[gage]['label']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s5.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = 1.0, line_dash = plot_info[gage]['bokeh_style'], line_width = plot_info[gage]['lw'])
        myLegendList.append((label_sting,[l]))
        circle = s5.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)
    hover = s5.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    legend = Legend(items = myLegendList, location = (40,0))
    s5.add_layout(legend, 'above')
    s5.legend.orientation = "horizontal"

    #TDG plot with 12 hour calc.
    dates = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    dates2 = gage_lists['Qtotal']["dates_bokeh_TZbug"]
    gage_lists['TDG115'] = {'dates_bokeh_TZbug':dates2, 'meas':[115]*len(dates), 'dates' : dates}
    gage_lists['TDG120'] = {'dates_bokeh_TZbug':dates2, 'meas':[120]*len(dates), 'dates' : dates}
    myLegendList = []
    s6 = figure(plot_width=900, plot_height=400, x_range=s1.x_range, title=title1,  x_axis_type='datetime',
                x_axis_label=str(start_dt.year), y_axis_label='TDG (% saturation)', tools=TOOLS)
    s6.xgrid.grid_line_color = 'white'
    s6.ygrid.grid_line_color = 'white'
    for gage in ['TDG_ds_TW', 'TDG_ds_FB', 'TDG115','TDG120','TDG_ds_TW_12hr_c','TDG_ds_FB_12hr_c' ]:
        if gage not in gage_lists: continue
        if gage in SiteInfo[project]:
            label_sting = SiteInfo[project][gage]['file'].split('.')[0] + ' '  + plot_info[gage]['label']
        else:
            label_sting = plot_info[gage]['label']
        if 'alpha' not in plot_info[gage]:
            alpha1 = 1.0
        else:
            alpha1 = plot_info[gage]['alpha']
        source = ColumnDataSource(data={
                    'dateX': gage_lists[gage]["dates_bokeh_TZbug"], # python datetime object as X axis
                    'v': gage_lists[gage]["meas"],
                    'site': [label_sting] * len(gage_lists[gage]["dates"]),
                    'dateX_str': [datetime.strftime(dt, '%m/%d %H:%M') for dt in gage_lists[gage]["dates"]], #string of datetime for display in tooltip
                })
        l = s6.line('dateX', 'v',source=source,color = plot_info[gage]['color'], alpha = alpha1, line_dash = plot_info[gage]['bokeh_style'], line_width = plot_info[gage]['lw'])
        myLegendList.append((label_sting,[l]))
        circle = s6.circle('dateX', 'v',source=source, size=6, color = plot_info[gage]['color'], alpha = 0.0)
    hover = s6.select(dict(type=HoverTool))
    hover.tooltips = [("site", "@site"), ("date", "@dateX_str"), ("value", "@v")]
    hover.mode = 'mouse'
    legend = Legend(items = myLegendList, location = (40,0))
    s6.add_layout(legend, 'above')
    s6.legend.orientation = "horizontal"


    p = column(s1, s2, s5, s3, s4, s6)
    
    # show the results
#    show(p)
    save(p)
    reset_output()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  2 10:26:58 2018

@author: G0PDWDFT
"""

import os
from datetime import datetime, timedelta
from cwms_read.cwms_read import get_cwms
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np

#network paths
outdir_V = outdir =  os.getcwd() + '/../data/'
indir = os.getcwd() + "/../config/"

#Dan's paths for testing
outdir_V = outdir =  os.getcwd() 
indir = r'F:\python_local\spill_vs_tdg\config\\'

file_out_base = 'daily_spill_v_tdg_2'

projects = ['BON_WRNO', 'TDA', 'JDA', 'MCN', 'IHR', 'LMN_uniform', 'LGS', 'LWG', 'GCL_DG', 'CHJ']
#projects = ['BON', 'TDA', 'JDA', 'MCN', 'IHR', 'LMN_uniform', 'LGS', 'LWG', 'GCL_DG', 'CHJ']
#projects = [ 'BON_WRNO']


now = datetime.now()
#now = datetime(2017,6,15)
then = now - timedelta(7)

end_dt = now + timedelta(1)
end = (end_dt.year, end_dt.month, end_dt.day+1)
start = (then.year, then.month, then.day)

then36hr = now - timedelta(1)
start36hr = (then36hr.year, then36hr.month, then36hr.day)

x_value = 'Qspill'
y_value = 'TDG_ds_TW'
TDG_goals = [110, 115, 116, 117, 118, 119, 120, 122, 125, 127, 130, 135]

surrogate_GC = {
        'LWG':118.1,
        'LGS':115.5,
        'LMN_bulk':118.1,
        'LMN_uniform':118.1,
        'IHR':118.9,
        'MCN':119.9,
        'JDA':118,
        'TDA':118,
        'BON':119.9,
        'BON_WRNO':119.9,
        'GCL_DG':117.2,
        'GCL_OT':117.2,
        'CHJ':119.9,
        'CHJ_WSBW':118,
        }


outlets = {}
outlets['BON'] = {
'e_tw':            {'CWMS':'BON.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'BON.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':    {'CWMS':'BON.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'BON.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'BON.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'WRNO.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'CCIW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'CWMW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['BON_WRNO'] = {
'e_tw':            {'CWMS':'BON.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'BON.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':    {'CWMS':'BON.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'BON.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'BON.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'WRNO.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'WRNO.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'CWMW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}

outlets['TDA'] = {
'e_tw':            {'CWMS':'TDA.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'TDA.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':    {'CWMS':'TDA.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'TDA.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'TDA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'TDDO.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'TDDO.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'BON.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}

outlets['JDA'] = {
'e_tw':            {'CWMS':'JDA.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'JDA.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':    {'CWMS':'JDA.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'JDA.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'JDY.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'JHAW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'JHAW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'TDA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['MCN'] = {
'e_tw':            {'CWMS':'MCN.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'MCN.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':    {'CWMS':'MCN.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'MCN.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'MCNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'IDSW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'MCPW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'JDY.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['IHR'] = {
'e_tw':{'CWMS':'IHR.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':{'CWMS':'IHR.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':{'CWMS':'IHR.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':{'CWMS':'IHR.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':{'CWMS':'IHRA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':{'CWMS':'IDSW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':{'CWMS':'IDSW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':   {'CWMS':'MCNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}

outlets['LMN'] = {
'e_tw':{'CWMS':'LMN.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':{'CWMS':'LMN.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':{'CWMS':'LMN.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':{'CWMS':'LMN.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':{'CWMS':'LMNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':{'CWMS':'LMNW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':{'CWMS':'LMNW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':{'CWMS':'IHRA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['LGS'] = {
'e_tw':           {'CWMS':'LGS.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':   {'CWMS':'LGS.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':   {'CWMS':'LGS.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':    {'CWMS':'LGS.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':      {'CWMS':'LGSA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':    {'CWMS':'LGSW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':      {'CWMS':'LGSW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':   {'CWMS':'LMNA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['LWG'] = {
'e_tw':           {'CWMS':'LWG.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':   {'CWMS':'LWG.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spilltotal':   {'CWMS':'LWG.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':    {'CWMS':'LWG.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':      {'CWMS':'LWG.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':    {'CWMS':'LGNW.Pres-Air.Inst.1Hour.0.GOES-REV', 'units':'mm-hg'},
'z3_tw_TDG':      {'CWMS':'LGNW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':      {'CWMS':'LGSA.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['GCL_DG'] = {
'e_tw':            {'CWMS':'GCL.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'e_fb':            {'CWMS':'GCL.Elev-Forebay.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'GCL.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spillbay_fake': {'CWMS':'GCL.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',  'units':'kcfs'},
'q_spilltotal':    {'CWMS':'GCL.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'GCL.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'FDRW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'CHQW.Pres-Air.Inst.1Hour.0.NWSRADIO-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'GCGW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'CHQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}
outlets['GCL_OT'] = {
'e_tw':            {'CWMS':'GCL.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'e_fb':            {'CWMS':'GCL.Elev-Forebay.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'GCL.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spillbay_fake': {'CWMS':'GCL.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',  'units':'kcfs'},
'q_spilltotal':    {'CWMS':'GCL.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'GCL.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'FDRW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'CHQW.Pres-Air.Inst.1Hour.0.NWSRADIO-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'GCGW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'CHQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
}

outlets['CHJ'] = {
'e_tw':            {'CWMS':'CHJ.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'CHJ.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spillbay_fake': {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',  'units':'kcfs'},
'q_spilltotal':    {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'CHJ.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'CHJ.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'CHQW.Pres-Air.Inst.1Hour.0.NWSRADIO-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'CHQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'WEL.%-Saturation-TDG.Inst.1Hour.0.CBT-COMPUTED-RAW', 'units':'%'},
}

outlets['CHJ'] = {
'e_tw':            {'CWMS':'CHJ.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'CHJ.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spillbay_fake': {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',  'units':'kcfs'},
'q_spilltotal':    {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'CHJ.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'CHJ.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'CHQW.Pres-Air.Inst.1Hour.0.NWSRADIO-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'CHQW.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'WEL.%-Saturation-TDG.Inst.1Hour.0.CBT-COMPUTED-RAW', 'units':'%'},
}

outlets['CHJ_WSBW'] = {
'e_tw':            {'CWMS':'CHJ.Elev-Tailwater.Inst.1Hour.0.CBT-REV', 'units':'ft'},
'q_powerhouse':    {'CWMS':'CHJ.Flow-Gen.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_spillbay_fake': {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV',  'units':'kcfs'},
'q_spilltotal':    {'CWMS':'CHJ.Flow-Spill.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'q_totalflow':     {'CWMS':'CHJ.Flow-Out.Ave.1Hour.1Hour.CBT-REV', 'units':'kcfs'},
'z0_fb_TDG':       {'CWMS':'CHJ.%-Saturation-TDG.Inst.1Hour.0.GOES-COMPUTED-REV', 'units':'%'},
'z1_Pres_Air':     {'CWMS':'WSBW.Pres-Air.Inst.1Hour.0.CBT-REV', 'units':'mm-hg'},
'z3_tw_TDG':       {'CWMS':'WSBW.%-Saturation-TDG.Inst.1Hour.0.CBT-COMPUTED-RAW', 'units':'%'},
'z4_ds_fb_TDG':    {'CWMS':'WEL.%-Saturation-TDG.Inst.1Hour.0.CBT-COMPUTED-RAW', 'units':'%'},
}


for project in projects:
#    TDG_goals += [surrogate_GC[project]]
    TDG_goals.sort()

    if 'LMN' in project:
        paths = [outlets['LMN']['q_spilltotal']['CWMS'], outlets['LMN']['z3_tw_TDG']['CWMS']]
    else:
        paths = [outlets[project]['q_spilltotal']['CWMS'], outlets[project]['z3_tw_TDG']['CWMS']]

#    if 'GCL' in project:
#        paths += [outlets[project]['e_fb']['CWMS']]

    df1 = get_cwms(paths, public = True, interval = 'hourly', start_date = start, end_date = end, timezone = 'PST')
    df1 = df1[df1>0].dropna()
    df1 = df1[(df1.iloc[:,1]<200)]

    df36hr = get_cwms(paths, public = True, interval = 'hourly', start_date = start36hr, end_date = end, timezone = 'PST')
    df36hr = df36hr[df36hr>0].dropna()
    df36hr = df36hr[(df36hr.iloc[:,1]<200)]


    #bulk_uni_threshold = 32
    #if 'bulk' in project:
    #    df1 = df1[(df1['LMN_Flow_Spill']<=bulk_uni_threshold)]
    #if 'uniform' in project:
    #    df1 = df1[(df1['LMN_Flow_Spill']>bulk_uni_threshold)]

#    if project == 'GCL_DG':
#        df1 = df1[(df1['GCL_Elev_Forebay']>=1266)]
#    if project == 'GCL_OT':
#        df1 = df1[(df1['GCL_Elev_Forebay']<1266)]

    fig, ax = plt.subplots(figsize=(6, 4))
    dt_string = '{d.month}/{d.day}'.format(d=then)  + '-' + '{d.month}/{d.day}'.format(d=now)
    ax.plot(df1.iloc[:,0], df1.iloc[:,1], label = dt_string, linestyle='None', marker='o', color = 'k', alpha =0.5, markersize=5)
    dt_string = '{d.month}/{d.day}'.format(d=then36hr)  + '-' + '{d.month}/{d.day}'.format(d=now)
    ax.plot(df36hr.iloc[:,0], df36hr.iloc[:,1], label = dt_string, linestyle='None', marker='o', color = 'r', alpha =0.66, markersize=5)
    lowess = sm.nonparametric.lowess(df1.iloc[:,1].tolist(), df1.iloc[:,0].tolist(), frac=0.66)
    ax.plot(lowess[:, 0], lowess[:, 1], label = '7d reg.', color = 'k')
    smooth_df = pd.DataFrame(lowess)

    if smooth_df.count().any()>0:
        x_lims = ax.get_xlim()
        y_lims = ax.get_ylim()


    #get 5-50-95th percentile smooth lines
    p = project
    if project == 'CHJ_WSBW':
        p = 'CHJ'
    hist_sm = pd.read_csv(indir + p + '_smoothed_P.csv')
    ax.fill_between(hist_sm['Unnamed: 0'], hist_sm['0.95'], hist_sm['0.05'], alpha = 0.33, label = '5-95th P')
    ax.plot(hist_sm['Unnamed: 0'], hist_sm['0.5'], color = 'b', label = '50th P')
#    if smooth_df.count().any()>0:
#        if x_lims[0] > 0:
#            x_lims = (0.0, x_lims[1])
#        if y_lims[0] > 100.0:
#            y_lims = (100.0, y_lims[1])
#        ax.set_xlim(x_lims)
#        ax.set_ylim(y_lims)
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    spill_table = 'Most recent:\n{d.month}/{d.day}/{d.year} {d.hour:02}{d.minute:02}\n'.format(d=df1.index.max())
    if smooth_df.count().any()==0:
        spill_table = 'no spill or\nno data:\n' + '{d.month}/{d.day}'.format(d=then)  + '-' + '{d.month}/{d.day}'.format(d=now)
    elif np.all(np.isnan(lowess[:,1])):
        spill_table = '7day regression\nfailed'
    else: 
#        smooth_df.count().any()>0:
        spill_table += '\n7day regress.\nTDG    Spill\n(sat)   (kcfs)\n'
        for tdg_level in TDG_goals:
            aaa = smooth_df.iloc[(smooth_df[1]-tdg_level).abs().argsort()[:1]]
            spill = aaa.iloc[0,0]
            if tdg_level > smooth_df[1].max():
                spill_txt = '>'+'%0.0f'%smooth_df[0].max()
            elif tdg_level < smooth_df[1].min():
                spill_txt = '<'+'%0.0f'%smooth_df[0].min()
            else:
                spill_txt = '%0.0f'%spill
            print(tdg_level, spill_txt)
            spill_table += str(tdg_level) + '%   ' + spill_txt + '\n'
    plt.text(1.02,0.5, spill_table, transform = ax.transAxes, verticalalignment='center')

    title1 = project

    #if 'LMN' in project:
    #    if 'bulk' in project:
    #        title1 += '(assumed <= '+ str(bulk_uni_threshold) + 'kcfs spill)'
    #    else:
    #        title1 += '(assumed > '+ str(bulk_uni_threshold) + 'kcfs spill)'
    plt.xlabel(df1.keys()[0] + ' (kcfs)')
    plt.ylabel(df1.keys()[1])
    plt.legend(bbox_to_anchor=(0.5, 1.2), ncol = 3, loc = 'upper center')
#    if not df1.count().any():
    title1 += ' {d.month}/{d.day}/{d.year} {d.hour:02}{d.minute:02}'.format(d=now)
    plt.title(title1, y=1.2)
    filname = outdir + project + '_'  + file_out_base + '.png'
    plt.gcf().subplots_adjust(top=0.8,right=0.8)
    plt.savefig(filname, dpi = 200)
    #os.startfile(filname)

# -*- coding: utf-8 -*-
"""
py-AppleHealth-Visualizer
Created on Sun Oct  9 00:46:10 2022

@author: mhejda
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
plt.style.use('bmh')

def Moving_Average(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def Nearest(dates, target):
    abs_deltas_from_target_date = np.absolute(dates - target)
    index_of_min_delta_from_target_date = np.argmin(abs_deltas_from_target_date)
    return index_of_min_delta_from_target_date
    #closest_date = all_dates[index_of_min_delta_from_target_date]

#################################################################################

data_of_interest = ['weight_body_mass','body_fat_percentage','lean_body_mass']
DoI_colours = ['xkcd:indigo','xkcd:dark orange','xkcd:kelly green']
from_date = '2022-08-22' #or None
moving_avg_length = 5
#################################################################################

health_data = pd.read_json('exported.json')
data = {}
for metric_ind in range(len(health_data.loc['metrics'][0])):
    metricname = health_data.loc['metrics'][0][metric_ind]['name']
    print(f'Processing: {metricname}')
    data[metricname] = {}
    data[metricname]['x'] = []
    data[metricname]['y'] = []
    data[metricname]['unit'] = health_data.loc['metrics'][0][metric_ind]['units']

    for ind in range(len(health_data.loc['metrics'][0][metric_ind]['data'])):
        data[metricname]['y'].append(float(health_data.loc['metrics'][0][metric_ind]['data'][ind]['qty']))
        date = datetime.strptime(health_data.loc['metrics'][0][metric_ind]['data'][ind]['date'], '%Y-%m-%d %H:%M:%S %z')
        data[metricname]['x'].append(date)
  
    
fig, ax = plt.subplots(len(data_of_interest),1,figsize=(6,6),sharex=True,constrained_layout=True)


for i, k in enumerate(data_of_interest):

    if from_date == None:
        numdates = mdates.date2num(data[k]['x'])
        z = np.polyfit(numdates, data[k]['y'], 1)
        
        moving_avg = Moving_Average(data[k]['y'], moving_avg_length)
        
        beginning = data[k]['x'][0].strftime("%d/%m/%Y")
        fig.suptitle(f'Apple Health data: processing all available data ({beginning})')
        
        ax[i].plot(data[k]['x'][moving_avg_length-1:],moving_avg,ls='-',color=DoI_colours[i],lw=2)      
        
        match_ind = 0 #for post-proc convenience
    else:
        from_date_td = datetime.strptime(from_date, '%Y-%m-%d')
        from_date_td = from_date_td.astimezone()
        match_ind = Nearest(np.asarray(data[k]['x']),
                            from_date_td)
        
        
    
        numdates = mdates.date2num(data[k]['x'][match_ind:])
        z = np.polyfit(numdates, data[k]['y'][match_ind:], 1)
        
        moving_avg = Moving_Average(data[k]['y'][match_ind:], moving_avg_length)
        
        beginning = from_date_td.strftime("%d/%m/%Y")
        fig.suptitle(f'Apple Health data: processing selection (from {beginning})')
        
        ax[i].plot(data[k]['x'][moving_avg_length-1+match_ind:],moving_avg,ls='-',color=DoI_colours[i],lw=2)
        
    p1 = np.poly1d(z)
    
    xx = np.linspace(numdates.min(), numdates.max(), 100)
    dd = mdates.num2date(xx)
    
    delta_y = p1(numdates.max())-p1(numdates.min())
    delta_x = numdates.max()-numdates.min()
    
    wdelta = delta_y*7/delta_x
    
    ax[i].plot(dd, p1(xx),color=DoI_colours[i],label=r'$\Delta =$'+f'{wdelta:.3f}{data[k]["unit"]} per week',ls='--',lw=1)
    
    ax[i].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=1,interval=2))    
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax[i].xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=1,interval=1))    
    #ax[i].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    ax[i].xaxis.grid(True, which='both')
    
    ax_maxmin_range = np.max(data[k]['y'][match_ind:])-np.min(data[k]['y'][match_ind:])
    ax[i].set_ylim((np.min(data[k]['y'][match_ind:])-ax_maxmin_range*0.10,
                    np.max(data[k]['y'][match_ind:])+ax_maxmin_range*0.10))

    

    #ax[i].plot(data[k]['x'],data[k]['y'],ls='--',color='xkcd:black',lw=0.5)
    
    ax[i].set_ylabel(f'{k}'+'\n'+f'[{data[k]["unit"]}]')
    
    ymin, ymax = ax[i].get_ylim()
    ax[i].set_ylim(ymin, ymax)
    
    if from_date == None:
        ax[i].scatter(data[k]['x'],data[k]['y'],s=40,marker='x',color='xkcd:black',lw=0.75,label=f"max-min: {np.max(data[k]['y'])-np.min(data[k]['y']):.2f}{data[k]['unit']}")
    else:
        ax[i].scatter(data[k]['x'],data[k]['y'],s=40,marker='x',color='xkcd:black',lw=0.75,label=f"max-min: {np.max(data[k]['y'][match_ind:])-np.min(data[k]['y'][match_ind:]):.2f}{data[k]['unit']}")
        vl= ax[i].axvline(from_date_td, 
                      0, 
                      1,
                      color=DoI_colours[i],
                      ls='--',
                      lw=1.5)  
    ax[i].legend(loc='upper right',bbox_to_anchor=(1.03, 1.2),fontsize=10)
#fig.tight_layout()
fig.savefig('AppleHealthData.pdf')  
fig.savefig('AppleHealthData.png')  
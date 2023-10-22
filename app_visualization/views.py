from django.shortcuts import render
from django.conf import settings
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from app_visualization.utils import *

# Create your views here.


def visualization(request):
    path_dataset = os.path.join(settings.MEDIA_ROOT, 'analysis/dataset.xlsx')
    path_salaries = os.path.join(settings.MEDIA_ROOT, 'analysis/salaries.xlsx')

    # histogram
    data_second = pd.read_excel(path_dataset, sheet_name='Wait_times')
    hist = get_hist(data_second, 'seconds', 'Customer Wait Time')

    # boxplot
    data_salaries = pd.read_excel(path_salaries)
    box = get_box(data_salaries, 'salary', 'Salary')

    # barchart
    activity = pd.read_excel(path_dataset, sheet_name="Activity")
    barchart = get_bar(activity, 'Activity',
                       'Number_of_Students', 'After-School Activities')

    # linechart
    water_consumption = pd.DataFrame({'m_3': [11, 13, 10, 14, 12, 12, 9, 10, 12, 15, 10, 14]},
                                     index=['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06',
                                            '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12'])
    linechart = get_plot(water_consumption, "Water Consumption 2020")

    # piechart
    df = pd.DataFrame(
        {
            'Name': ['Hillary Clinton', 'Donald Trump', 'Others'],
            'Virginia': [1981473, 1769443, 233715],
            'Maryland': [1677928, 943169, 160349],
            'West Virginia': [188794, 489371, 36258],
        }
    )
    df['Total'] = df['Virginia'] + df['Maryland'] + df['West Virginia']
    piechart=get_pie(df['Total'],df.Name,"Presidential Election Results")

    # scatter
    scatter_data = pd.read_excel(path_salaries)
    scatter=get_scatter(scatter_data,"years", "salary","Years vs. Salary")

    return render(request, 'visualization.html', {
        'hist': hist,
        'box': box,
        'barchart': barchart,
        'linechart': linechart,
        'piechart':piechart,
        'scatter':scatter,
    })

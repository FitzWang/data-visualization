# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import requests
import io
import altair as alt
from altair import datum
import geopandas as gpd
import panel as pn

alt.renderers.enable('altair_viewer')
alt.data_transformers.disable_max_rows() #disable the max row limitation of 5000

olympic_original_trans = pd.read_csv("https://raw.githubusercontent.com/FitzWang/data-visualization/master/olympic_transCode.csv")
olympic_medal_only = olympic_original_trans.dropna(subset=['Medal'])
olympic_summer_only = olympic_medal_only.loc[olympic_medal_only["Season"]=="Summer"]
#olympic_medal_only.to_csv("Medal_only.csv")

# process team achievements as unique item and count
olympicSum_medal_count = olympic_summer_only.groupby(['Year','NOC','Event','Medal']).count().reset_index().filter(items=['Year','NOC','Medal']).groupby(['Year','NOC']).count().reset_index()
olympicSum_count_byMedal = olympic_summer_only.groupby(['Year','NOC','Event','Medal']).count().reset_index().filter(items=['Year','NOC','Medal','ID']).groupby(['Year','NOC','Medal']).count().reset_index()
olympicSum_count_byMedal.rename(columns={'Medal': 'MedalCate', 'ID': 'Medal'},inplace=True)

group_yearCountry = olympicSum_count_byMedal.groupby(['Year','NOC'])
medal_cate = pd.DataFrame({"MedalCate":["Gold","Silver","Bronze"],"MedalCateOrder":[3,2,1]})
merge_medalCate = pd.DataFrame({"MedalCate":[],"Year":[],"NOC":[],"Medal":[]})
for i in list(group_yearCountry.indices):
    current_merge = pd.merge(medal_cate,group_yearCountry.get_group(i),how="outer",on = "MedalCate")
    current_merge["Year"] = current_merge["Year"].fillna(i[0])
    current_merge["NOC"] = current_merge["NOC"].fillna(i[1])
    merge_medalCate = pd.concat([current_merge,merge_medalCate])
merge_medalCate.rename(columns={"Medal":"MedalByCate"},inplace = True)

world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world  = world[world.continent!='Antarctica'] # do not display Antarctica
world.loc[21,'iso_a3']='NOR'
world.loc[43,'iso_a3']='FRA'
world.loc[174,'iso_a3']='KOS'
world.loc[160,'iso_a3']='CYP'

olympic_group_year = olympicSum_medal_count.groupby(['Year'])
year_unique = olympicSum_medal_count["Year"].unique()
for i in year_unique:
    if(i==1896):
        current_merge = pd.merge(world,olympic_group_year.get_group(i),how='outer',left_on="iso_a3",right_on="NOC")
        current_merge["Year"] = current_merge["Year"].fillna(i)
        medal_count_year = current_merge
    else:
        current_merge = pd.merge(world,olympic_group_year.get_group(i),how='outer',left_on="iso_a3",right_on="NOC")
        current_merge["Year"] = current_merge["Year"].fillna(i)
        medal_count_year = pd.concat([medal_count_year,current_merge])
medal_count_year['Medal'] = medal_count_year['Medal'].fillna(0)
count_year = pd.DataFrame(np.tile(np.arange(1,177),year_unique.size),columns=["order"])
medal_count_year = medal_count_year.sort_values(by=["Year","Medal"],ascending=[True,False]).reset_index()
medal_count_year["Order"]=count_year

# merge count with order and count medals by categories
medal_count_year_withCate = pd.merge(medal_count_year,merge_medalCate,how='outer',on=["Year","NOC"])

# Altair part
slider_year = alt.binding_range(min=1896, max=2016, step=4, name='Year:')
selector_year = alt.selection_single(fields=['Year'],bind=slider_year, init={'Year': 2016})
select_country = alt.selection(type="single", fields=['Year'])

sphere = alt.sphere()
graticule = alt.graticule()
background1 = alt.Chart(sphere).mark_geoshape(fill='lightgray')
background2 = alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5)
chart_medal_year = alt.Chart(medal_count_year_withCate).mark_geoshape(stroke='darkgray').encode( 
    color=alt.Color(field = "Medal",type = "quantitative",
                    scale=alt.Scale(type = "sqrt"),
                    legend=alt.Legend(title="Medals",labelFontSize = 15,symbolSize = 30,titleFontSize=20)),
    tooltip=['name:N','Medal:Q']
).add_selection(
    selector_year
).transform_filter(
    selector_year
).add_selection(select_country)

chart_medal_year_background = (background1+background2+chart_medal_year).project(
    'naturalEarth1'
).properties(
    title='Olympic Medals of The World',
    width=600,
    height=400
)

# bar chart for top 10 every year
olympic_bar = alt.Chart(medal_count_year_withCate).mark_bar().encode(
    x=alt.X(field="name", type='nominal', title="country",sort = '-y',
            axis=alt.Axis(labelFontSize=20,titleFontSize=25,labelAngle=-45)),
    y=alt.Y(field="MedalByCate",type="quantitative",aggregate='sum',stack='zero',title="Total Medals",
            axis=alt.Axis(labelFontSize=20,titleFontSize=25)),
    color=alt.Color(field = 'MedalCate', type = 'nominal',
                    scale = alt.Scale(domain = ["Gold","Silver","Bronze"],range=['gold', 'silver','sienna']),
                    legend=alt.Legend(title="Medal Category",labelFontSize = 15,symbolSize = 30,titleFontSize=20)),
    order=alt.Order('MedalCateOrder',sort='ascending')
)

# text
olympic_text = alt.Chart(medal_count_year_withCate).mark_text(dy=10,color='black').encode(
    x=alt.X(field="name", type='nominal', title="country",sort = '-y',
            axis=alt.Axis(labelFontSize=20,titleFontSize=25,labelAngle=-45)),
    y=alt.Y(field="MedalByCate",type="quantitative",aggregate='sum',stack='zero',title="Total Medals",
            axis=alt.Axis(labelFontSize=20,titleFontSize=25)),
    order=alt.Order('MedalCateOrder',sort='ascending'),
    detail='MedalCate:N',
    text=alt.Text('MedalByCate:Q')
)
# combine text with bar
olympic_bar_text = (olympic_bar+olympic_text).transform_filter(
    alt.datum.Order <= 10
).properties(
    title='Top 10 countries of the year',
    width=600,
    height=400
).add_selection(
    selector_year
).transform_filter(
    selector_year
)
    
(olympic_bar_text|chart_medal_year_background).configure_title(fontSize=30)

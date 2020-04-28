# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os
import altair as alt
from altair import datum
import geopandas as gpd
import panel as pn

alt.renderers.enable('altair_viewer')
alt.data_transformers.disable_max_rows()


# collect NOC
countries_breakup = pd.read_csv("https://raw.githubusercontent.com/FitzWang/data-visualization/master/breakup_NOC.csv")
Germany = countries_breakup["Germany"].dropna().tolist()
Soviet_Union = countries_breakup["Soviet Union"].dropna().tolist()
Yugoslavia = countries_breakup["Yugoslavia"].dropna().tolist()
Czechoslovakia = countries_breakup["Czechoslovakia"].dropna().tolist()
# collect name
countries_breakup_name = pd.read_csv("https://raw.githubusercontent.com/FitzWang/data-visualization/master/coutries_of_breakup.csv")
Germany_name = countries_breakup_name["Germany"].dropna().tolist()
Soviet_Union_name = countries_breakup_name["Soviet Union"].dropna().tolist()
Yugoslavia_name = countries_breakup_name["Yugoslavia"].dropna().tolist()
Czechoslovakia_name = countries_breakup_name["Czechoslovakia"].dropna().tolist()

countries_breakup_total_NOC = Germany + Soviet_Union + Yugoslavia + Czechoslovakia
countries_breakup_total_name = Germany_name  + Soviet_Union_name  + Yugoslavia_name  + Czechoslovakia_name 

# filter data for breakup countries
olympic_original = pd.read_csv("https://raw.githubusercontent.com/FitzWang/data-visualization/master/athlete_events.csv")
olympic_original_medal_only = olympic_original.dropna(subset=['Medal'])
olympic_original_summmer_only = olympic_original_medal_only.loc[olympic_original_medal_only["Season"]=="Summer"]
olympic_breakupCountries = olympic_original_summmer_only.loc[olympic_original_summmer_only["NOC"].isin(countries_breakup_total_NOC)]
# process team medals as one
olympic_BC_mergeTeam = olympic_breakupCountries.groupby(['Year','NOC','Event','Medal']).agg({'Team': 'first','ID': 'count'}).reset_index()
olympic_BC_countYear = olympic_BC_mergeTeam.groupby(['Year','NOC']).agg({'Team': 'first','Medal': 'count'}).reset_index()
# replace Latvia-1 to Latvia
# replace Tutti V to Estonia
olympic_BC_countYear.loc[:,"Team"].replace(["Latvia-1","Tutti V"],["Latvia","Estonia"],inplace=True)

## set year of close due to war to zero
# 1906: held during 1904 and 1906, not official, may consider to delete the data here
# 1916: world war 1
# 1940 and 1944: world war 2
nr_countries = np.size(countries_breakup_total_name)
# create observations with medal = 0 
olympic_close_filled = pd.DataFrame({'Year': pd.Series(np.repeat([1916, 1940, 1944],nr_countries)),
                                     'NOC': pd.Series(countries_breakup_total_NOC*3),
                                     'Team': pd.Series(countries_breakup_total_name*3),
                                     'Medal': pd.Series(np.repeat(0,nr_countries*3))})
olympic_BC_countYear_filled = pd.concat([olympic_BC_countYear,olympic_close_filled])
# drop year 1906
olympic_BC_countYear_filled = olympic_BC_countYear_filled.loc[olympic_BC_countYear_filled["Year"]!=1906]
year_unique = sorted(olympic_BC_countYear_filled["Year"].unique().tolist())

# plot for gernmany
Olympic_Germany = alt.Chart(olympic_BC_countYear_filled).mark_area().encode(
    alt.X(field = 'Year',type = "quantitative",
          scale=alt.Scale(domain=[1896, 2016]),
          axis=alt.Axis(title = " ",labels=False,values=year_unique)
          ),
    alt.Y(field = 'Medal',type = "quantitative",stack='zero',
          scale=alt.Scale(domain=[0,200]),
          axis=alt.Axis(labelFontSize = 15,titleFontSize=25)
          ),
    alt.Color('Team:N', scale=alt.Scale(scheme='category10'),
              legend=alt.Legend(values = Germany_name,title="Germany",
                                labelFontSize = 15,symbolSize = 200,titleFontSize=20)),
    opacity = alt.value(0.8)
).transform_filter(
    alt.FieldOneOfPredicate(field='NOC', oneOf = Germany)
).properties(
    title='Stream graph for 4 groups of countries',
    width=1000,
    height=300
).interactive()
Olympic_Germany

# plot for Soviet Union
Olympic_Soviet = alt.Chart(olympic_BC_countYear_filled).mark_area().encode(
    alt.X(field = 'Year',type = "quantitative",
          scale=alt.Scale(domain=[1896, 2016]),
          axis=alt.Axis(title = " ",labels=False,values=year_unique)
          ),
    alt.Y(field = 'Medal',type = "quantitative",stack='zero',
          scale=alt.Scale(domain=[0,200]),
          axis=alt.Axis(labelFontSize = 15,titleFontSize=25)
          ),
    alt.Color('Team:N',
              scale=alt.Scale(scheme='category20'),
              legend=alt.Legend(values = Soviet_Union_name,title="Soviet Union",
                                labelFontSize = 15,symbolSize = 200,titleFontSize=20)
              ),
    opacity = alt.value(0.8)
).transform_filter(
    alt.FieldOneOfPredicate(field='NOC', oneOf = Soviet_Union)
).properties(
    width=1000,
    height=300
)
Olympic_Soviet

# plot for Yugoslavia
Olympic_Yugoslavia = alt.Chart(olympic_BC_countYear_filled).mark_area().encode(
    alt.X(field = 'Year',type = "quantitative",
          scale=alt.Scale(domain=[1896, 2016]),
          axis=alt.Axis(title = " ",labels=False,values=year_unique)
          ),
    alt.Y(field = 'Medal',type = "quantitative",stack='zero',
          scale=alt.Scale(domain=[0,200]),
          axis=alt.Axis(labelFontSize = 15,titleFontSize=25)
          ),
    alt.Color('Team:N',
              scale=alt.Scale(scheme='paired'),
              legend=alt.Legend(values = Yugoslavia_name,title="Yugoslavia",
                                labelFontSize = 15,symbolSize = 200,titleFontSize=20)
              ),
    opacity = alt.value(0.8)
).transform_filter(
    alt.FieldOneOfPredicate(field='NOC', oneOf = Yugoslavia)
).properties(
    width=1000,
    height=300
)
Olympic_Yugoslavia

# plot for Czechoslovakia
Olympic_Czechoslovakia= alt.Chart(olympic_BC_countYear_filled).mark_area().encode(
    alt.X(field = 'Year',type = "quantitative",
          scale=alt.Scale(domain=[1896, 2016]),
          axis=alt.Axis(labelFontSize = 18,titleFontSize=30,values=year_unique)
          ),
    alt.Y(field = 'Medal',type = "quantitative",stack='zero',
          scale=alt.Scale(domain=[0,200]),
          axis=alt.Axis(labelFontSize = 15,titleFontSize=25,labelAngle=-45),
          ),
    alt.Color('Team:N',
              scale=alt.Scale(scheme='paired'),
              legend=alt.Legend(values = Czechoslovakia_name,title="Czechoslovakia",
                                labelFontSize = 15,symbolSize = 200,titleFontSize=20),
              ),
    opacity = alt.value(0.8)
).transform_filter(
    alt.FieldOneOfPredicate(field='NOC', oneOf = Czechoslovakia)
).properties(
    width=1000,
    height=300
)
Olympic_Czechoslovakia

# merge 4 graphs
alt.vconcat(
    Olympic_Germany,
    Olympic_Soviet,
    Olympic_Yugoslavia,
    Olympic_Czechoslovakia
).resolve_scale(
    color='independent'
).configure_title(fontSize = 30)
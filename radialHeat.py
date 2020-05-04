# -*- coding: utf-8 -*-
"""
Created on Mon May  4 11:30:22 2020

@author: guang
"""
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts
import panel as pn
import altair as alt
from altair import datum

pn.extension('vega')
#alt.renderers.enable('altair_viewer')
alt.data_transformers.disable_max_rows()
hv.extension("bokeh")
medal_count_year_withCate = pd.read_csv("medal_count_year_withCate.csv")
medal_count_year_top10 = medal_count_year_withCate.loc[medal_count_year_withCate["Order"]<=10]

year_unique = medal_count_year_top10["Year"].unique().tolist()
name_unique = medal_count_year_top10["name"].unique().tolist()
heatmap = hv.HeatMap(medal_count_year_top10, ["Year", "name"],["Medal"])
heatmap.opts(opts.HeatMap(radial=True,colorbar=True, start_angle=np.pi/2, width=500, height=500,
    yticks=None,xticks=year_unique,tools=['hover'],toolbar='above'))

slider_year = alt.binding_range(min=1896, max=2016, step=4, name='Year:')
selector_year = alt.selection_single(fields=['Year'],bind=slider_year, init={'Year': 2016})
select_country = alt.selection(type="single", fields=['Year'])

olympic_bar = alt.Chart(medal_count_year_withCate).mark_bar(opacity=0.8).encode(
    x=alt.X(field="name", type='nominal', title="country",sort = '-y',
            axis=alt.Axis(labelFontSize=10,titleFontSize=15,labelAngle=-45)),
    y=alt.Y(field="MedalByCate",type="quantitative",aggregate='sum',stack='zero',title="Total Medals",
            axis=alt.Axis(labelFontSize=10,titleFontSize=15)),
    color=alt.Color(field = 'MedalCate', type = 'nominal',
                    scale = alt.Scale(domain = ["Gold","Silver","Bronze"],range=['gold', 'silver','sienna']),
                    legend=alt.Legend(title="Medal Category",labelFontSize = 15,symbolSize = 30,titleFontSize=10)),
    order=alt.Order('MedalCateOrder',sort='ascending')
)

# text
olympic_text = alt.Chart(medal_count_year_withCate).mark_text(dy=10,color='black').encode(
    x=alt.X(field="name", type='nominal', title="country",sort = '-y',
            axis=alt.Axis(labelFontSize=10,titleFontSize=15,labelAngle=-45)),
    y=alt.Y(field="MedalByCate",type="quantitative",aggregate='sum',stack='zero',title="Total Medals",
            axis=alt.Axis(labelFontSize=10,titleFontSize=15)),
    order=alt.Order('MedalCateOrder',sort='ascending'),
    detail='MedalCate:N',
    text=alt.Text('MedalByCate:Q')
)
# combine text with bar
olympic_bar_text = (olympic_bar+olympic_text).transform_filter(
    alt.datum.Order <= 10
).properties(
    title='Top 10 countries of the year',
    width=500,
    height=300
).add_selection(
    selector_year
).transform_filter(
    selector_year
)
    
pn.Row(pn.pane.Vega(olympic_bar_text,width=700, height=500),pn.pane.HoloViews(heatmap,width=550, height=500)).show()

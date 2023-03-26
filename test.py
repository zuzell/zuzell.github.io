import pandas as pd
from bokeh.io import output_file, save, show
from bokeh.models.widgets import Select
from bokeh.models.callbacks import CustomJS
from bokeh.models import ColumnDataSource, FactorRange, CustomJS
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import Select, Legend, LegendItem
from bokeh.resources import CDN
from bokeh.embed import file_html

df = pd.read_csv("C:/Users/zuzal/Masters/02806 Social Data Analysis/Police_Department_Incident_Reports__Historical_2003_to_May_2018.csv")
df['Date']= pd.to_datetime(df['Date'])
#filter by year
df=df[(df['Date'].dt.strftime('%Y') < '2018') & (df['Date'].dt.strftime('%Y') > '2009')] 
#create a year column
df['Year'] = df['Date'].dt.year

#timeseries
categories = ['DRUNKENNESS', 'DRUG/NARCOTIC', 'PROSTITUTION']

df['Time'] = pd.to_datetime(df['Time'], format='%H:%M')
df['Hour'] = df['Time'].dt.hour
df['Month'] = df['Time'].dt.month
df=df[df['Category'].isin(categories)] 

#df grouped by hours
df_hour=df.groupby(['Hour', 'Category']).size() / df.groupby('Category').size()
df_hour=df_hour.unstack()


#grouped by years
df_year = df.groupby(['Year', 'Category']).size() / df.groupby('Category').size()
df_year = df_year.unstack()


#group by days
df_day = df.groupby(['DayOfWeek', 'Category']).size() / df.groupby('Category').size()
df_day=df_day.unstack()


source = ColumnDataSource(df_day)
#Factor ranges
hours = [str(x+1) for x in range(24)]
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
years = df['Year'].unique().astype(str).tolist()



# Define the colors for each category
colors = ["#BE98CB", "#A7DF9A", "#3571E4"]

# Define the options for the dropdown menu
options = ["Days", "Years", "Hours"]
# Create a Select widget
picklist = Select(title="Select time unit for x-axis", value=options[2], options=options)


from bokeh.layouts import column, row
from bokeh.models import Div

from bokeh.models import CustomJS

from bokeh.models import Legend, LegendItem

def create_plot(x_range, source, x_label, title):
    #source = ColumnDataSource(data)
    p = figure(x_range=x_range, height=350, title=title, toolbar_location=None, tools="")
    
    legend = Legend(items=[], location="top_left")

    bar = {}  # to store vbars
    for indx, i in enumerate(categories):
        bar[i] = p.vbar(x='index', top=i, source=source, muted_alpha=0.2, color=colors[indx % len(colors)])
        legend_item = LegendItem(label=i, renderers=[bar[i]])
        legend.items.append(legend_item)

    p.add_layout(legend, 'left')
    p.legend.click_policy = "mute"
    p.legend.background_fill_alpha = 0.7
    p.legend.label_text_font_size = "8pt"
    p.legend.spacing = 2
    p.legend.padding = 2
    p.legend.margin = 5
    p.xaxis.axis_label = x_label
    p.yaxis.axis_label = "Occurrences"

    return p

source_day = ColumnDataSource(df_day.reset_index())
source_year = ColumnDataSource(df_year.reset_index())
source_hour = ColumnDataSource(df_hour.reset_index())

p_day = create_plot(FactorRange(factors=days), source_day, "Days", "Crimes Counts by Days")
p_year = create_plot(FactorRange(factors=years), source_year, "Years", "Crimes Counts by Years")
p_hour = create_plot(FactorRange(factors=hours), source_hour, "Hours", "Crimes Counts by Hours")

p_day.visible = False
p_year.visible = False
p_hour.visible = True

callback = CustomJS(args=dict(p_day=p_day, p_year=p_year, p_hour=p_hour), code="""
    p_day.visible = false;
    p_year.visible = false;
    p_hour.visible = false;
    if (cb_obj.value == "Days") {
        p_day.visible = true;
    } else if (cb_obj.value == "Years") {
        p_year.visible = true;
    } else {
        p_hour.visible = true;
    }
""")

picklist.js_on_change('value', callback)

layout = column(picklist, p_day, p_year, p_hour)

output_file("crimes_plot.html")

show(layout)
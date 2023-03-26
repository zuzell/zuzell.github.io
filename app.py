import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, FactorRange, Legend, LegendItem, Select
from bokeh.plotting import figure, show


df = pd.read_csv("../files/PD_reports_03_18.csv")
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

# Define the initial source for the plot
source = ColumnDataSource(df_hour.reset_index())

# Define the figure
p = figure(x_range=FactorRange(factors=hours), height=350, title="Crimes Counts by hours", toolbar_location=None, tools="")

# Create a legend
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
p.xaxis.axis_label = "Hours"
p.yaxis.axis_label = "Occurrences"

def update_plot(attr, old, new):
    selected_value = picklist.value
    if selected_value == "Days":
        p.xaxis.axis_label = "Days"
        p.x_range.factors = days
        p.title.text = f"Crimes Counts by {selected_value}"
        source.data = df_day.reset_index()
    elif selected_value == "Years":
        p.xaxis.axis_label = "Years"
        p.x_range.factors = years
        p.title.text = f"Crimes Counts by {selected_value}"
        source.data = df_year.reset_index()
    else:  # selected_value == "Hours"
        p.xaxis.axis_label = "Hours"
        p.x_range.factors = hours
        p.title.text = f"Crimes Counts by {selected_value}"
        source.data = df_hour.reset_index()

picklist.on_change('value', update_plot)

layout = column(picklist, p)

curdoc().add_root(layout)

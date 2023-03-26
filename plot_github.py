import pandas as pd
from bokeh.io import output_file, save, show
from bokeh.models import ColumnDataSource, FactorRange, CustomJS
from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import Select, Legend, LegendItem
from bokeh.models.widgets import Select
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
source_hour=ColumnDataSource(df_hour.reset_index())
source_year=ColumnDataSource(df_year.reset_index())
source_day=ColumnDataSource(df_day.reset_index())

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

'''callback = CustomJS(args=dict(p=p, picklist=picklist, source=source, s_day=source_day, s_year=source_year, s_hour=source_hour, days=days, years=years, hours=hours), code="""
    const selected_value = cb_obj.value;
    if (selected_value == "Days") {
        p.xaxis.axis_label = "Days";
        p.x_range.factors = days;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data = s_day;
    } else if (selected_value == "Years") {
        p.xaxis.axis_label = "Years";
        p.x_range.factors = years;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data = s_year;
    } else { // selected_value == "Hours"
        p.xaxis.axis_label = "Hours";
        p.x_range.factors = hours;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data = s_hour;
    }
    p.change.emit();
""")'''


callback = CustomJS(args=dict(p=p, picklist=picklist, source=source, s_day=source_day, s_year=source_year, s_hour=source_hour, days=days, years=years, hours=hours), code="""
    const selected_value = cb_obj.value;
    if (selected_value == "Days") {
        p.xaxis.axis_label = "Days";
        p.x_range.factors = days;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data['index'] = s_day.data['index'].slice();
        source.data['DRUG/NARCOTIC'] = s_day.data['DRUG/NARCOTIC'].slice();
        source.data['DRUNKENNESS'] = s_day.data['DRUNKENNESS'].slice();
        source.data['PROSTITUTION'] = s_day.data['PROSTITUTION'].slice();
    } else if (selected_value == "Years") {
        p.xaxis.axis_label = "Years";
        p.x_range.factors = years;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data['index'] = s_year.data['index'].slice();
        source.data['DRUG/NARCOTIC'] = s_year.data['DRUG/NARCOTIC'].slice();
        source.data['DRUNKENNESS'] = s_year.data['DRUNKENNESS'].slice();
        source.data['PROSTITUTION'] = s_year.data['PROSTITUTION'].slice();
    } else { // selected_value == "Hours"
        p.xaxis.axis_label = "Hours";
        p.x_range.factors = hours;
        p.title.text = `Crimes Counts by ${selected_value}`;
        source.data['index'] = s_hour.data['index'].slice();
        source.data['DRUG/NARCOTIC'] = s_hour.data['DRUG/NARCOTIC'].slice();
        source.data['DRUNKENNESS'] = s_hour.data['DRUNKENNESS'].slice();
        source.data['PROSTITUTION'] = s_hour.data['PROSTITUTION'].slice();
    }
    p.x_range.change.emit();
    p.change.emit();
    source.change.emit();
""")




picklist.js_on_change('value', callback)
layout = column(picklist, p)

output_file("crimes_plot.html")


show(layout)
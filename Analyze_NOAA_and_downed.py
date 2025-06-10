#!/usr/bin/env python
# coding: utf-8

# ## Merge and analyze NOAA_df and downed_df
# 

# In[1]:


# Import the following libraries:
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from NOAA import get_cleaned_NOAA_df
from reason_data import downed 


# In[2]:


# Quick look at the data size for reference
downed_df = downed()
NOAA_df = get_cleaned_NOAA_df()

print("downed_df: ",len(downed_df))
print("NOAA_df: ",len(NOAA_df))


# ## Now join downed_df and NOAA_df
# The NOAA data contains multiple lines per day.  In order to limit lines from downed_df being duplicated after the merge,
# use the **pandas.merge_asof** method.<br>This will merge the downed_df on the nearest prior datetime as the NOAA_df.

# In[3]:


downed_df = downed_df.sort_values('downed')
NOAA_df = NOAA_df.sort_values('DATE')

def merge_downed_and_NOAA():
    # Merge and assign each downed event the most recent NOAA data before that event
    # merge_asof is like a left-join but matches on the nearest key rather than the equal keys. 
    merged_df = pd.merge_asof(
        downed_df,
        NOAA_df,
        left_on='downed',
        right_on='DATE',
        direction='backward'
    )
    return merged_df
merged_df = merge_downed_and_NOAA()

# Check to make sure merge operation worked correctly. 
# The dates in 'downed' (from downed_df) and 'DATE' (from NOAA_df) should be the same.
merged_df[['downed','DATE']]


# ### There are still some rows in merged_df that contain NaNs!

# In[4]:


nan_rows = merged_df[merged_df['DATE'].isna()]
nan_rows['downed']


# ### All of these events began prior to the NOAA data, so remove these rows.

# In[5]:


merged_df = merged_df.drop(nan_rows.index)
print("merged_df: ",len(merged_df), " rows")


# ### The 50 hour, 100 hour, and Annual inspections occur on a schedule, and the Unspecified reasons don't give any indications, so all those can be removed from analysis.

# In[6]:


final_merged_df = merged_df.loc[merged_df['reason'].isin(['50 Hr Inspect', '100 Hr Inspect', 'Annual Inspect','Unspecified']) == False]
final_merged_df.head()


# ### The dataframe is ready to analyze.  Start with a SPLOM.
# Use Seaborn's pairplot to create a SPLOM.

# In[7]:


# There are a lot of weather columns, so pick just a few to start.
important_cols = [
    'avg_temperature_prev_5d',
    'avg_precipitation_prev_5d',
    'avg_humidity_prev_5d',
    'avg_wind_speed_prev_5d',
    'avg_visibility_prev_5d',
]


# In[32]:


def weather_splom(columns):
    sub_df = final_merged_df[columns + ['reason']].dropna()

    g = sns.pairplot(
        sub_df,
        vars=columns,
        hue='reason',
        palette='Pastel1',
        corner=True,
        plot_kws={'alpha': 0.6}
    )

    g.fig.suptitle("SPLOM of NOAA Rolling Averages by Downed Reason", y=1.02)
    g.fig.tight_layout()
    g.fig.subplots_adjust(top=0.95)
    return g.fig
weather_splom(important_cols)


# ### The results show a relation between downed events and weather conditions.
# It looks like there might be a link among good visibility, low precipitation, and warm weather causing an increase in downed events. Probably more flights during that time!
# 
# Use Seaborn's kdeplot to recreate the diagonal charts from the above SPLOM.

# In[27]:


# KDE plot template for weather data in final_merged_df
# Use this function for any/all weather features to get a closer look.
def plot_kde_by_reason(x):

    sub_df = final_merged_df[[x, 'reason']].dropna()

    fig = plt.figure(figsize=(10, 5))
    sns.kdeplot(
        data=sub_df,
        x=x,
        hue='reason',
        fill=True,
        common_norm=False,
        alpha=0.4,
        linewidth=1.5,
        palette='Pastel1'
    )

    plt.title(f'Distribution of {x} by Downed Reason')
    plt.xlabel(x)
    plt.ylabel('Distribution Density')
    plt.tight_layout()
    return fig
plot_kde_by_reason('avg_temperature_prev_5d')


# In[10]:


# Get the number of each downed reason
reason_counts = merged_df['reason'].value_counts()
print(reason_counts)


# ### The resource column in final_merged_df contains the aircraft's WMU# and tail number
# How can we add that to the analysis?

# In[11]:


# Get a count of the number of aircraft used in the dataset and the number
# of times each one was downed for a maintenance problem
aircraft_counts = final_merged_df['resource'].value_counts()
print("Aircraft Count: ", len(aircraft_counts))
aircraft_counts


# ### Build a bar chart that shows the breakdown of each downed event by reason and separated for each aircraft
# Use Seaborn's barplot

# In[28]:


def downed_counts_by_aircraft_and_reason():
    # Count downed events per aircraft
    aircraft_counts = final_merged_df['resource'].value_counts()
    
    # Count how many times each aircraft was downed for each reason
    count_df = final_merged_df.groupby(['resource', 'reason']).size().reset_index(name='count')

    # Sort aircraft by total downed events for ordered plotting
    count_df['resource'] = pd.Categorical(count_df['resource'], categories=aircraft_counts.index, ordered=True)

    fig = plt.figure(figsize=(10, 8))
    ax = sns.barplot(
        data=count_df,
        y='resource',
        x='count',
        hue='reason',
        palette='tab10'
    )

    plt.title("Downed Events per Aircraft by Reason")
    plt.xlabel("Event Count")
    plt.ylabel("Aircraft (Resource)")
    plt.legend(title='Reason', bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout()
    return fig

downed_counts_by_aircraft_and_reason()


# ### Use a stacked bar chart to make it easier to read
# 

# In[29]:


def stacked_downed_counts_by_aircraft_and_reason():
    # Count downed events per aircraft
    aircraft_counts = final_merged_df['resource'].value_counts()

    # Create pivot table of counts per (resource, reason)
    count_df = final_merged_df.groupby(['resource', 'reason']).size().unstack(fill_value=0)

    # Order aircraft by total downed counts using aircraft_counts
    count_df = count_df.loc[aircraft_counts.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    left = pd.Series([0] * len(count_df), index=count_df.index)
    colors = plt.cm.Pastel1.colors

    for i, reason in enumerate(count_df.columns):
        counts = count_df[reason]
        ax.barh(count_df.index, counts, left=left, label=reason, color=colors[i % len(colors)])
        left += counts

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)    

    ax.set_xlabel("Total Downed Events")
    ax.set_ylabel("Aircraft Number")
    ax.margins(y=0.02)
    ax.set_title("Downed Events per Aircraft by Reason")
    ax.legend(title='Reasons', bbox_to_anchor=(1.01, 1), loc='upper left')

    plt.tight_layout()
    return fig
stacked_downed_counts_by_aircraft_and_reason()


# ## Take a look at durations of downed events
# Make a horizontal bar chart with Seaborn's barplot

# In[55]:


def downtime_barchart(df):
    avg_duration = df.groupby('reason')['duration'].mean().reset_index()
    avg_duration['duration_hours'] = avg_duration['duration'].dt.total_seconds() / 3600
    
    plot_data = avg_duration.reset_index()
    plot_data = plot_data.sort_values('duration_hours', ascending=True)
        
    fig = plt.figure(figsize=(12, 6))
    barplot = sns.barplot(
        data=plot_data,
        y='reason',
        x='duration_hours',
        palette='rocket'
    )
    
    for i in barplot.containers:
        barplot.bar_label(i, fmt='%.1f', label_type='edge', padding=3)
    
    plt.title('Average Downtime Duration by Reason', fontsize=14)
    plt.xlabel('Average Duration (Hours)')
    plt.ylabel('Reason')
    plt.tight_layout()

    return fig
downtime_barchart(downed_df)


# In[52]:


figb


# In[34]:


#Create KDE plots for all the columns for the report
avg_cols = ['avg_altimeter_prev_5d', 
            'avg_dew_point_prev_5d',
            'avg_temperature_prev_5d',
            'avg_precipitation_prev_5d',
            'avg_humidity_prev_5d',
            'avg_visibility_prev_5d',
            'avg_wind_dir_prev_5d',
            'avg_gust_speed_prev_5d',
            'avg_wind_speed_prev_5d',
           ]


# ### Define a function that will save the desired charts to a folder in the Jupyter workspace

# In[35]:


# Use this to save any of the above charts by calling its function.
save_dir = "Charts" 

def save_plots(filename):    
    path = os.path.join(save_dir, f"{filename}.png")
    fig = plt.gcf()
    fig.savefig(path, dpi=300)
    plt.close(fig)


# In[36]:


#Plots to save:

# plot_kde_by_reason for every avg_col
# downtime_barchart(downed_df)
# stacked_downed_counts_by_aircraft_and_reason()
# weather_splom(important_cols)



# Save all the plot_kde_by_reason for every avg_col

# In[41]:


# uncomment to run
# for col in avg_cols:
#     plot_kde_by_reason(col)
#     save_plots(f'kde_{col}')


# downtime_barchart(downed_df)

# In[54]:


# uncomment to run
# downtime_barchart(downed_df)
# save_plots('downtime_barchart')


# stacked_downed_counts_by_aircraft_and_reason()

# In[43]:


# uncomment to run
# stacked_downed_counts_by_aircraft_and_reason()
# save_plots('stacked_downed_counts_by_aircraft_and_reason')


# weather_splom(important_cols)

# In[44]:


# uncomment to run
# weather_splom(important_cols)
# save_plots('weather_splom')


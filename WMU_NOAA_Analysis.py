import pandas as pd
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from NOAA import df_A, df_B, get_cleaned_NOAA_df
from reason_data import downed
from historical_data import total_down_time, fleet_average_down_time, history

# Correlations
df_A = df_A()
df_B = df_B()

# Labels and attributes
RMS_tot_down_time = total_down_time()
RMS_avg_down_time = fleet_average_down_time()
history_df = history()
downed_df = downed()
NOAA_df = get_cleaned_NOAA_df()

# This is to track the effect of cleaning a dataframe
def descriptives():
    print("RMS reported average down time:", RMS_avg_down_time)
    print("RMS reported down time:", RMS_tot_down_time, "\n")

    downed_total_time = np.sum(downed_df["duration"])
    downed_avg = np.mean(downed_df["duration"])
    print("Average down time in 'downed' df:", downed_avg)
    print("Downed time in 'downed' df:", downed_total_time, "\n")
    history_total_time = np.sum(history_df["duration"])
    history_avg = np.mean(history_df["duration"])
    print("Average down time in 'history' df:", history_avg)
    print("Downed time in 'history' df:", history_total_time)

    return print("_" * 25, "end of report", "_" * 25)

descriptives()

def reason_cats():
    print(downed_df.reason.unique())
    print("_" * 65)

reason_cats()

def history_cats():
    print(history_df["downed reason"].unique(), "\n")
    print(history_df["squawk"].unique(), "\n")
    print(history_df["comments"].unique(), "\n")
    print("_" * 65)

history_cats()

#########################################################################################
# We need to clean this all up, but I wanteed to get it in here so you can check it out.#
#########################################################################################

downed_df = downed_df.sort_values('downed')
NOAA_df = NOAA_df.sort_values('DATE')

# Merge: assign each downed event the most recent NOAA data before that event
merged_df = pd.merge_asof(
    downed_df,
    NOAA_df,
    left_on='downed',
    right_on='DATE',
    direction='backward'
)

# There are some rows in merged_df that contain NaNs.
nan_rows = merged_df[merged_df['avg_temperature_prev_5d'].isna()]
print(nan_rows['downed'])

merged_df = merged_df.drop(nan_rows.index)

# The 50 hour, 100 hour, and Annual inspections occur on a schedule, and the Unspecified reasons don't give any indications, so all those can be removed from analysis.

final_merged_df = merged_df.loc[merged_df['reason'].isin(['50 Hr Inspect', '100 Hr Inspect', 'Annual Inspect','Unspecified']) == False]

# Here's the SPLOM.  
def weather_splom():

    important_cols = [
        'avg_temperature_prev_5d',
        'avg_precipitation_prev_5d',
        'avg_humidity_prev_5d',
        'avg_wind_speed_prev_5d',
        'avg_visibility_prev_5d',
    ]

    sub_df = final_merged_df[important_cols + ['reason']].dropna()

    sns.pairplot(
        sub_df,
        vars=important_cols,
        hue='reason',
        corner=True,
        plot_kws={'alpha': 0.6}
    )

    plt.suptitle("SPLOM of NOAA Rolling Averages by Downed Reason", y=1.02)
    plt.tight_layout()
    plt.show()

# plot_weather_splom()


# KDE plot template for weather data in final_merged_df
def plot_kde_by_reason(x):
    sub_df = final_merged_df[[x, 'reason']].dropna()

    plt.figure(figsize=(10, 5))
    sns.kdeplot(
        data=sub_df,
        x=x,
        hue='reason',
        fill=True,
        common_norm=False,
        alpha=0.4,
        linewidth=1.5,
        palette='tab10'
    )

    plt.title(f'Distribution of {x} by Downed Reason')
    plt.xlabel(x)
    plt.ylabel('Density')
    plt.tight_layout()
    plt.show()

# plot_kde_by_reason('avg_temperature_prev_5d')


reason_counts = merged_df['reason'].value_counts()
# print(reason_counts)

aircraft = merged_df['resource'].value_counts()
print("No. aircraft: ", len(aircraft))
print(aircraft)


# Chart showing how many times each aircraft was downed and for what reason.
def downed_counts_by_aircraft_and_reason():
    count_df = final_merged_df.groupby(['resource', 'reason']).size().reset_index(name='count')
    total_counts = count_df.groupby('resource')['count'].sum().sort_values(ascending=False)
    count_df['resource'] = pd.Categorical(count_df['resource'], categories=total_counts.index, ordered=True)

    plt.figure(figsize=(10, 8))
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
    plt.show()

# downed_counts_by_aircraft_and_reason()

# Another plot of the same data, but this one is stacked so it is easier to read.
def stacked_downed_counts_by_aircraft_and_reason():
    count_df = final_merged_df.groupby(['resource', 'reason']).size().unstack(fill_value=0)
    count_df = count_df.loc[count_df.sum(axis=1).sort_values(ascending=False).index]

    plt.figure(figsize=(10, 8))
    left = pd.Series([0] * len(count_df), index=count_df.index)
    colors = plt.cm.tab10.colors  
    for i, reason in enumerate(count_df.columns):
        counts = count_df[reason]
        bars = plt.barh(count_df.index, counts, left=left, label=reason, color=colors[i % len(colors)])
        left += counts

    plt.xlabel("Total Downed Events")
    plt.ylabel("Aircraft (Resource)")
    plt.margins(y=0.02)
    plt.title("Stacked Downed Events per Aircraft by Reason")
    plt.legend(title='Reason', bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.xticks(ticks=[0, 5, 10, 15, 20], labels=['0', '5', '10', '15', '20'])
    plt.tight_layout()
    plt.show()

# stacked_downed_counts_by_aircraft_and_reason()




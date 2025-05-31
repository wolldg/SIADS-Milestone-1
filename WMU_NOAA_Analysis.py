import pandas as pd
import re
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from NOAA import df_A, df_B
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
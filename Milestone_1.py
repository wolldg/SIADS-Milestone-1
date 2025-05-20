import pandas as pd
import datetime

history_df = pd.read_csv("Resource Down History.csv")
# print(history_df.columns)
# print(history_df.head())

# -------------------------------------------------------------- #
# The first and second columns are repeating strings.

# The aircraft data is from 01 January 2024 to 31 December 2024
# -------------------------------------------------------------- #

history_df = history_df.drop(columns=["Unnamed: 0", "Unnamed: 1"])
# print(history_df.columns)

SR_20_down_time = history_df["avg down time per resource"].iloc[0] # Average down-time for the fleet of SR20s
fleet_avg_down_time = SR_20_down_time = pd.to_timedelta(SR_20_down_time)
history_df = history_df.drop(columns=["avg down time per resource"]) # Dropping old column
# print(history_df.info())
# print(SR_20_down_time)

reason_df = pd.read_csv("Resources Downed by Reason.csv")
# print(reason_df.columns)
# print(reason_df.info())



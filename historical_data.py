import pandas as pd
import re
import numpy as np


history_df = pd.read_csv("Resource Down History.csv")

# Needed to clean "duration" separately
def parse_mixed_time(val):
    try:
        val = val.strip()

        # HH:MM:SS
        if re.match(r"^\d+:\d{2}:\d{2}(\.\d+)?$", val):
            return pd.to_timedelta(val)

        # MM:SS or M:SS
        if re.match(r"^\d+:\d{2}$", val):
            mins, secs = map(int, val.split(":"))
            return pd.to_timedelta(pd.Timedelta(minutes=mins, seconds=secs))

        # :SS
        if re.match(r"^\d+$", val):
            return pd.to_timedelta(seconds=int(val))

    # It can be nan if the number is too wild
    except Exception as e:
        print(f"Error parsing '{val}': {e}")
        return np.nan

def history():
    # -------------------------------------------------------------- #
    # 1. The first and second columns are repeating strings, headers for Excel.
    # 2. Four features have repeating values that may not be accurate.
    #    - Average down-time by resource (there is only one resource), SR20.
    #    - Total fleet down-time.
    #    - Average down-time for a tail (registration number).
    #    - Downs, the number of times the tail was taken out of service.
    # 3. One aircraft is dropped because it was sold, and not operating in the fleet.
    # 4. The aircraft data is from 01 January 2024 to 31 December 2024
    # -------------------------------------------------------------- #

    interesting_columns = ["registration number", "downs",
                           "total tail down time", "avg tail down time",
                           "upped", "downed", "duration",
                           "downed reason", "squawk", "comments"]
    df = pd.read_csv("Resource Down History.csv", usecols=interesting_columns)
    df = df.drop(index=0) # Sold aircraft
    df.rename(columns={"registration number": "reg"}, inplace=True)

    # Correcting Datatypes
    df["total tail down time"] = pd.to_timedelta(df["total tail down time"])
    df["avg tail down time"] = pd.to_timedelta(df["avg tail down time"])
    df["upped"] = pd.to_datetime(df["upped"])
    df["downed"] = pd.to_datetime(df["downed"])
    df["reported duration"] = df["duration"].apply(parse_mixed_time)
    df["duration"] = df["upped"] - df["downed"]

    def complete_duration ():
        nans = df[df["duration"].isna()].index  # index of all NaN values [57, 132, 266, 441, 727, 861, 900]
        for i in nans:
            df.at[i, "duration"] = df.at[i, "reported duration"]  # Filling NaN from "reported duration"
        return df["duration"]

    df["duration"] = complete_duration()

    return df

# Average down-time for the fleet of SR20s
def fleet_average_down_time():
    fleet_avg_down_time = history_df["avg down time per resource"].iloc[0]
    fleet_avg_down_time = pd.to_timedelta(fleet_avg_down_time)

    return fleet_avg_down_time

# Total down-time for the fleet of SR20s
def total_down_time():
    total_down_time = history_df["total down time"].iloc[1]
    total_down_time = pd.to_timedelta(total_down_time)

    return total_down_time

history()
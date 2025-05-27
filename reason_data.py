import pandas as pd
import datetime
import re
import numpy as np

df = pd.read_csv("Resources Downed by Reason.csv")
df = df.drop(df.index[0]) # Sold aircraft

def downed():
    downed_df = df.copy()
    # print(downed_df['day'].unique(), "\n") # This is all the day the data was queried
    # print(downed_df['time'].unique(), "\n") # This is all the time the data was queried
    downed_df = downed_df.iloc[:, :6]

    # print(downed_df["downed reason"].head(10), downed_df["eta squawk"].head(10)) # These columns complete each other
    # Concatenating columns
    # Replacing NaN with nice string values
    downed_df["reason"] = ((downed_df["downed reason"].fillna("").str.strip()
                           + " " +
                           downed_df["eta squawk"].fillna("").str.strip())
                           .str.replace(r"Squawk", "Unspecified", regex=True).str.strip()
                           .str.replace(r"\s+", " ", regex=True).str.strip())


    #------------------------------------------------------------------------------------------------------------------#

    # print(downed_df["reason"].unique())

    # ['50 Hr Inspect' 'Other' 'Engine' 'Inspection' 'Squawk' 'Propeller'
    #  'Squawk Other' 'Avionics' 'Airframe' 'Squawk Engine' 'Annual Inspect'
    #  'Aircraft Malfunc' 'Scheduled Mx' 'Squawk Airframe Damage'
    #  'Squawk Avionics' 'Inspection 50 Hr Inspect' 'Airframe Damage' 'Hangar'
    #  'Squawk Airframe' 'Squawk Aircraft Malfunc' 'Eng Abnorm Noise'
    #  '100 Hr Inspect' 'Inspection Engine' 'Inspection Other'
    #  'Inspection Avionics']

    # Some of these are redundant

    acceptable = ['50 Hr Inspect', 'Engine', 'Propeller',
                  'Avionics', 'Airframe', 'Annual Inspect',
                  'Airframe Damage', 'Hangar', '100 Hr Inspect', "Unspecified"]

    acceptable_lower = {word.lower(): word for word in acceptable}  # For stability

    def map_reason(reason):
        reason_lower = str(reason).lower()
        for label in acceptable_lower:
            if label in reason_lower:
                return next(original for original in acceptable if original.lower() == label)
        return "Unspecified"

    downed_df["reason"] = downed_df["reason"].apply(map_reason)
    downed_df = downed_df.drop(["downed reason", "eta squawk"], axis=1)  # Don't need these anymore
    #------------------------------------------------------------------------------------------------------------------#
    from historical_data import parse_mixed_time


    downed_df["downed"] = pd.to_datetime(downed_df['downed'])
    downed_df["upped"] = pd.to_datetime(downed_df['upped'])
    downed_df['duration'] = downed_df['duration'].astype(str).str.replace(",", "", regex=False)  # Removing commas
    downed_df["reported duration"] = [pd.Timedelta(hours=h) for h in downed_df["duration"].astype(float)]

    # This column is the more precisely calculated duration
    downed_df["duration"] = downed_df["upped"] - downed_df["downed"]

    # print(downed_df["duration"].iloc[58]) # There are some rows where the upped time is missing
    def complete_duration ():
        nans = downed_df[downed_df["duration"].isna()].index  # index of NaN values [57, 132, 266, 441, 727, 861, 900]
        for i in nans:
            downed_df.at[i, "duration"] = downed_df.at[i, "reported duration"]  # Filling NaN from "reported duration"
            downed_df["downed"] = pd.to_datetime(downed_df['downed'])
        return downed_df["duration"]

    downed_df["duration"] = complete_duration()

    return (downed_df)

test = downed()
#print(test.columns)

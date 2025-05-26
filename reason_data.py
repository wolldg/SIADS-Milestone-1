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

    downed_df["downed"] = pd.to_datetime(downed_df['downed'])
    downed_df["upped"] = pd.to_datetime(downed_df['upped'])

    downed_df["duration"] = downed_df["upped"] - downed_df["downed"]  # The duration column was messy and inaccurate

    # print(downed_df["duration"].iloc[58]) # There are some rows where the upped time is missing

    return (downed_df)

test = downed()
#print(test.columns)

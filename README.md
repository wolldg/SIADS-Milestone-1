# SIADS-Milestone-1
Aviation Operational Intelligence Analysis: A look at the flight hour and maintenance requirements of a high tempo flight school.

## There are four programs. Three of them clean a csv.
    - NOAA.py cleans the NOAA_LCD_BattleCreek_2024.csv.
        - **df_A** is a function that returns a dataframe with meteorological data from the NOAA.
        - **df_B** is a function that returns a dataframe with METAR data collected from the airport.

    - historical_data.py
        - **total_down_time** is a function that returns a descriptive statistic from the service center database.
          It does not benefit from data cleaning methods.
        - **fleet_average_down_time** is a function that returns a descriptive statistic from the service center database.
          It does not benefit from data cleaning methods.
        - **history** is a function that returns a dataframe that is more reasonably cleaned.
          It has multiple datapoints to describe the downed reason: "downed reason", "squawk", "comments".

    - reason_data.py
        - **downed** is a function that returns a df similar to _history_ but is is less descriptive.
          While it may not call out things like "boost pump" of "mag check" it categorizes points of failure more broadly. 
import pandas as pd
import re

# Correcting an annoying DtypeWarning
dtype_spec = {16: str, 26: str, 27: str, 32: str,
              37: str, 41: str, 42: str, 43: str,
              45: str, 82: str, 85: str, 87: str}


df = pd.read_csv("NOAA_LCD_BattleCreek_2024.csv", dtype=dtype_spec)

# Rows below have additional data that are making cleaning more cumbersome.
df = df[df["REPORT_TYPE"] != "SOD  "]  # These are at 23:59 when there is no flying and ACFT are in the hangars.
df = df[df["REPORT_TYPE"] != "SOM  "]  # Same as "SOD" but at the end of the month.


def Source_A():
    df["DATE"] = pd.to_datetime(df["DATE"])
    labels = ["HourlyAltimeterSetting", "HourlyDewPointTemperature", "HourlyDryBulbTemperature",
              "HourlyPrecipitation", "HourlyPresentWeatherType", "HourlyRelativeHumidity", "HourlySkyConditions",
              "HourlyVisibility", "HourlyWindDirection", "HourlyWindGustSpeed", "HourlyWindSpeed"]
    df.index = df["DATE"]

    return df[labels]

df_A = Source_A()
print(df_A.head())

# There is an additional timestamp on the METAR reports that needs to be removed.
def extract_metar_text(line):
    return re.sub(r'^MET\w+\s\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ', '', str(line))


df["REM"] = df["REM"].apply(extract_metar_text)

# The metar needs to be decoded separately
# The metar is a single string that encodes multiple datapoints.
def decode_metar(metar):
    result = {"station": None, "datetime_utc": None,
              "wind": None, "visibility": None,
              "temperature": None, "dew_point": None,
              "pressure": None}
    try:
        parts = metar.strip().split()

        # Station ID is typically first
        result["station"] = parts[0]

        # Observation time (UTC) not including the year or month
        obs_time_match = re.search(r'\b(\d{6})Z\b', metar)
        if obs_time_match:
            result["datetime_utc"] = obs_time_match.group(1)

        # Wind heading and speed (knots)
        wind_match = re.search(r'\b(\d{3})(\d{2})KT\b', metar)
        if wind_match:
            result["wind"] = f"{wind_match.group(1)}° at {wind_match.group(2)} kt"

        # Visibility (SM)
        vis_match = re.search(r'\b(\d{1,2})SM\b', metar)
        if vis_match:
            result["visibility"] = f"{vis_match.group(1)} SM"

        # Temperature/dew point (C)
        temp_dew_match = re.search(r'\b(M?\d{2})/(M?\d{2})\b', metar)
        if temp_dew_match:
            temp = temp_dew_match.group(1).replace('M', '-')
            dew = temp_dew_match.group(2).replace('M', '-')
            result["temperature"] = f"{temp} °C"
            result["dew_point"] = f"{dew} °C"

        # Pressure (inHg)
        press_match = re.search(r'\bA(\d{4})\b', metar)
        if press_match:
            inches = press_match.group(1)
            result["pressure"] = f"{inches[:2]}.{inches[2:]} inHg"

    except Exception as e:
        result["error"] = str(e)

    return result

# The decoded metar is parsed into a df
def df_B():
    decoded = df["REM"].apply(decode_metar)
    df_B = pd.json_normalize(decoded)
    labels = ["wind", "visibility", "temperature", "dew_point", "pressure"]
    df_B = df_B[labels]
    df_B.index = df["DATE"]

    return df_B

df_B()




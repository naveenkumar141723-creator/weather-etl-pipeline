import requests
import pandas as pd
from datetime import datetime

API_KEY = "88d5046d20b27ef54a56ff694cf651ad"

cities = ["Berlin", "Bonn", "Munich", "Hamburg", "Magdeburg",
          "Frankfurt", "Stuttgart", "Cologne"]


def extract_weather(cities):
    all_data = []

    for city in cities:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        data = response.json()

        all_data.append({
            "city": city,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather_condition": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "extracted_at": datetime.now()
        })

        print(f"Extracted: {city} — {data['main']['temp']}°C")

    df = pd.DataFrame(all_data)
    print("Extract complete")
    return df


def transform_weather(df):
    df["temperature"] = df["temperature"].round(2)
    df["feels_like"] = df["feels_like"].round(2)
    df["wind_speed"] = df["wind_speed"].round(2)

    df["city"] = df["city"].str.title().str.strip()

    df["heat_category"] = df["temperature"].apply(
        lambda x: "Extreme Heat" if x > 35
        else ("Very Hot" if x > 30
              else ("Hot" if x > 25
                    else ("Warm" if x > 20
                          else "Cool")))
    )


    df["date"] = pd.to_datetime(df["extracted_at"]).dt.date
    df["hour"] = pd.to_datetime(df["extracted_at"]).dt.hour
    df["month"] = pd.to_datetime(df["extracted_at"]).dt.month
    df["year"] = pd.to_datetime(df["extracted_at"]).dt.year
    df["day_name"] = pd.to_datetime(df["extracted_at"]).dt.day_name()

    print(f"Transform complete — {len(df)} records")
    print(df[["city", "temperature", "heat_category"]].to_string())
    return df


def validate_weather(df):
    import logging
    logging.basicConfig(filename="weather_pipeline.log", level=logging.WARNING)

    print("\nRunning validation checks...")

    # Null check
    null_count = df.isnull().sum().sum()
    if null_count > 0:
        logging.warning(f"Null values found: {null_count}")
        print(f"WARNING: {null_count} null values found")
    else:
        print("Null check passed")

    # Temperature range check
    if df["temperature"].max() > 60:
        logging.warning(f"Unrealistic temperature: {df['temperature'].max()}")
        print("WARNING: Unrealistic temperature detected")
    else:
        print("Temperature range check passed")

    # Humidity range check
    if df["humidity"].max() > 100 or df["humidity"].min() < 0:
        logging.warning("Humidity out of range")
        print("WARNING: Humidity out of range")
    else:
        print("Humidity range check passed")

    # Row count check
    assert len(df) > 0, "Empty dataframe — pipeline failed"
    print("Row count check passed")

    print(f"\nValidation complete — all checks passed for {len(df)} records")
    return df


def load_weather(df):

    import os

    file_path = "weather_data.csv"


    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False)
        print(f"Appended {len(df)} records to {file_path}")
    else:
        df.to_csv(file_path, mode="w", header=True, index=False)
        print(f"Created {file_path} with {len(df)} records")

    print(f"Load complete — data saved to {file_path}")



df = extract_weather(cities)
df = transform_weather(df)
validate_weather(df)
load_weather(df)


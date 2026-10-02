import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import URL, create_engine

# MySQL connection
conn_str = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="admin123",
    host="localhost",
    port=3306,
    database="ride_booking"
)
engine = create_engine(conn_str)

# Load ride-booking data
df = pd.read_sql("SELECT * FROM ncr_ride_bookings", engine)

# Basic validation
print("Shape:", df.shape)
print("Duplicate rows:", df.duplicated().sum())
print("\nMissing values:\n", df.isna().sum())

# Data types
print("\nData types:\n", df.dtypes)

# Convert date/time fields
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Time"] = pd.to_datetime(df["Time"], errors="coerce").dt.time

# Numeric columns
numeric_cols = [
    "Avg VTAT", "Avg CTAT", "Booking Value", "Ride Distance",
    "Driver Ratings", "Customer Rating"
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# IQR outlier check
def iqr_outliers(data, column):
    s = data[column].dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return data[(data[column] < lower) | (data[column] > upper)]

for col in ["Booking Value", "Ride Distance"]:
    if col in df.columns:
        print(f"{col} outliers:", len(iqr_outliers(df, col)))

# EDA summaries
print("\nBooking status:\n", df["Booking Status"].value_counts())
print("\nVehicle type:\n", df["Vehicle Type"].value_counts())
print("\nPayment method:\n", df["Payment Method"].value_counts())

# Monthly booking trend
if "Month" in df.columns:
    monthly = df.groupby("Month").size().sort_values(ascending=False)
    print("\nBookings by month:\n", monthly)

# Peak booking hours
if "Hour" in df.columns:
    print("\nBookings by hour:\n", df["Hour"].value_counts().sort_index())

# KPI summaries
kpis = {
    "Total Bookings": len(df),
    "Total Revenue": df["Booking Value"].sum(),
    "Average Booking Value": df["Booking Value"].mean(),
    "Average Ride Distance": df["Ride Distance"].mean(),
    "Average Driver Rating": df["Driver Ratings"].mean(),
    "Average Customer Rating": df["Customer Rating"].mean()
}
print("\nKPIs:\n", pd.Series(kpis))

# Power BI-ready cleaned export
df.to_csv("Ride_Booking_Cleaned.csv", index=False)
print("\nCleaned dataset exported as Ride_Booking_Cleaned.csv")

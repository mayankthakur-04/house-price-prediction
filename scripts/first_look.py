import pandas as pd

df = pd.read_csv("data/raw/AmesHousing.csv")

print("Shape:", df.shape)
print("\nColumn names:")
print(list(df.columns))

print("\nDtype counts:")
print(df.dtypes.value_counts())

print("\nMissing values (top 15):")
print(df.isna().sum().sort_values(ascending=False).head(15))

print("\nFully duplicated rows:", df.duplicated().sum())
if "PID" in df.columns:
    print("Repeated PID (same parcel):", df["PID"].duplicated().sum())

target = [c for c in df.columns if c.replace(" ", "").lower() == "saleprice"][0]
print("\nTarget column:", target)
print(df[target].describe())
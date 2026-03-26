import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib

# 1. Load data
df = pd.read_csv('data.csv', skiprows=3)

# CLEANING: Remove any leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Print columns to terminal so you can see exactly what Pandas sees
print("Detected Columns:", df.columns.tolist())

# 2. Identify the correct columns even if the names are slightly different
# We search for names that START with 'Price' or 'Commodity'
price_col = [c for c in df.columns if 'Price' in c and '2026-27' in c]
commodity_col = [c for c in df.columns if 'Commodity' in c]

if not price_col or not commodity_col:
    # Fallback: Try using the index if names are totally messed up
    # Based on your CSV screenshot, Commodity is likely index 1, Price is index 4
    target_price = df.columns[4] 
    target_commodity = df.columns[1]
else:
    target_price = price_col[0]
    target_commodity = commodity_col[0]

print(f"Using '{target_commodity}' as features and '{target_price}' as target.")

# 3. Final Cleaning
df = df.dropna(subset=[target_price, target_commodity])

# 4. Encoding
le_commodity = LabelEncoder()
df['Commodity_Num'] = le_commodity.fit_transform(df[target_commodity])

X = df[['Commodity_Num']]
y = pd.to_numeric(df[target_price], errors='coerce').fillna(0)

# 5. Train
model = LinearRegression()
model.fit(X, y)

# 6. Save
joblib.dump(model, 'crop_price_model.pkl')
joblib.dump(le_commodity, 'commodity_encoder.pkl')

print("✅ Success! AI Model trained and saved.")
import sqlite3
import pandas as pd

def upload_csv_to_db(csv_file_path):
    conn = sqlite3.connect("farmers.db")
    cursor = conn.cursor()

    try:
        # Load the CSV
        df = pd.read_csv(csv_file_path)
        
        # We strip spaces from column names just in case
        df.columns = [c.strip() for c in df.columns]

        for index, row in df.iterrows():
            # YOUR DATA MAPPING:
            # We use .iloc to pick by position so we don't get 'KeyErrors' anymore
            # row.iloc[1] is 'Commodity'
            # row.iloc[3] is 'Price on 17 Mar, 2026'
            
            commodity = row.iloc[1]
            price = row.iloc[3] 
            
            # Default values for your startup logic
            state = "India (National)"
            district = "Multiple"
            market = "Central Market"
            date = "2026-03-17"

            cursor.execute("""
                INSERT INTO market_prices (state, district, market_name, commodity, modal_price, arrival_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (state, district, market, commodity, price, date))
        
        conn.commit()
        print(f"✅ SUCCESS! Uploaded {len(df)} records to the FarmConnect database.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    upload_csv_to_db("data.csv")
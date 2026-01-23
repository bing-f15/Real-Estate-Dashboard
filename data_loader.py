import pandas as pd
import numpy as np

def load_data(file_path):
    """
    Load and clean the real estate data.
    """
    try:
        # Read the file
        # The file is comma separated but values are quoted.
        # Header is on line 0 (1st line).
        df = pd.read_csv(file_path, quotechar='"', skipinitialspace=True)
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Function to clean currency/area strings
        def clean_currency(x):
            if isinstance(x, str):
                return pd.to_numeric(x.replace('AED', '').replace(',', '').strip(), errors='coerce')
            return x

        def clean_area(x):
            if isinstance(x, str):
                # Handle '-' as NaN
                if x.strip() == '-':
                    return np.nan
                return pd.to_numeric(x.replace('sqm', '').replace(',', '').strip(), errors='coerce')
            return x
            
        def clean_rate(x):
             if isinstance(x, str):
                if x.strip() == '-' or x.strip() == '':
                    return np.nan
                return pd.to_numeric(x.replace('AED/sqm', '').replace(',', '').strip(), errors='coerce')
             return x

        # Clean Price
        df['Price (AED)'] = df['Price (AED)'].apply(clean_currency)
        
        # Clean Areas
        df['Sold Area (sqm)'] = df['Sold Area (sqm)'].apply(clean_area)
        df['Plot Area (sqm)'] = df['Plot Area (sqm)'].apply(clean_area)
        
        # Clean Rate
        df['Rate (AED/sqm)'] = df['Rate (AED/sqm)'].apply(clean_rate)
        
        # Clean Registration Date
        df['Registration'] = pd.to_datetime(df['Registration'], dayfirst=True, errors='coerce')
        
        # Calculate derived Rate if missing
        # Prefer Sold Area, then Plot Area
        df['Effective Area'] = df['Sold Area (sqm)'].fillna(df['Plot Area (sqm)'])
        
        # Calculate Rate where missing
        # Note: We are assuming Price is for the given Share.
        # To get a comparable Market Rate (Valuation Rate), strictly we should assume 
        # Rate = (Price / Share_Percentage) / Area  OR Price / (Area * Share_Percentage)
        # However, 'Share' column is string like '50%'.
        def clean_share(x):
            if isinstance(x, str):
                return pd.to_numeric(x.replace('%', '').strip(), errors='coerce') / 100.0
            return 1.0 # Default to 100% if missing/numeric 1

        df['Share_Value'] = df['Share'].apply(clean_share).fillna(1.0)
        
        # Calculated Rate = Price / (Effective Area * Share_Value)
        # Avoid division by zero
        mask = (df['Rate (AED/sqm)'].isna()) & (df['Effective Area'] > 0) & (df['Price (AED)'] > 0)
        df.loc[mask, 'Rate (AED/sqm)'] = df.loc[mask, 'Price (AED)'] / (df.loc[mask, 'Effective Area'] * df.loc[mask, 'Share_Value'])
        
        # Drop rows where we still don't have a valid Rate or Price or Registration date?
        # For the dashboard, we might want to keep them but filter in charts.
        # Let's keep them and handle in charts.
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

if __name__ == "__main__":
    # Test loading
    df = load_data('d:/AI Projects/recent_sales.txt')
    if df is not None:
        print("Data loaded successfully.")
        print(df.head())
        print(df.info())
    else:
        print("Failed to load data.")

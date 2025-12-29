import pandas as pd
from sqlalchemy import create_engine
import pymysql

# --- Local XAMPP Configuration ---
LOCAL_DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'job_portal_user_behavior_dataset',  # ✅ Updated DB Name
    'port': 3306
}


def load_data(local_config=LOCAL_DB_CONFIG):
    """
    Connects to the local MySQL database, fetches data from the combined 2025 table,
    renames columns for clarity, and returns it as a Pandas DataFrame.
    """
    local_conn_str = (
        f"mysql+pymysql://{local_config['user']}:{local_config['password']}"
        f"@{local_config['host']}:{local_config['port']}/{local_config['database']}"
    )

    try:
        print(f"🔄 Connecting to Local Database ({local_config['database']})...")
        local_engine = create_engine(local_conn_str)

        # --- UPDATED QUERY ---
        # Target the new combined table
        table_name = "aj_subscription_job_stats_combined_2025"

        # We filter by timeCreatedAtUTC to ensure we have valid time data
        query = f"SELECT * FROM {table_name} WHERE timeCreatedAtUTC IS NOT NULL;"

        df = pd.read_sql(query, con=local_engine)

        if df.empty:
            print(f"⚠️ Table '{table_name}' is empty.")
            return df

        # --- RENAME COLUMNS ---
        # Mapping raw SQL column names to Analysis-Friendly names
        column_mapping = {
            'record_id': 'Unique_Row_ID',  # The new Auto-Increment ID
            'id': 'Original_Source_ID',  # The ID from the remote DB (may have duplicates)
            'source_table': 'Data_Source_Month',  # e.g., '2025_01'

            'adTitle': 'Job_Title',
            'category': 'Job_Category',
            'companyName': 'Company',
            'companyEmail': 'Company_Email',
            'adStatus': 'Ad_Status',

            'totalViewCount': 'Total_Views',
            'totalApplied': 'Total_Applications',
            'outboundClicks': 'Outbound_Clicks',

            'userID': 'User_ID',
            'customerID': 'Customer_ID',
            'productID': 'Product_ID',
            'subscriptionID': 'Subscription_ID',

            'timeCreatedAtUTC': 'Created_At',
            'adRunTimeStart': 'Run_Start_Date',
            'adRunTimeEnd': 'Run_End_Date',
            'detailViewLink': 'Job_URL',
            'Country':'Country'
        }

        # Apply the renaming
        df.rename(columns=column_mapping, inplace=True)

        # Optional: Convert date columns to datetime objects immediately
        if 'Created_At' in df.columns:
            df['Created_At'] = pd.to_datetime(df['Created_At'])

        print(f"✅ Success! Loaded {len(df)} rows from '{table_name}'.")
        return df

    except Exception as e:
        print(f"❌ Error fetching data from local SQL: {e}")
        return None


if __name__ == "__main__":
    df_result = load_data()

    if df_result is not None:
        print("\n--- DataFrame Info ---")
        print(df_result.info())

        print("\n--- Sample Data (First 5 Rows) ---")
        print(df_result.head())

        # Verify we have data from multiple months
        if 'Data_Source_Month' in df_result.columns:
            print("\n--- Row Count by Month ---")
            print(df_result['Data_Source_Month'].value_counts())
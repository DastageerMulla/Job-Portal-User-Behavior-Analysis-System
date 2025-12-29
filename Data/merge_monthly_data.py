import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv()

REMOTE_CONFIG = {
    'host': os.getenv('SQL_HOST'),
    'user': os.getenv('SQL_USER'),
    'pass': os.getenv('SQL_PASSWORD'),
    'db': os.getenv('SQL_DATABASE')
}

LOCAL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'pass': '',
    'db': 'job_portal_user_behavior_dataset',  # ✅ Check DB Name
    'table': 'aj_subscription_job_stats_combined_2025'
}


def run_etl_process():
    # 1. Connect to Remote
    if not REMOTE_CONFIG['host']:
        print("❌ Error: .env variables not loaded.")
        return

    remote_conn_str = f"mysql+pymysql://{REMOTE_CONFIG['user']}:{REMOTE_CONFIG['pass']}@{REMOTE_CONFIG['host']}/{REMOTE_CONFIG['db']}"

    try:
        remote_engine = create_engine(remote_conn_str)
        print(f"🔄 Connecting to Remote SQL...")

        all_data = []

        # 2. Loop Months 1-12
        for i in range(1, 13):
            month_suffix = f"{i:02d}"
            table_name = f"aj_subscription_job_powerBI_stats_2025_{month_suffix}"

            print(f"   🔎 Fetching {table_name}...", end=" ")

            try:
                query = f"SELECT * FROM {table_name}"
                with remote_engine.connect() as conn:
                    df = pd.read_sql(query, conn)

                if not df.empty:
                    df['source_table'] = table_name
                    all_data.append(df)
                    print(f"✅ Found {len(df)} rows.")
                else:
                    print("⚠️ Empty.")
            except Exception:
                print("❌ Table not found (Skipping).")

        if not all_data:
            print("\n❌ No data found.")
            return

        # 3. Combine Data
        final_df = pd.concat(all_data, ignore_index=True)
        print(f"\n✅ TOTAL ROWS: {len(final_df)}")

        # --- 4. SAVE TO LOCAL (UPDATED LOGIC) ---
        local_conn_str = f"mysql+pymysql://{LOCAL_CONFIG['user']}:{LOCAL_CONFIG['pass']}@{LOCAL_CONFIG['host']}/{LOCAL_CONFIG['db']}"
        local_engine = create_engine(local_conn_str)

        print(f"🔄 Connecting to Local XAMPP...")

        # A. Clean Data
        df_clean = final_df.replace({np.nan: None})

        # B. ⚠️ WE KEEP THE 'id' COLUMN NOW ⚠️
        # Since we created 'record_id' as the new primary key in SQL,
        # we can safely insert the old 'id' without errors.
        print("ℹ️  Preserving original 'id' column (mapped to non-primary column)...")

        with local_engine.connect() as conn:
            print(f"🧹 Clearing table '{LOCAL_CONFIG['table']}'...")
            conn.execute(text(f"TRUNCATE TABLE {LOCAL_CONFIG['table']}"))
            conn.commit()

            print(f"🚀 Inserting {len(df_clean)} rows...")
            df_clean.to_sql(
                name=LOCAL_CONFIG['table'],
                con=conn,
                if_exists='append',
                index=False,
                chunksize=1000
            )
            conn.commit()

        print("✅ SUCCESS! All data saved. 'record_id' is the new unique key.")

        # Verification
        print("\n--- 📊 DATA VERIFICATION ---")
        print(df_clean['source_table'].value_counts())

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_etl_process()
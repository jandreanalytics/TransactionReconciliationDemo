"""
Reconciliation script to analyze discrepancies between POS and processor data
This version reads databases directly from AWS S3
"""
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import boto3
from io import BytesIO
from datetime import datetime, timedelta
import tempfile

# Load environment variables from .env file
load_dotenv()

# Verify AWS credentials are loaded
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

if not all([aws_access_key, aws_secret_key, aws_region]):
    raise EnvironmentError("AWS credentials not found in environment variables")

# Initialize AWS session with credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

def ensure_directory_exists(path):
    """Make sure the directory exists for output files"""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def download_db_from_s3(bucket, key, local_path=None):
    """Download SQLite database from S3 to a local temporary file"""
    s3 = session.client('s3')  # Use the session we created
    
    if local_path is None:
        # Create a temporary file
        local_path = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
    
    print(f"Downloading {key} from S3 bucket {bucket} to {local_path}")
    s3.download_file(bucket, key, local_path)
    
    return local_path

def upload_results_to_s3(local_path, bucket, key):
    """Upload results file to S3"""
    s3 = session.client('s3')
    print(f"Uploading {local_path} to S3 bucket {bucket} as {key}")
    s3.upload_file(local_path, bucket, key)

def main():
    print("Starting Gift Card Transaction Reconciliation...\n")
    
    # Set up visualization styling
    sns.set(style="whitegrid")
    plt.rcParams['figure.figsize'] = [12, 8]
    
    # Get project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.normpath(os.path.join(script_dir, '..', '..'))
    db_dir = os.path.join(project_root, 'data', 'db')
    processed_dir = os.path.join(project_root, 'data', 'processed')
    
    # Ensure directories exist
    os.makedirs(db_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    try:
        # AWS credentials working, proceed with S3 access
        bucket_name = "gift-card-demo-processed"
        pos_db_key = "pos_system.db"
        proc_db_key = "processor.db"
        
        print(f"Accessing databases from AWS S3...")
        
        # Try to download files directly instead of checking bucket access
        pos_db_path = download_db_from_s3(bucket_name, pos_db_key)
        proc_db_path = download_db_from_s3(bucket_name, proc_db_key)
        
    except Exception as e:
        print("Error connecting to AWS. Please verify your credentials and permissions.")
        print(f"Error details: {str(e)}")
        print("\nFalling back to local database files...")
        
        # Use local database files instead
        pos_db_path = os.path.join(db_dir, "pos_system.db")
        proc_db_path = os.path.join(db_dir, "processor.db")
        
        if not all(os.path.exists(p) for p in [pos_db_path, proc_db_path]):
            raise FileNotFoundError("Local database files not found. Please ensure databases are in data/db directory.")
    
    # Connect to POS database and load transactions
    pos_conn = sqlite3.connect(pos_db_path)
    pos_transactions = pd.read_sql("SELECT * FROM transactions", pos_conn)
    
    # Connect to processor database and load transactions
    proc_conn = sqlite3.connect(proc_db_path)
    proc_transactions = pd.read_sql("SELECT * FROM transactions", proc_conn)
    
    # Display basic info
    print(f"\nPOS Transactions: {len(pos_transactions)}")
    print(f"Processor Transactions: {len(proc_transactions)}")
    
    print("\n----- Transaction Matching & Reconciliation -----")
    
    # Create a merged dataset for reconciliation
    # Match processor transactions to POS using reference_id
    reconciled = pd.merge(
        pos_transactions,
        proc_transactions,
        left_on='transaction_id',
        right_on='reference_id',
        how='outer',
        suffixes=('_pos', '_proc')
    )
    
    print(f"Total records after merge: {len(reconciled)}")
    
    print("\n----- Identifying Discrepancies -----")
    
    # Flag different types of discrepancies
    
    # 1. Missing transactions (in POS but not processor)
    missing_in_processor = reconciled[reconciled['transaction_id_proc'].isna()].copy()
    print(f"Missing in processor: {len(missing_in_processor)} transactions")
    
    # 2. Amount discrepancies
    # Fix the SettingWithCopyWarning
    # Create a proper copy for matched transactions
    matched = reconciled.dropna(subset=['transaction_id_pos', 'transaction_id_proc']).copy()
    # Use loc for assignment
    matched.loc[:, 'amount_diff'] = matched['amount_pos'] - matched['amount_proc']
    amount_issues = matched[abs(matched['amount_diff']) > 0.01].copy()
    print(f"Amount discrepancies: {len(amount_issues)} transactions")
    
    # 3. Identify likely decimal shift errors
    amount_issues['decimal_shift'] = (
        (abs(amount_issues['amount_pos'] * 10 - amount_issues['amount_proc']) < 0.01) | 
        (abs(amount_issues['amount_pos'] / 10 - amount_issues['amount_proc']) < 0.01)
    )
    decimal_shifts = amount_issues[amount_issues['decimal_shift']]
    print(f"Decimal shift errors: {len(decimal_shifts)} transactions")
    
    print("\n----- Creating Visualizations -----")
    
    # Create a summary of discrepancy types
    discrepancy_counts = {
        'Missing in Processor': len(missing_in_processor),
        'Amount Discrepancies': len(amount_issues) - len(decimal_shifts),
        'Decimal Shift Errors': len(decimal_shifts),
        'Matched Correctly': len(matched) - len(amount_issues)
    }
    
    # Create output directory for visuals
    os.makedirs('data/processed', exist_ok=True)
    
    # Create a pie chart of discrepancy types
    plt.figure(figsize=(10, 8))
    plt.pie(
        discrepancy_counts.values(), 
        labels=discrepancy_counts.keys(),
        autopct='%1.1f%%', 
        startangle=90,
        explode=[0.05, 0.05, 0.2, 0],
        shadow=True
    )
    plt.title('Transaction Reconciliation Results', fontsize=16)
    plt.tight_layout()
    
    # Save the chart
    chart_path = "data/processed/reconciliation_chart.png"
    plt.savefig(chart_path)
    print(f"Saved visualization to {chart_path}")
    
    print("\n----- Exporting Reconciliation Results -----")
    
    # Add discrepancy type column
    reconciled['discrepancy_type'] = 'None'
    reconciled.loc[reconciled['transaction_id_proc'].isna(), 'discrepancy_type'] = 'Missing in Processor'
    reconciled.loc[reconciled['transaction_id_pos'].isna(), 'discrepancy_type'] = 'Missing in POS'
    
    # Mark amount discrepancies where both transactions exist
    matched_mask = ~(reconciled['transaction_id_pos'].isna() | reconciled['transaction_id_proc'].isna())
    reconciled.loc[matched_mask, 'amount_diff'] = reconciled.loc[matched_mask, 'amount_pos'] - reconciled.loc[matched_mask, 'amount_proc']
    
    # Flag decimal shift errors
    decimal_shift_mask = matched_mask & (
        (abs(reconciled['amount_pos'] * 10 - reconciled['amount_proc']) < 0.01) | 
        (abs(reconciled['amount_pos'] / 10 - reconciled['amount_proc']) < 0.01)
    )
    reconciled.loc[decimal_shift_mask, 'discrepancy_type'] = 'Decimal Shift'
    
    # Flag other amount discrepancies
    amount_diff_mask = matched_mask & (abs(reconciled['amount_diff']) > 0.01) & ~decimal_shift_mask
    reconciled.loc[amount_diff_mask, 'discrepancy_type'] = 'Amount Discrepancy'
    
    # Save results to S3
    results_local_path = "data/processed/reconciliation_results.csv"
    ensure_directory_exists(results_local_path)
    reconciled.to_csv(results_local_path, index=False)
    
    # Upload results to S3 - store in a results folder
    results_s3_key = "results/reconciliation_results.csv"
    upload_results_to_s3(results_local_path, bucket_name, results_s3_key)
    print(f"Reconciliation results uploaded to S3: s3://{bucket_name}/{results_s3_key}")
    
    # Generate summary statistics
    summary = {
        'Total POS Transactions': len(pos_transactions),
        'Total Processor Transactions': len(proc_transactions),
        'POS Amount Total': pos_transactions['amount'].sum(),
        'Processor Amount Total': proc_transactions['amount'].sum(),
        'Net Amount Difference': pos_transactions['amount'].sum() - proc_transactions['amount'].sum(),
        'Missing in Processor': len(missing_in_processor),
        'Decimal Shift Errors': len(decimal_shifts),
        'Other Amount Discrepancies': len(amount_issues) - len(decimal_shifts),
        'Perfectly Matched': len(matched) - len(amount_issues)
    }
    
    # Create summary table
    summary_df = pd.DataFrame.from_dict(summary, orient='index', columns=['Value'])
    
    # Format and display summary
    print("\n----- Reconciliation Summary Report -----\n")
    for index, row in summary_df.iterrows():
        value = row['Value']
        if isinstance(value, float):
            print(f"{index}: ${value:.2f}")
        else:
            print(f"{index}: {value}")
            
    # Save summary to file
    summary_path = "data/processed/reconciliation_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("Transaction Reconciliation Summary\n")
        f.write("=================================\n\n")
        for index, row in summary_df.iterrows():
            value = row['Value']
            if isinstance(value, float):
                f.write(f"{index}: ${value:.2f}\n")
            else:
                f.write(f"{index}: {value}\n")
                
    print(f"\nSummary saved to {summary_path}")
    
    # Upload chart to S3
    chart_local_path = "data/processed/reconciliation_chart.png"
    chart_s3_key = "results/reconciliation_chart.png"
    upload_results_to_s3(chart_local_path, bucket_name, chart_s3_key)
    print(f"Chart uploaded to S3: s3://{bucket_name}/{chart_s3_key}")
    
    # Clean up temporary files
    if os.path.exists(pos_db_path):
        os.unlink(pos_db_path)
    if os.path.exists(proc_db_path):
        os.unlink(proc_db_path)
    
    print("\n----- Reconciliation Complete -----")
    print("""
Next steps would include:
- Working with the processor to locate missing transactions
- Implementing decimal validation in transaction processing
- Investigating specific causes of amount discrepancies
- Setting up automated daily reconciliation to catch issues sooner
    """)

if __name__ == "__main__":
    main()

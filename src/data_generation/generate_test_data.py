"""
Main script to generate test data for gift card reconciliation
"""
import os
import pandas as pd
import random
from datetime import datetime, timedelta
import uuid
from config import STORE_CONFIG, CARD_CONFIG, TRANSACTION_TYPES, ERROR_CONFIG, generate_reference_id
from utils import (
    generate_card_number, 
    generate_transaction_time,
    calculate_processor_delay,
    should_inject_error,
    apply_decimal_shift
)

def create_gift_card_pool(count=None):
    """Generate a pool of gift cards"""
    if count is None:
        count = CARD_CONFIG['initial_pool_size']
    
    cards = []
    
    # TODO: Implement gift card generation
    # 1. Generate card_number using generate_card_number()
    # 2. Pick random amount from CARD_CONFIG['denominations']
    # 3. Set activation_date to random recent date
    # 4. Set status from CARD_CONFIG['status_types']
    
    return pd.DataFrame(cards)

def generate_transactions(gift_cards, transaction_count=5000):
    """
    Generate transaction data for both POS and processor systems
    
    Parameters:
    - gift_cards: DataFrame of gift cards
    - transaction_count: Number of transactions to generate
    
    Returns:
    - tuple of (pos_transactions, processor_transactions)
    """
    # Create empty lists for transactions
    pos_transactions = []
    processor_transactions = []
    
    # TODO: Implement transaction generation
    # 1. For each transaction, select random card from gift_cards
    # 2. Generate transaction details (amount, time, type)
    # 3. Create POS transaction record
    # 4. Create matching processor record with appropriate delay
    # 5. Apply error injection based on ERROR_CONFIG
    
    return pd.DataFrame(pos_transactions), pd.DataFrame(processor_transactions)

def inject_errors(pos_df, processor_df):
    """
    Add specific error scenarios to the data
    
    Parameters:
    - pos_df: POS transactions DataFrame
    - processor_df: Processor transactions DataFrame
    
    Returns:
    - Modified DataFrames with injected errors
    """
    # Make copies to avoid modifying originals
    pos = pos_df.copy()
    processor = processor_df.copy()
    
    # TODO: Implement specific error injections:
    # 1. Missing transactions (remove from processor)
    # 2. Double charges (duplicate in POS)
    # 3. Amount mismatches (change amount in processor)
    # 4. Extreme timing differences
    
    return pos, processor

def export_to_csv(pos_df, processor_df, output_dir='../../data/raw'):
    """Export DataFrames to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    pos_df.to_csv(f"{output_dir}/pos_transactions.csv", index=False)
    processor_df.to_csv(f"{output_dir}/processor_transactions.csv", index=False)
    
    print(f"Exported {len(pos_df)} POS transactions and {len(processor_df)} processor transactions")

def main():
    """Main function to generate test data"""
    print("Generating gift card pool...")
    gift_cards = create_gift_card_pool()
    
    print("Generating transactions...")
    pos_transactions, processor_transactions = generate_transactions(gift_cards)
    
    print("Injecting errors...")
    pos_transactions, processor_transactions = inject_errors(pos_transactions, processor_transactions)
    
    print("Exporting to CSV...")
    export_to_csv(pos_transactions, processor_transactions)
    
    print("Done!")

if __name__ == "__main__":
    main()

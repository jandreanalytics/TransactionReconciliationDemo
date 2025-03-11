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
    apply_decimal_shift,
    generate_realistic_transaction_amount,
    is_weekend,
    generate_transaction_id,
    generate_processor_transaction_id,
    generate_authorization_code,
    generate_batch_id,
    calculate_card_balance,
    convert_timezone,
    get_terminal_id
)

def create_gift_card_pool(count=None):
    """Generate a pool of gift cards"""
    if count is None:
        count = CARD_CONFIG['initial_pool_size']
    
    # Use current date as reference
    today = datetime.now()
    
    # Create list for gift cards
    cards = []
    
    # Generate cards with different patterns
    card_patterns = list(CARD_CONFIG['patterns'].keys())
    
    # List to keep track of card numbers to avoid duplicates
    card_numbers = set()
    
    for _ in range(count):
        # Choose a random pattern for more variety
        pattern_key = random.choice(card_patterns)
        
        # Generate unique card number
        card_number = None
        while card_number is None or card_number in card_numbers:
            card_number = generate_card_number(pattern_key)
        
        card_numbers.add(card_number)
        
        # Select denomination from config
        initial_balance = random.choice(CARD_CONFIG['denominations'])
        
        # Generate activation date within last 90 days
        days_ago = random.randint(1, 90)
        activation_date = today - timedelta(days=days_ago)
        
        # Add business hour constraint to activation time
        activation_timestamp = generate_transaction_time(activation_date)
        
        # Select status (mostly active, some inactive/redeemed)
        status_weights = [0.85, 0.10, 0.05]  # Active, Inactive, Redeemed
        status = random.choices(CARD_CONFIG['status_types'][:3], weights=status_weights)[0]
        
        # Create card record
        card = {
            'card_id': card_number,
            'initial_balance': initial_balance,
            'current_balance': initial_balance if status != 'REDEEMED' else 0.00,
            'status': status,
            'activation_date': activation_timestamp,
            'last_updated': activation_timestamp,
            'pattern_type': pattern_key
        }
        
        cards.append(card)
    
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
    
    # Use only active cards for transactions
    active_cards = gift_cards[gift_cards['status'] == 'ACTIVE'].copy()
    
    if active_cards.empty:
        raise ValueError("No active gift cards available for transactions")
    
    # Track current balances for each card
    card_balances = {row['card_id']: row['current_balance'] for _, row in active_cards.iterrows()}
    card_transactions = {card_id: [] for card_id in card_balances.keys()}
    
    # Reference date (today)
    today = datetime.now()
    
    # Generate transactions until we reach the desired count
    actual_count = 0
    max_attempts = transaction_count * 3  # Allow more attempts to reach target
    attempts = 0
    
    print(f"Attempting to generate {transaction_count} transactions...")
    
    while actual_count < transaction_count and attempts < max_attempts:
        attempts += 1
        
        # Select a random card
        card_id = random.choice(list(card_balances.keys()))
        current_balance = card_balances[card_id]
        
        # Determine transaction type
        tx_type_options = [
            TRANSACTION_TYPES['purchase'], 
            TRANSACTION_TYPES['refund'],
            TRANSACTION_TYPES['balance_check']
        ]
        weights = [0.85, 0.10, 0.05]  # 85% purchases, 10% refunds, 5% balance checks
        transaction_type = random.choices(tx_type_options, weights=weights)[0]
        
        # Generate transaction date in the past 30 days
        days_ago = random.randint(0, 30)
        tx_date = today - timedelta(days=days_ago)
        
        # Adjust transaction volume based on weekends - reduce skip probability
        if is_weekend(tx_date) and random.random() > 0.7:  # Changed from 0.5 to 0.7
            # Skip some transactions to simulate lower weekend volume
            continue
            
        # Generate transaction time based on business hours
        tx_timestamp = generate_transaction_time(tx_date)
        
        # Generate transaction amount based on type
        if transaction_type == TRANSACTION_TYPES['purchase']:
            # For purchase, limit by available balance
            max_amount = min(current_balance, 100.00)
            
            # Lower minimum amount to allow more transactions
            min_amount = 1.00  # Changed from 5.00 to 1.00
            
            if max_amount < min_amount:
                # For low balances, allow smaller purchases or refunds
                if random.random() < 0.5:
                    transaction_type = TRANSACTION_TYPES['refund']
                    amount = generate_realistic_transaction_amount(1.00, 10.00)
                    card_balances[card_id] += amount
                else:
                    # Skip this attempt
                    continue
            else:
                amount = generate_realistic_transaction_amount(min_amount, max_amount)
                # Ensure positive amount for purchase (will be deducted)
                amount = abs(amount)
                # Update balance
                card_balances[card_id] -= amount
            
        elif transaction_type == TRANSACTION_TYPES['refund']:
            # Refunds are typically smaller
            amount = generate_realistic_transaction_amount(1.00, 50.00)  # Changed minimum from 5.00 to 1.00
            
            # Update balance
            card_balances[card_id] += amount
            
        else:  # Balance check
            amount = 0.00
        
        # Generate transaction IDs
        tx_id = generate_transaction_id(prefix="TX", system="POS")
        
        # Get batch ID (same day transactions are batched together)
        batch_id = generate_batch_id(date=tx_timestamp)
        
        # Generate authorization code
        auth_code = generate_authorization_code()
        
        # Create POS transaction
        pos_tx = {
            'transaction_id': tx_id,
            'card_id': card_id,
            'amount': amount,
            'transaction_type': transaction_type,
            'timestamp': tx_timestamp,
            'store_id': STORE_CONFIG['store_id'],
            'terminal_id': get_terminal_id(),
            'batch_id': batch_id,
            'authorization_code': auth_code,
            'status': 'APPROVED',
            'balance_after': card_balances[card_id]
        }
        
        pos_transactions.append(pos_tx)
        card_transactions[card_id].append({
            'amount': amount,
            'type': transaction_type
        })
        
        # Create matching processor transaction with slight delay
        delay_seconds = calculate_processor_delay()
        processor_timestamp = tx_timestamp + timedelta(seconds=delay_seconds)
        
        # Generate processor transaction ID based on POS ID
        processor_tx_id = generate_processor_transaction_id(tx_id)
        
        # Processor may record slightly different data
        processor_tx = {
            'transaction_id': processor_tx_id,
            'reference_id': tx_id,  # Links back to POS transaction
            'card_id': card_id,
            'amount': amount,  # Will be modified later for error injection
            'transaction_type': transaction_type,
            'processed_at': processor_timestamp,
            'merchant_id': STORE_CONFIG['store_id'],
            'terminal_id': pos_tx['terminal_id'],
            'batch_id': batch_id,
            'authorization_code': auth_code,
            'status': 'SETTLED'
        }
        
        processor_transactions.append(processor_tx)
        actual_count += 1
        
        # Print progress indicator every 1000 transactions
        if actual_count % 1000 == 0:
            print(f"Generated {actual_count} of {transaction_count} transactions...")
    
    print(f"Generated {actual_count} transactions in {attempts} attempts")
    
    # Convert to DataFrames
    pos_df = pd.DataFrame(pos_transactions)
    processor_df = pd.DataFrame(processor_transactions)
    
    return pos_df, processor_df

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
    
    # Record counts for summary
    total_transactions = len(pos)
    error_counts = {
        'missing': 0,
        'decimal_shift': 0,
        'double_charge': 0,
        'timing_mismatch': 0,
        'wrong_amount': 0
    }
    
    # 1. Missing Transaction Errors
    if total_transactions > 10:  # Ensure we have enough transactions
        # Choose random transactions to be missing from processor
        missing_count = int(total_transactions * ERROR_CONFIG['rates']['missing_transaction'])
        missing_indices = random.sample(range(len(processor)), missing_count)
        
        # Remove these transactions from processor
        processor = processor.drop(missing_indices).reset_index(drop=True)
        error_counts['missing'] = missing_count
    
    # 2. Decimal Shift Errors
    # Find purchase transactions for possible amount errors
    purchase_mask = processor['transaction_type'] == TRANSACTION_TYPES['purchase']
    purchase_indices = processor[purchase_mask].index.tolist()
    
    if purchase_indices:
        # Choose random transactions for decimal errors
        decimal_shift_count = int(len(purchase_indices) * ERROR_CONFIG['rates']['decimal_shift'])
        decimal_shift_indices = random.sample(purchase_indices, min(decimal_shift_count, len(purchase_indices)))
        
        # Apply decimal shift to these transactions
        for idx in decimal_shift_indices:
            original_amount = processor.at[idx, 'amount']
            shifted_amount = apply_decimal_shift(original_amount, error_probability=1.0)  # Force shift
            processor.at[idx, 'amount'] = shifted_amount
            
        error_counts['decimal_shift'] = len(decimal_shift_indices)
    
    # 3. Double Charge Errors
    # Duplicate some POS transactions
    if len(pos) > 20:  # Ensure we have enough transactions
        double_charge_count = int(len(pos) * ERROR_CONFIG['rates']['double_charge'])
        double_charge_indices = random.sample(range(len(pos)), double_charge_count)
        
        double_charges = []
        for idx in double_charge_indices:
            duplicate = pos.iloc[idx].copy()
            # Change transaction ID slightly (e.g., add -DUP suffix)
            original_id = duplicate['transaction_id']
            duplicate['transaction_id'] = f"{original_id}-DUP"
            
            # Adjust timestamp slightly (a few seconds later)
            duplicate['timestamp'] = duplicate['timestamp'] + timedelta(seconds=random.randint(60, 180))
            
            double_charges.append(duplicate)
        
        # Add duplicates to POS transactions
        pos = pd.concat([pos, pd.DataFrame(double_charges)], ignore_index=True)
        error_counts['double_charge'] = len(double_charges)
    
    # 4. Random Amount Errors (small adjustments)
    amount_error_count = int(len(processor) * ERROR_CONFIG['rates']['wrong_amount'])
    if amount_error_count > 0:
        amount_error_indices = random.sample(range(len(processor)), amount_error_count)
        
        for idx in amount_error_indices:
            # Small random adjustment to amount (±5%)
            original_amount = processor.at[idx, 'amount']
            adjustment = original_amount * random.uniform(-0.05, 0.05)  # ±5% 
            processor.at[idx, 'amount'] = round(original_amount + adjustment, 2)
            
        error_counts['wrong_amount'] = amount_error_count
    
    # 5. Extreme Timing Differences
    timing_error_count = int(len(processor) * ERROR_CONFIG['rates']['timing_mismatch'])
    if timing_error_count > 0:
        timing_error_indices = random.sample(range(len(processor)), timing_error_count)
        
        for idx in timing_error_indices:
            # Add a large delay (hours instead of seconds)
            delay_hours = random.randint(1, 24)  # 1-24 hours delay
            processor.at[idx, 'processed_at'] = processor.at[idx, 'processed_at'] + timedelta(hours=delay_hours)
            
        error_counts['timing_mismatch'] = timing_error_count
    
    # Print error summary
    print("\nError Injection Summary:")
    for error_type, count in error_counts.items():
        print(f"  {error_type}: {count} errors ({count/total_transactions*100:.1f}%)")
    print(f"Total Transactions: {total_transactions}")
    
    return pos, processor

def export_to_csv(pos_df, processor_df, output_dir=None):
    """Export DataFrames to CSV files"""
    # Use a relative path pointing to the raw data directory
    if output_dir is None:
        # Get directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate up to project root, then into data/raw
        output_dir = os.path.normpath(os.path.join(script_dir, '..', '..', 'data', 'raw'))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to CSV
    pos_df.to_csv(os.path.join(output_dir, "pos_transactions.csv"), index=False)
    processor_df.to_csv(os.path.join(output_dir, "processor_transactions.csv"), index=False)
    
    print(f"Exported {len(pos_df)} POS transactions and {len(processor_df)} processor transactions to {output_dir}")
    print(f"Full path: {os.path.abspath(output_dir)}")
    
    # Save summary data
    summary = {
        'pos_count': len(pos_df),
        'processor_count': len(processor_df),
        'difference': len(pos_df) - len(processor_df),
        'pos_total': pos_df['amount'].sum(),
        'processor_total': processor_df['amount'].sum(),
        'amount_difference': pos_df['amount'].sum() - processor_df['amount'].sum()
    }
    
    with open(os.path.join(output_dir, "summary.txt"), 'w') as f:
        f.write("Transaction Reconciliation Summary\n")
        f.write("=================================\n\n")
        f.write(f"POS Transactions: {summary['pos_count']}\n")
        f.write(f"Processor Transactions: {summary['processor_count']}\n")
        f.write(f"Count Difference: {summary['difference']}\n\n")
        f.write(f"POS Total Amount: ${summary['pos_total']:.2f}\n")
        f.write(f"Processor Total Amount: ${summary['processor_total']:.2f}\n")
        f.write(f"Amount Difference: ${summary['amount_difference']:.2f}\n")

def main():
    """Main function to generate test data"""
    print("Generating gift card pool...")
    
    # Ensure we have enough cards with sufficient balances
    gift_cards = create_gift_card_pool(count=1000)  # Increased from 500 to 1000
    
    # Increase initial balances for more transaction capacity
    gift_cards['initial_balance'] = gift_cards['initial_balance'] * 2
    gift_cards['current_balance'] = gift_cards['current_balance'] * 2
    
    print(f"Generated {len(gift_cards)} gift cards")
    
    # Get directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to project root, then into data/raw
    output_dir = os.path.normpath(os.path.join(script_dir, '..', '..', 'data', 'raw'))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save gift card data
    gift_cards.to_csv(os.path.join(output_dir, "gift_cards.csv"), index=False)
    print(f"Saved gift cards to {output_dir}")
    
    print("Generating transactions...")
    pos_transactions, processor_transactions = generate_transactions(gift_cards, transaction_count=25000)  # Increased to 25,000
    print(f"Generated {len(pos_transactions)} POS transactions")
    
    print("Injecting errors...")
    pos_transactions, processor_transactions = inject_errors(pos_transactions, processor_transactions)
    
    print("Exporting to CSV...")
    export_to_csv(pos_transactions, processor_transactions, output_dir)
    
    print("Done!")

if __name__ == "__main__":
    main()

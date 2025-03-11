"""
Utility functions for gift card data generation
"""
import random
from datetime import datetime, timedelta
import string
from config import STORE_CONFIG, CARD_CONFIG, ERROR_CONFIG, TRANSACTION_TYPES

# Simplify card number generation
def generate_card_number(pattern_key='store', store_id=None):
    """Generate a card number using the pattern specified in config"""
    if store_id is None:
        store_id = STORE_CONFIG['store_id']
    
    # Simple pattern-based generation
    if pattern_key == 'retail':
        # Simpler retail pattern (no formatting complexity)
        digits = random.randint(1000000000000000, 9999999999999999)
        return str(digits)
    
    elif pattern_key == 'store':
        # Basic store pattern
        digits = random.randint(1000, 9999)
        return f"GC-{store_id}-{digits}"
    
    elif pattern_key == 'amazon':
        # Simplified Amazon pattern
        chars = ''.join(random.choices(string.ascii_uppercase, k=4))
        digits = random.randint(1000, 9999)
        return f"{chars}-{digits}"
    
    # Default fallback
    return f"CARD-{random.randint(10000, 99999)}"

# Keep this function simple
def is_business_hours(timestamp):
    """Check if timestamp is during business hours"""
    hour = timestamp.hour
    return STORE_CONFIG['hours']['open'] <= hour < STORE_CONFIG['hours']['close']

# Simplify transaction time generation
def generate_transaction_time(base_date):
    """Generate transaction timestamp during business hours"""
    # Basic business hour constraint
    store_open = STORE_CONFIG['hours']['open']
    store_close = STORE_CONFIG['hours']['close']
    
    # Simple random hour selection
    hour = random.randint(store_open, store_close - 1)
    # Peak hours get higher probability (basic implementation)
    for start, end in STORE_CONFIG['peak_hours']:
        if random.random() < 0.6:  # 60% chance to use peak hours
            hour = random.randint(start, end - 1)
            break
    
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return datetime(
        year=base_date.year, 
        month=base_date.month, 
        day=base_date.day, 
        hour=hour, 
        minute=minute, 
        second=second
    )

# Basic delay calculator
def calculate_processor_delay():
    """Calculate delay between POS and processor timestamps"""
    # Simplify to basic delay - no complex logic
    if random.random() < 0.1:  # 10% chance of longer delay
        return random.randint(30, 120)  # 30-120 seconds
    return random.randint(1, 10)  # 1-10 seconds normally

# Straightforward error chance function
def should_inject_error(error_type):
    """Determine if an error should occur"""
    error_rate = ERROR_CONFIG['rates'].get(error_type, 0.0)
    return random.random() < error_rate

def apply_decimal_shift(amount, error_probability=None):
    """
    Sometimes shift decimal point to create realistic errors
    
    Parameters:
    - amount: original amount
    - error_probability: override default error rate if specified
    
    Returns:
    - amount (possibly with decimal shifted)
    """
    # Use default error rate if none provided
    if error_probability is None:
        error_probability = ERROR_CONFIG['rates']['decimal_shift']
    
    # Determine if we should shift the decimal
    if random.random() < error_probability:
        # Choose a shift direction (multiply or divide)
        if random.choice([True, False]):
            # Multiply by 10 (shift right)
            return amount * 10
        else:
            # Divide by 10 (shift left)
            return amount / 10
    
    # No shift
    return amount

def generate_realistic_transaction_amount(min_amount=5.00, max_amount=150.00):
    """
    Generate a realistic transaction amount
    
    Parameters:
    - min_amount: Minimum transaction amount
    - max_amount: Maximum transaction amount
    
    Returns:
    - A realistic looking transaction amount (e.g., $19.99, $25.50)
    """
    # Common price endings
    price_patterns = [
        lambda x: round(x, 2),           # Regular rounding (e.g., 24.87)
        lambda x: round(x - 0.01, 0) + 0.99,  # $X.99 pattern
        lambda x: round(x, 0) - 0.01,    # $X9.99 pattern
        lambda x: round(x * 2) / 2,      # $X.50 pattern
        lambda x: round(x, 0),           # Whole dollars
    ]
    
    # Choose a pattern with weights
    weights = [0.2, 0.35, 0.15, 0.15, 0.15]  # $X.99 is most common
    pattern = random.choices(price_patterns, weights=weights)[0]
    
    # Generate base amount
    base_amount = random.uniform(min_amount, max_amount)
    
    # Apply the chosen pattern
    amount = pattern(base_amount)
    
    # Ensure within bounds
    amount = max(min_amount, min(amount, max_amount))
    
    return round(amount, 2)

def is_weekend(date):
    """Check if a date is on a weekend"""
    # 5 = Saturday, 6 = Sunday
    return date.weekday() >= 5

def generate_transaction_id(prefix="TXN", system="POS"):
    """
    Generate a unique transaction ID
    
    Parameters:
    - prefix: Transaction ID prefix
    - system: System identifier (POS or PROC)
    
    Returns:
    - Unique transaction ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    random_part = ''.join(random.choices('0123456789', k=6))
    return f"{prefix}-{system}-{timestamp}-{random_part}"

def generate_processor_transaction_id(pos_id):
    """
    Generate a processor transaction ID based on POS ID
    
    Parameters:
    - pos_id: Original POS transaction ID
    
    Returns:
    - Matching processor transaction ID
    """
    # Extract components from original ID
    parts = pos_id.split('-')
    
    if len(parts) >= 3:
        # Replace POS with PROC
        parts[1] = 'PROC'
        return '-'.join(parts)
    else:
        # If ID format isn't as expected, generate a new one
        return generate_transaction_id(prefix=parts[0], system="PROC")

def generate_authorization_code():
    """
    Generate a realistic authorization code
    
    Returns:
    - Authorization code string
    """
    # Format options
    formats = [
        # Alpha-numeric format
        lambda: ''.join(random.choices(string.ascii_uppercase, k=1)) + 
                ''.join(random.choices('0123456789', k=5)),
        # Numeric format
        lambda: ''.join(random.choices('0123456789', k=6)),
        # Letter-number-letter format
        lambda: ''.join(random.choices(string.ascii_uppercase, k=2)) + 
                ''.join(random.choices('0123456789', k=4))
    ]
    
    # Choose a format randomly
    chosen_format = random.choice(formats)
    return chosen_format()

def generate_batch_id(store_id=None, date=None):
    """
    Generate a batch ID for transaction grouping
    
    Parameters:
    - store_id: The store identifier
    - date: The batch date
    
    Returns:
    - Batch ID string
    """
    if store_id is None:
        store_id = STORE_CONFIG['store_id']
        
    if date is None:
        date = datetime.now()
        
    date_part = date.strftime("%Y%m%d")
    batch_num = random.randint(1, 9)
    
    return f"BATCH-{store_id}-{date_part}-{batch_num}"

def calculate_card_balance(initial_balance, transactions):
    """
    Calculate current card balance based on transaction history
    
    Parameters:
    - initial_balance: Starting balance
    - transactions: List of transaction dictionaries with amount and type
    
    Returns:
    - Current balance
    """
    balance = initial_balance
    
    for txn in transactions:
        amount = txn.get('amount', 0)
        txn_type = txn.get('type', '')
        
        if txn_type == TRANSACTION_TYPES['purchase']:
            balance -= amount
        elif txn_type == TRANSACTION_TYPES['refund']:
            balance += amount
        elif txn_type == TRANSACTION_TYPES['reload']:
            balance += amount
            
    # Ensure non-negative balance (gift cards don't go below zero)
    return max(0, round(balance, 2))

def convert_timezone(timestamp, hours_offset):
    """
    Convert timestamp between time zones
    
    Parameters:
    - timestamp: Original datetime
    - hours_offset: Hours to add/subtract
    
    Returns:
    - Adjusted datetime
    """
    return timestamp + timedelta(hours=hours_offset)

def get_terminal_id():
    """
    Get random terminal ID from config
    
    Returns:
    - Terminal ID string
    """
    return random.choice(STORE_CONFIG['terminals'])

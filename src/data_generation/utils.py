"""
Utility functions for gift card data generation
"""
import random
from datetime import datetime, timedelta
import string
import uuid
from config import STORE_CONFIG, CARD_CONFIG, ERROR_CONFIG, TRANSACTION_TYPES

def generate_card_number(pattern_key='store', store_id=None):
    """
    Generate a card number using the pattern specified in config
    
    Parameters:
    - pattern_key: Which pattern from CARD_CONFIG to use
    - store_id: Override store ID if needed
    
    Returns:
    - A formatted card number string
    """
    if store_id is None:
        store_id = STORE_CONFIG['store_id']
    
    # Get the pattern from config
    pattern = CARD_CONFIG['patterns'].get(pattern_key)
    
    if not pattern:
        raise ValueError(f"Pattern key '{pattern_key}' not found in CARD_CONFIG")
    
    # Generate random digits based on the pattern
    if pattern_key == 'retail':
        # For retail pattern with 3 groups of 4 digits
        digits_1 = random.randint(1000, 9999)
        digits_2 = random.randint(1000, 9999)
        digits_3 = random.randint(1000, 9999)
        return f"6073-{digits_1:04d}-{digits_2:04d}-{digits_3:04d}"
    
    elif pattern_key == 'store':
        # For store-specific pattern
        digits = random.randint(1, 999999)
        return pattern.format(store=store_id, digits=digits)
    
    elif pattern_key == 'amazon':
        # For Amazon-style alphanumeric pattern
        char_part = ''.join(random.choices(string.ascii_uppercase, k=2))
        digits_1 = random.randint(10, 99)
        char_part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        digits_2 = random.randint(1000, 9999)
        return f"{char_part}{digits_1}-{char_part2}-{digits_2}"
    
    elif pattern_key == 'microsoft':
        # For Microsoft-style pattern
        digits_1 = random.randint(1000, 9999)
        chars = ''.join(random.choices(string.ascii_uppercase, k=4))
        digits_2 = random.randint(1000, 9999)
        return f"MSFT-{digits_1:04d}-{chars}-{digits_2:04d}"
    
    # Default fallback - just use a simple format
    return f"GC-{random.randint(100000, 999999)}"

def is_business_hours(timestamp):
    """
    Check if timestamp is during business hours
    
    Parameters:
    - timestamp: datetime object
    
    Returns:
    - Boolean: True if within business hours
    """
    # Extract the hour from timestamp
    hour = timestamp.hour
    
    # Check if hour is within business hours
    return STORE_CONFIG['hours']['open'] <= hour < STORE_CONFIG['hours']['close']

def generate_transaction_time(base_date, peak_hour_bias=0.7):
    """
    Generate realistic transaction timestamp biased toward peak hours
    
    Parameters:
    - base_date: date to use
    - peak_hour_bias: probability of transaction during peak hours (0.0-1.0)
    
    Returns:
    - datetime object with realistic transaction time
    """
    # Decide whether to use peak hours based on bias
    use_peak_hours = random.random() < peak_hour_bias
    
    if use_peak_hours:
        # Choose one of the peak hour ranges randomly
        peak_range = random.choice(STORE_CONFIG['peak_hours'])
        # Select a random hour within that range
        hour = random.randint(peak_range[0], peak_range[1] - 1)
    else:
        # Select a random hour within business hours, excluding peak hours
        store_open = STORE_CONFIG['hours']['open']
        store_close = STORE_CONFIG['hours']['close']
        
        # Create a list of all business hours
        all_hours = list(range(store_open, store_close))
        
        # Remove peak hours from the list
        for peak_start, peak_end in STORE_CONFIG['peak_hours']:
            for h in range(peak_start, peak_end):
                if h in all_hours:
                    all_hours.remove(h)
        
        # Select a random hour from remaining business hours
        if all_hours:  # Make sure we have non-peak hours
            hour = random.choice(all_hours)
        else:
            # Fallback if all business hours are peak hours
            hour = random.randint(store_open, store_close - 1)
    
    # Generate random minute and second
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    # Combine with base_date
    return datetime(
        year=base_date.year, 
        month=base_date.month, 
        day=base_date.day, 
        hour=hour, 
        minute=minute, 
        second=second
    )

def calculate_processor_delay(error_rate=None):
    """
    Calculate realistic delay between POS and processor timestamps
    
    Parameters:
    - error_rate: if specified, chance of problematic delay
    
    Returns:
    - delay in seconds
    """
    # Determine if we should use normal or delayed timing
    if error_rate is None:
        error_rate = ERROR_CONFIG['rates']['timing_mismatch']
    
    # Determine if this transaction has a timing issue
    has_timing_issue = random.random() < error_rate
    
    if has_timing_issue:
        # Use the delayed timing range
        min_delay, max_delay = ERROR_CONFIG['timing_delays']['delayed']
    else:
        # Use the normal timing range
        min_delay, max_delay = ERROR_CONFIG['timing_delays']['normal']
    
    # Return a random delay within the appropriate range
    return random.randint(min_delay, max_delay)

def should_inject_error(error_type):
    """
    Determine if a specific error should be injected
    
    Parameters:
    - error_type: type of error from ERROR_CONFIG['rates']
    
    Returns:
    - Boolean: True if error should be injected
    """
    if error_type not in ERROR_CONFIG['rates']:
        return False
    
    # Get error rate for this type
    error_rate = ERROR_CONFIG['rates'][error_type]
    
    # Randomly determine if we should inject the error
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

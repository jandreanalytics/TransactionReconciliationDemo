"""
Configuration for gift card data generation
"""
import random
import string

# Business Rules
STORE_CONFIG = {
    'hours': {
        'open': 8,   # 8 AM
        'close': 22  # 10 PM
    },
    'peak_hours': [
        (11, 14),  # Lunch rush
        (17, 20)   # Dinner rush
    ],
    'weekend_multiplier': 1.5,  # 50% more transactions on weekends
    'store_id': 'STORE-0512',
    'terminals': [f"POS-{i:03d}" for i in range(1, 6)]  # 5 terminals
}

# Gift card denomination research based on market statistics
CARD_CONFIG = {
    'denominations': [
        # Common standard amounts
        25.00, 50.00, 100.00,
        # Special occasion amounts
        75.00, 150.00, 200.00,
        # Smaller increments
        10.00, 15.00, 20.00,
        # Marketing price points
        19.99, 49.99, 99.99
    ],
    'patterns': {
        # Standard retail format (16-digit numeric)
        'retail': '6073-{digits:04d}-{digits:04d}-{digits:04d}',
        
        # Store-specific format
        'store': 'GC-{store}-{digits:06d}',
        
        # Amazon-style alphanumeric format
        'amazon': '{char:2}{digits:02d}-{char:6}-{digits:04d}',

        # Microsoft-style alphanumeric format
        'microsoft': 'MSFT-{digits:4d}-{char:4}-{digits:4d}'
    },
    'initial_pool_size': 1000,
    'status_types': [
        'ACTIVE',     # Card is ready for use
        'INACTIVE',   # Card created but not yet activated
        'REDEEMED'    # Fully used
        'PENDING'     # Activation in progress
        'EXPIRED'     # Past expiration date
        'CANCELLED'   # Deactivated by customer service
    ]
}

# Error rates based on industry statistics (slightly exaggerated for demo)
ERROR_CONFIG = {
    'rates': {
        'decimal_shift': 0.03,    # Decimal point error (3%)
        'double_charge': 0.02,    # Same transaction appears twice (2%)
        'missing_transaction': 0.05,  # Transaction missing from processor (5%)
        'timing_mismatch': 0.05,  # Significant time difference (5%)
        'wrong_amount': 0.03,     # Different amount in processor vs POS (3%)
        'system_crash': 0.01,     # Processor failure (1%)
    },
    'timing_delays': {
        'normal': (1, 5),      # 1-5 seconds between systems (normal)
        'delayed': (30, 120),   # 30-120 seconds (problematic delay)
        'missing': (300, 600)  # 5-10 minutes (missing transaction)
    }
}

# Transaction types from real-world gift card systems
TRANSACTION_TYPES = {
    'activation': 'ACTIVATE',       # Initial card activation
    'purchase': 'PURCHASE',         # Standard purchase with card
    'refund': 'REFUND',             # Money returned to card
    'balance_check': 'BALANCE',     # Check remaining balance
    'reload': 'RELOAD',             # Add more funds to card
    'void': 'VOID',                 # Cancel a transaction
    'partial_auth': 'PARTIAL_AUTH', # Only part of requested amount approved
    'load_fee': 'LOAD_FEE',          # Fee for activating/loading card
    'no_auth': 'NO_AUTH'            # Transaction declined
}

# Generate reference IDs for transactions
def generate_reference_id(prefix, length=10):
    """Generate a reference ID with given prefix and random digits"""
    digits = ''.join(random.choices('0123456789', k=length))
    return f"{prefix}{digits}"

# Helper function for amazon-style card generation
def generate_alphanumeric(length):
    """Generate random alphanumeric string of given length"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

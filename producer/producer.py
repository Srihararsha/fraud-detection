import pandas as pd
import numpy as np
import json
import time
import os
import sys
from datetime import datetime
import random
import uuid

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create transactions directory if it doesn't exist
transactions_dir = os.path.join(project_root, 'transactions')
os.makedirs(transactions_dir, exist_ok=True)

# Transaction amount ranges
AMOUNT_RANGES = {
    'small': (0.01, 50.00),
    'medium': (50.01, 200.00),
    'large': (200.01, 1000.00),
    'very_large': (1000.01, 5000.00)
}

# Fraud probability by amount range
FRAUD_PROBABILITIES = {
    'small': 0.3,    # 30% chance of fraud for small amounts
    'medium': 0.4,   # 40% chance of fraud for medium amounts
    'large': 0.6,    # 60% chance of fraud for large amounts
    'very_large': 0.7  # 70% chance of fraud for very large amounts
}

def load_dataset():
    """Load and prepare the dataset."""
    try:
        data_path = os.path.join(project_root, 'data', 'creditcard.csv')
        df = pd.read_csv(data_path)
        
        # Verify required columns exist
        required_columns = ['Time', 'Amount', 'Class'] + [f'V{i+1}' for i in range(28)]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
        # Filter out invalid amounts
        df = df[df['Amount'] > 0]
        
        return df
    except Exception as e:
        print(f"Error loading dataset: {str(e)}")
        sys.exit(1)

def generate_realistic_amount():
    """Generate a realistic transaction amount."""
    # Select amount range based on probability
    range_weights = [0.5, 0.3, 0.15, 0.05]  # Higher probability for smaller amounts
    amount_range = random.choices(
        list(AMOUNT_RANGES.keys()),
        weights=range_weights,
        k=1
    )[0]
    
    min_amount, max_amount = AMOUNT_RANGES[amount_range]
    
    # Generate amount with 2 decimal places
    amount = round(random.uniform(min_amount, max_amount), 2)
    
    # Sometimes round to .99 or .95 for more realistic prices
    if random.random() < 0.3:  # 30% chance
        amount = round(amount, 0) - 0.01
    
    return amount, amount_range

def generate_transaction(df):
    """Generate a random transaction with realistic amounts and fraud patterns."""
    try:
        # Generate realistic amount
        amount, amount_range = generate_realistic_amount()
        
        # Determine if this should be a fraud based on amount range
        is_fraud = random.random() < FRAUD_PROBABILITIES[amount_range]
        
        # Select a random row for features
        row = df.sample(n=1).iloc[0]
        
        # Extract features (V1-V28)
        features = {f'V{i+1}': float(row[f'V{i+1}']) for i in range(28)}
        
        # Add Time and Amount features
        current_time = datetime.now()
        features['Time'] = float(current_time.hour)  # Hour of day
        features['Amount'] = float(amount)
        
        # Create transaction with unique ID
        transaction = {
            'id': str(uuid.uuid4()),
            'timestamp': current_time.isoformat(),
            'amount': amount,
            'is_fraud': int(is_fraud),
            'features': features
        }
        
        return transaction
    except Exception as e:
        print(f"Error generating transaction: {str(e)}")
        return None

def save_transaction(transaction):
    """Save transaction to a JSON file."""
    try:
        if transaction is None:
            return False
            
        # Generate unique filename using transaction ID
        filename = f'transaction_{transaction["id"]}.json'
        filepath = os.path.join(transactions_dir, filename)
        
        # Save transaction
        with open(filepath, 'w') as f:
            json.dump(transaction, f)
            
        return True
    except Exception as e:
        print(f"Error saving transaction: {str(e)}")
        return False

def cleanup_old_files():
    """Clean up old transaction files."""
    try:
        # Remove files older than 1 hour
        current_time = time.time()
        for file_path in os.listdir(transactions_dir):
            if file_path.startswith('transaction_') and file_path.endswith('.json'):
                full_path = os.path.join(transactions_dir, file_path)
                try:
                    if os.path.getmtime(full_path) < current_time - 3600:  # 1 hour
                        os.remove(full_path)
                except FileNotFoundError:
                    continue  # Skip if file was already deleted
                except Exception as e:
                    print(f"Error removing file {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error cleaning up old files: {str(e)}")

def main():
    """Main function to generate and save transactions."""
    print("Loading dataset...")
    df = load_dataset()
    print("Dataset loaded successfully!")
    
    print("\nStarting transaction generation...")
    print("Generating transactions with realistic amounts and fraud patterns...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Generate transaction
            transaction = generate_transaction(df)
            
            if transaction:
                # Save transaction
                if save_transaction(transaction):
                    status = "🚨 FRAUD" if transaction['is_fraud'] else "✅ LEGIT"
                    print(f"Generated {status} transaction: ${transaction['amount']:.2f} (ID: {transaction['id'][:8]})")
            
            # Cleanup old files
            cleanup_old_files()
            
            # Shorter delay for more frequent transactions
            time.sleep(random.uniform(0.2, 0.5))  # Random delay between 0.2 and 0.5 seconds
            
    except KeyboardInterrupt:
        print("\nStopping transaction generation...")
    except Exception as e:
        print(f"Error in main loop: {str(e)}")
    finally:
        print("Transaction generation stopped.")

if __name__ == "__main__":
    main() 
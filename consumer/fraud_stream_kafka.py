import streamlit as st
import json
import pandas as pd
import numpy as np
import tensorflow as tf
from datetime import datetime
import plotly.graph_objects as go
from collections import deque
import glob
import os
import time
import sys
import shutil

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add alerting module path
alerting_path = os.path.join(project_root, 'alerting')
if alerting_path not in sys.path:
    sys.path.insert(0, alerting_path)

from alert import send_sms_alert

# Create transactions directory if it doesn't exist
transactions_dir = os.path.join(project_root, 'transactions')
os.makedirs(transactions_dir, exist_ok=True)

# Load the trained model
model_path = os.path.join(project_root, 'model', 'fraud_model.h5')
try:
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    st.error(f"Failed to load model: {str(e)}")
    st.stop()

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = deque(maxlen=100)
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()
if 'total_transactions' not in st.session_state:
    st.session_state.total_transactions = 0
if 'fraud_count' not in st.session_state:
    st.session_state.fraud_count = 0
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()
if 'fraud_amount' not in st.session_state:
    st.session_state.fraud_amount = 0
if 'legit_amount' not in st.session_state:
    st.session_state.legit_amount = 0

# Set up the Streamlit page
st.set_page_config(page_title="Real-Time Fraud Detection", layout="wide")
st.title("Real-Time Fraud Detection Dashboard")

# Create columns for metrics
col1, col2, col3, col4 = st.columns(4)

def process_transaction(transaction):
    """Process a transaction and make fraud prediction."""
    try:
        # Extract features in the correct order
        features = []
        
        # Add Time and Amount as first two features
        features.append(float(transaction['timestamp'].split('T')[1].split(':')[0]))  # Hour
        features.append(float(transaction['amount']))
        
        # Add V1-V28 features
        for i in range(28):
            feature_name = f'V{i+1}'
            if feature_name in transaction['features']:
                features.append(transaction['features'][feature_name])
            else:
                features.append(0.0)  # Default value if feature is missing
        
        features = np.array(features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(features, verbose=0)[0][0]
        
        # Update metrics
        st.session_state.total_transactions += 1
        st.session_state.total_amount += transaction['amount']
        
        # Use both model prediction and actual fraud label
        is_fraud = prediction > 0.3 or transaction['is_fraud'] == 1
        
        # Store transaction with prediction
        transaction['prediction'] = float(prediction)
        transaction['is_fraud'] = is_fraud
        
        # Update fraud metrics
        if is_fraud:
            st.session_state.fraud_count += 1
            st.session_state.fraud_amount += transaction['amount']
            try:
                alert_message = (
                    f"🚨 FRAUD ALERT 🚨\n"
                    f"Amount: ${transaction['amount']:.2f}\n"
                    f"Time: {transaction['timestamp']}\n"
                    f"Fraud Probability: {prediction:.2%}\n"
                    f"Transaction ID: {transaction['id']}"
                )
                send_sms_alert(alert_message)
            except Exception as e:
                st.error(f"Failed to send SMS alert: {str(e)}")
        else:
            st.session_state.legit_amount += transaction['amount']
        
        # Add transaction to history
        st.session_state.transactions.append(transaction)
        
    except Exception as e:
        st.error(f"Error processing transaction: {str(e)}")
        print(f"Error processing transaction: {str(e)}")  # Add console logging

def update_dashboard():
    """Update the dashboard with latest metrics and visualizations."""
    try:
        # Update metrics
        col1.metric("Total Transactions", st.session_state.total_transactions)
        fraud_rate = (st.session_state.fraud_count / st.session_state.total_transactions * 100) if st.session_state.total_transactions > 0 else 0
        col2.metric("Fraud Rate", f"{fraud_rate:.1f}%")
        col3.metric("Total Amount", f"${st.session_state.total_amount:,.2f}")
        col4.metric("Fraud Amount", f"${st.session_state.fraud_amount:,.2f}")
        
        # Create transaction history plot
        if len(st.session_state.transactions) > 0:
            df = pd.DataFrame(list(st.session_state.transactions))
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Create figure with secondary y-axis
            fig = go.Figure()
            
            # Add legitimate transactions
            legit_df = df[~df['is_fraud']]
            if not legit_df.empty:
                fig.add_trace(go.Scatter(
                    x=legit_df['timestamp'],
                    y=legit_df['amount'],
                    mode='markers',
                    marker=dict(color='green', size=8),
                    name='Legitimate'
                ))
            
            # Add fraudulent transactions
            fraud_df = df[df['is_fraud']]
            if not fraud_df.empty:
                fig.add_trace(go.Scatter(
                    x=fraud_df['timestamp'],
                    y=fraud_df['amount'],
                    mode='markers',
                    marker=dict(color='red', size=8),
                    name='Fraudulent'
                ))
            
            fig.update_layout(
                title="Transaction History",
                xaxis_title="Time",
                yaxis_title="Amount ($)",
                showlegend=True,
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display recent transactions
            st.subheader("Recent Transactions")
            recent_df = pd.DataFrame(list(st.session_state.transactions)[-10:])
            recent_df['timestamp'] = pd.to_datetime(recent_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            recent_df['status'] = recent_df['is_fraud'].apply(lambda x: '🚨 FRAUD' if x else '✅ LEGIT')
            recent_df['probability'] = recent_df['prediction'].apply(lambda x: f"{x:.2%}")
            recent_df['id'] = recent_df['id'].apply(lambda x: x[:8])  # Show only first 8 chars of ID
            
            # Style the dataframe
            st.dataframe(
                recent_df[['timestamp', 'amount', 'status', 'probability', 'id']].style
                .applymap(lambda x: 'color: red' if 'FRAUD' in str(x) else 'color: green' if 'LEGIT' in str(x) else ''),
                hide_index=True
            )
            
    except Exception as e:
        st.error(f"Error updating dashboard: {str(e)}")

def cleanup_old_files():
    """Clean up old transaction files."""
    try:
        # Remove files older than 1 hour
        current_time = time.time()
        for file_path in glob.glob(os.path.join(transactions_dir, 'transaction_*.json')):
            try:
                if os.path.getmtime(file_path) < current_time - 3600:  # 1 hour
                    os.remove(file_path)
                    st.session_state.processed_files.discard(file_path)
            except FileNotFoundError:
                continue  # Skip if file was already deleted
            except Exception as e:
                print(f"Error removing file {file_path}: {str(e)}")
    except Exception as e:
        print(f"Error cleaning up old files: {str(e)}")

# Main dashboard loop
while True:
    try:
        # Get new transaction files
        transaction_files = glob.glob(os.path.join(transactions_dir, 'transaction_*.json'))
        
        # Process new files
        for file_path in transaction_files:
            if file_path not in st.session_state.processed_files:
                try:
                    with open(file_path, 'r') as f:
                        transaction = json.load(f)
                    
                    # Process transaction
                    process_transaction(transaction)
                    
                    # Mark file as processed
                    st.session_state.processed_files.add(file_path)
                    
                    # Remove processed file
                    try:
                        os.remove(file_path)
                    except FileNotFoundError:
                        continue  # Skip if file was already deleted
                    except Exception as e:
                        print(f"Error removing processed file {file_path}: {str(e)}")
                        
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue
        
        # Update dashboard every 0.5 seconds
        current_time = time.time()
        if current_time - st.session_state.last_update >= 0.5:
            update_dashboard()
            st.session_state.last_update = current_time
        
        # Cleanup old files
        cleanup_old_files()
        
        # Wait for a short time before next update
        time.sleep(0.1)
        
    except Exception as e:
        st.error(f"Error in main loop: {str(e)}")
        time.sleep(1)  # Wait before retrying 
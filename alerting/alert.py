import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
RECIPIENT_PHONE_NUMBER = os.getenv('RECIPIENT_PHONE_NUMBER')

def send_sms_alert(message):
    """
    Send SMS alert using Twilio without rate limiting.
    
    Args:
        message (str): The message to send
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    try:
        # Check if Twilio credentials are configured
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER]):
            print("⚠️ Twilio credentials not configured. Skipping SMS alert.")
            print("Please set the following environment variables:")
            print("- TWILIO_ACCOUNT_SID")
            print("- TWILIO_AUTH_TOKEN")
            print("- TWILIO_PHONE_NUMBER")
            print("- RECIPIENT_PHONE_NUMBER")
            return False
        
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send message
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER
        )
        
        print(f"✅ SMS alert sent successfully! SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send SMS alert: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    test_transaction = {
        'amount': 1000.00,
        'timestamp': '2024-03-14T12:00:00',
        'prediction': 0.95
    }
    send_sms_alert(f"🚨 FRAUD ALERT 🚨\nAmount: ${test_transaction['amount']:.2f}\nTime: {test_transaction['timestamp']}\nFraud Probability: {test_transaction['prediction']:.2%}") 
# Real-Time Fraud Detection System

A machine learning-based system for real-time credit card fraud detection with live dashboard and SMS alerts.

## 🚀 Features

- Real-time transaction monitoring
- Machine learning-based fraud detection
- Live Streamlit dashboard
- SMS alerts for fraud detection
- Simulated transaction generation
- High-accuracy fraud detection model

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Web browser (for viewing the dashboard)
- Twilio account (for SMS alerts)
- Git

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fraud-detection.git
   cd fraud-detection
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory with:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_number
   RECIPIENT_PHONE_NUMBER=your_phone_number
   ```

## 🚀 Running the System

1. Start the Streamlit dashboard:
   ```bash
   streamlit run consumer/fraud_stream_kafka.py
   ```
   Access the dashboard at: http://localhost:8501

2. In a new terminal, start the transaction producer:
   ```bash
   python producer/producer.py
   ```

3. Monitor the system:
   - View real-time metrics on the dashboard
   - Check terminal output for transaction logs
   - Receive SMS alerts for detected fraud

## 📁 Project Structure

```
fraud-detection/
├── producer/              # Transaction generation
│   └── producer.py       # Transaction producer script
├── consumer/             # Fraud detection
│   └── fraud_stream_kafka.py  # Streamlit dashboard
├── alerting/             # SMS notifications
│   └── alert.py         # Alert system
├── model/               # ML model
│   └── fraud_model.h5  # Trained model
├── data/               # Data files
│   └── creditcard.csv  # Sample data
├── transactions/       # Transaction storage
├── requirements.txt    # Project dependencies
├── setup.py           # Package setup
└── README.md          # Documentation
```

## 🔧 Configuration

### Fraud Detection Settings
- Detection threshold: 0.3 (configurable)
- SMS alert frequency: 60 seconds
- Transaction generation rate: 0.5-2 seconds
- Fraud simulation rate: 30%

### Model Specifications
- Framework: TensorFlow
- Input features: 30
- Model type: Neural Network
- Test accuracy: 99.83%

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Troubleshooting

### Common Issues

1. Import errors:
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check Python path configuration

2. Model errors:
   - Confirm model file exists in model/
   - Verify input feature dimensions
   - Check model loading process

3. SMS alert issues:
   - Validate Twilio credentials in .env
   - Check internet connection
   - Monitor rate limiting

## 📊 Performance Notes

- File-based transaction processing
- Rate-limited SMS alerts (1 per minute)
- Efficient model inference
- Real-time dashboard updates
- Memory-efficient storage (100 transaction limit)

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## 🙏 Acknowledgments

- TensorFlow team for the ML framework
- Streamlit for the dashboard framework
- Twilio for SMS capabilities 
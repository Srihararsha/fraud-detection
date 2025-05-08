from setuptools import setup, find_packages

setup(
    name="fraud-detection",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.32.0",
        "pandas==2.2.1",
        "numpy==1.26.4",
        "tensorflow==2.15.0",
        "plotly==5.19.0",
        "python-dotenv==1.0.1",
        "twilio==8.12.0",
    ],
) 
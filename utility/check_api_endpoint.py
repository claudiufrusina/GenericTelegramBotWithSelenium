import os
import requests

# Define the API endpoint
# url = 'https://api.telegram.org/bot<token>/getUpdates'
token = os.getenv('TELEGRAM_BOT_TOKEN')

url = f'https://api.telegram.org/bot{token}/getUpdates'

# Make the GET request
response = requests.get(url)

# Check the status code
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code}')
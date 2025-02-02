# Cruises Find project with selenium & telegram

## Overview

This project includes several Python scripts for interacting with the Telegram Bot API, automating browser actions using Selenium, and taking screenshots.

## Example of result in your Telegram chat bot

![Chat bot example](https://github.com/claudiufrusina/GenericTelegramBotWithSelenium/blob/main/utility/images/example.png)

## Installation

To install the required dependencies, run the following command:

```sh
pip install -r requirements.txt
```

## Project Structure

- 📄 **.env**: Contains environment variables such as `TELEGRAM_API_TOKEN`, `USER` & `PASSWORD`.
- 📝 **check_api_endpoint.py**: Script to check the Telegram API endpoint.
- 🌐 **check_infra.py**: Script to check network connectivity and send a test message via Telegram.
- 🔍 **find_telegram_chatId.py**: Script to find and print the Telegram chat ID.
- 📋 **requirements.txt**: List of dependencies required for the project.
- 📁 **screenshots**: Directory to store screenshots taken by the scripts.
- 🖥️ **script_selenium.py**: Script to automate browser actions and take screenshots using Selenium.
- 🤖 **telegram_bot_conn.py**: Script to send a screenshot to a Telegram bot.

## Usage

### 🤖 telegram_bot_conn.py

This script is the main to interface with the Telegram API endpoint.

```sh
python telegram_bot_conn.py
```

### 🌐 check_infra.py

This script checks network connectivity and sends a test message via Telegram.

### 🔍 find_telegram_chatId.py

This script finds and prints the Telegram chat ID.

### 🖥️ script_selenium.py

This script automates browser actions and takes screenshots using Selenium.

## Environment Variables

Create a .env file in the root directory with the following content:

Replace the placeholder values with your actual credentials.

## Activating the Virtual Environment

To create and activate a virtual environment, follow these steps:

1. Create a virtual environment:

```sh
python -m venv venv
- On Windows:
    .venv\Scripts\activate
- On macOS and Linux:
    source venv/bin/activate
```
To deactivate the virtual environment, simply run:
deactivate

## License

This project is licensed under the MIT License.

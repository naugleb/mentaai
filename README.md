# MentaAI - Mental Health Assistant Bot

MentaAI is an intelligent, NLP-based mental health assistant that utilizes large language models (LLMs) and the LangChain framework to offer intelligent and personalized mental health support. The primary goal of developing this assistant is to enhance accessibility to mental health care and reduce the burden on limited in-person therapy resources. The assistant provides immediate responses and support, detects emotions, responds to crises, and offer personalized advice. Utilizing Telegram as the platform ensures accessibility and privacy for users.

## Features
- Context-aware conversation with memory retention.
- Sentiment and emotion detection.
- Crisis response with immediate resources.
- Daily check-ins at scheduled intervals.

## Installation

### Prerequisites
- Python 3.9.12
- pip (Python package manager)

### Create and Activate a Virtual Environment
- Navigate to the Project Directory:
Before creating the virtual environment, make sure you are in the root directory of the project.

cd path\to\MentaAI

- Create the virtual environment:

python3.9.12 -m venv mentaAI

- Activate the virtual environment:

On Windows:
mentaAI\Scripts\activate

On macOS/Linux:
source mentaAI/bin/activate

### Install Dependencies
- pip install -r requirements.txt

### Set Up Environment Variables
- Create a .env file in the root directory of the project and add the following variables:

- TELEGRAM_TOKEN=<your-telegram-bot-token>
- OPENAI_API_KEY=<your-openai-api-key>
- PROXY=<your-proxy-url> 
- AWS_ACCESS_KEY_ID=<your-access-key> 
- AWS_SECRET_ACCESS_KEY=<your-secret-access-key> 

(.env file with all keys is provided for MSc Project examiners.)

### Run the Bot
- Navigate to the src directory:
Before running the bot, make sure you are in the src directory. This ensures that all file paths are correctly referenced.

cd MentaAI/src

- Run the bot:

python main.py

## Important Notice
This project is currently deployed on a live server. To avoid potential conflicts or disruptions in service, please refrain from running the bot locally on your machine.

Thank you for your cooperation.

## Usage
- Install Telegram app on your device
- Find the bot using the following link: https://t.me/MentaAI_bot
- Start the bot by sending the /start command.
- The bot will guide you through setting up your name and starting a conversation.


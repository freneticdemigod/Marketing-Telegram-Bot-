# AI Marketing Assistant Telegram Bot

A powerful Telegram bot that helps with digital marketing tasks using AI and real-time data scraping. The bot leverages Groq AI for intelligent responses and Selenium for web scraping capabilities.

## Features

- **Keyword Generation**: Generates targeted keywords based on:
  - Industry
  - Business objective
  - Website URL
  - Social media presence
  - Target audience
  - Geographic location

- **Industry Benchmarks**: 
  - Real-time scraping of marketing benchmarks
  - Provides industry-specific metrics:
    - Impressions
    - Click-Through Rate (CTR)
    - Cost Per Click (CPC)

- **Marketing FAQ**: 
  - AI-powered responses to marketing questions
  - Expert guidance on digital marketing strategies
  - Customized advice based on business context

## Prerequisites

```bash
# Required Python version
Python 3.7+

# Required packages
python-telegram-bot>=20.0
selenium
aiohttp
beautifulsoup4
requests
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/marketing-bot.git
cd marketing-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Chrome WebDriver:
- Install Google Chrome
- Install ChromeDriver matching your Chrome version
- Add ChromeDriver to your system PATH

4. Configure environment variables:
```bash
# Create a .env file and add your tokens
TELEGRAM_TOKEN="your_telegram_token"
GROQ_API_KEY="your_groq_api_key"
```

## Usage

1. Start the bot:
```bash
python bot.py
```

2. In Telegram:
- Search for your bot using its username
- Start a conversation with `/start`
- Choose from available options:
  - Generate Keywords
  - Industry Benchmarks
  - Marketing FAQ

## Bot Commands

- `/start` - Initialize the bot and show main menu
- Follow the interactive prompts for specific features

## Project Structure

```
marketing-bot/
│
├── bot.py                  # Main bot file
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # Documentation
```

## Feature Details

### Keyword Generation
The bot collects information about your business and generates relevant keywords using Groq AI. The process includes:
1. Industry selection
2. Business objective definition
3. Website and social media information
4. Target audience specification
5. Location targeting

### Industry Benchmarks
Real-time scraping of marketing benchmarks from industry sources, providing:
- Industry-specific impression data
- Average CTR rates
- Average CPC values

### Marketing FAQ
AI-powered responses to marketing questions, offering:
- Strategic advice
- Best practices
- Industry-specific recommendations

## Error Handling

The bot includes comprehensive error handling for:
- API failures
- Web scraping issues
- Invalid user inputs
- Connection problems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses Groq AI for intelligent responses
- Selenium for web scraping
- python-telegram-bot for Telegram integration

## Support

For support, email your-email@example.com or create an issue in the GitHub repository.

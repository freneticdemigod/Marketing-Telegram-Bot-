import logging
from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import aiohttp
from bs4 import BeautifulSoup
import json
from typing import List
import requests
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GroqAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_completion(self, messages):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": "mixtral-8x7b-32768",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error(f"Groq API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None

class BenchmarkScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

    async def fetch_benchmarks(self) -> dict:
        """Fetch industry benchmarks using Selenium"""
        # try:
        #     # Simulated benchmark data (replace with actual scraping in production)
        #     benchmarks = {
        #         'construction': {'cpc': 2.5, 'ctr': 3.17},
        #         'retail': {'cpc': 1.35, 'ctr': 2.69},
        #         'technology': {'cpc': 3.80, 'ctr': 2.41},
        #         'healthcare': {'cpc': 2.62, 'ctr': 2.83}
        #     }
        #     return benchmarks
        # except Exception as e:
        #     logger.error(f"Error fetching benchmarks: {e}")
        #     return {}
        url = 'http://databox.com/ppc-industry-benchmarks'
        response = requests.get(url)
    
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the CTR and CPC data for Facebook Ads
            facebook_ctr_table = soup.find_all('table')[0]
            facebook_cpc_table = soup.find_all('table')[1]
            facebook_data = self.extract_data(facebook_ctr_table, facebook_cpc_table)

            # Extract the CTR and CPC data for Google Ads
            google_ctr_table = soup.find_all('table')[2]
            google_cpc_table = soup.find_all('table')[3]
            google_data = self.extract_data(google_ctr_table, google_cpc_table)

            # Extract the CTR and CPC data for LinkedIn Ads
            linkedin_ctr_table = soup.find_all('table')[4]
            linkedin_cpc_table = soup.find_all('table')[5]
            linkedin_data = self.extract_data(linkedin_ctr_table, linkedin_cpc_table)

            # Combine all data into a single dictionary
            combined_data = {
                'Facebook': facebook_data,
                'Google': google_data,
                'LinkedIn': linkedin_data
            }

            return combined_data
        else:
            return {}

    def extract_data(self, ctr_table, cpc_table):
        """Extract CTR and CPC data from the given tables"""
        data = []

        # Extract CTR data
        ctr_rows = ctr_table.find_all('tr')[1:]  # Skip the header row
        for row in ctr_rows:
            columns = row.find_all('td')
            industry = columns[0].text.strip()
            ctr = columns[1].text.strip()
            data.append({'industry': industry, 'ctr': ctr})

        # Extract CPC data
        cpc_rows = cpc_table.find_all('tr')[1:]  # Skip the header row
        for row in cpc_rows:
            columns = row.find_all('td')
            industry = columns[0].text.strip()
            cpc = columns[1].text.strip()
            for item in data:
                if item['industry'] == industry:
                    item['cpc'] = cpc
                    break
            else:
                data.append({'industry': industry, 'cpc': cpc})

        return data
    
class KeywordGenerator:
    def __init__(self, groq_ai: GroqAI):
        self.groq_ai = groq_ai

    async def generate_keywords(self, industry: str, objective: str, website: str = None, 
                              social_media: str = None, target_audience: str = None, 
                              location: str = None) -> List[dict]:
        prompt = self._create_keyword_prompt(
            industry, objective, website, social_media, target_audience, location
        )
        
        messages = [
            {"role": "system", "content": "You are a digital marketing expert specializing in keyword research and SEO."},
            {"role": "user", "content": prompt}
        ]

        response = await self.groq_ai.generate_completion(messages)
        if response:
            try:
                keywords = self._parse_keyword_response(response)
                return keywords
            except Exception as e:
                logger.error(f"Error parsing keywords: {e}")
                return []
        return []

    def _create_keyword_prompt(self, industry, objective, website, social_media, 
                             target_audience, location) -> str:
        return f"""Generate a list of 10 keywords for a business with:
        Industry: {industry}
        Business Objective: {objective}
        Target Audience: {target_audience or 'Not specified'}
        Location: {location or 'Not specified'}
        
        Format as JSON array:
        [
            {{
                "keyword": "example keyword",
                "relevance": 85,
                "match_type": "phrase",
                "intent": "transactional"
            }}
        ]"""

    def _parse_keyword_response(self, response: str) -> List[dict]:
        try:
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing keyword response: {e}")
            return []

class MarketingFAQ:
    def __init__(self, groq_ai: GroqAI):
        self.groq_ai = groq_ai

    async def get_answer(self, question: str) -> str:
        messages = [
            {"role": "system", "content": "You are a digital marketing expert. Provide clear, actionable answers."},
            {"role": "user", "content": question}
        ]
        response = await self.groq_ai.generate_completion(messages)
        return response if response else "I apologize, but I couldn't generate an answer at this time."

class MarketingBot:
    def __init__(self, groq_api_key: str):
        self.groq_ai = GroqAI(groq_api_key)
        self.keyword_generator = KeywordGenerator(self.groq_ai)
        self.faq_system = MarketingFAQ(self.groq_ai)
        self.benchmark_scraper = BenchmarkScraper()
        self.user_states = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation with command options"""
        keyboard = [
            [InlineKeyboardButton("Generate Keywords", callback_data='cmd_keywords')],
            [InlineKeyboardButton("Industry Benchmarks", callback_data='cmd_benchmarks')],
            [InlineKeyboardButton("Marketing FAQ", callback_data='cmd_faq')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Welcome to the AI Marketing Assistant! 🚀\n"
            "Please select what you'd like to do:",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        user_id = update.effective_user.id
        message_text = update.message.text

        if user_id not in self.user_states:
            self.user_states[user_id] = {}

        state = self.user_states[user_id]
        current_step = state.get('current_step')

        if current_step == 'industry':
            state['industry'] = message_text
            state['current_step'] = 'objective'
            keyboard = [
                [InlineKeyboardButton(obj, callback_data=f"obj_{obj}")]
                for obj in ["Lead Generation", "Sales", "Brand Awareness", "Customer Retention"]
            ]
            await update.message.reply_text(
                "What is your business objective?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif current_step == 'website':
            state['website'] = message_text
            state['current_step'] = 'social_media'
            await update.message.reply_text(
                "Do you have any social media platforms? If yes, please share the URLs."
            )

        elif current_step == 'social_media':
            state['social_media'] = message_text
            state['current_step'] = 'target_audience'
            await update.message.reply_text(
                "Who is your target audience? (e.g., young adults, professionals, etc.)"
            )

        elif current_step == 'target_audience':
            state['target_audience'] = message_text
            state['current_step'] = 'location'
            await update.message.reply_text(
                "What location would you like to target?"
            )

        elif current_step == 'location':
            state['location'] = message_text
            # Generate keywords with all collected information
            keywords = await self.keyword_generator.generate_keywords(
                state['industry'],
                state['objective'],
                state.get('website'),
                state.get('social_media'),
                state['target_audience'],
                state['location']
            )
            
            response = "🎯 Generated Keywords:\n\n"
            for kw in keywords:
                response += (f"Keyword: {kw['keyword']}\n"
                           f"Relevance: {kw['relevance']}%\n"
                           f"Match Type: {kw['match_type']}\n"
                           f"Intent: {kw['intent']}\n\n")
            
            await update.message.reply_text(response)
            self.user_states[user_id] = {}  # Clear state

        elif current_step == 'faq':
            answer = await self.faq_system.get_answer(message_text)
            await update.message.reply_text(answer)

        else:
            # Default response if no specific state
            keyboard = [
                [InlineKeyboardButton("Generate Keywords", callback_data='cmd_keywords')],
                [InlineKeyboardButton("Industry Benchmarks", callback_data='cmd_benchmarks')],
                [InlineKeyboardButton("Marketing FAQ", callback_data='cmd_faq')]
            ]
            await update.message.reply_text(
                "Please use the menu options below to get started:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        user_id = query.from_user.id

        await query.answer()

        if query.data == 'cmd_keywords':
            self.user_states[user_id] = {'current_step': 'industry'}
            await query.message.reply_text("What industry is your business in?")

        elif query.data == 'cmd_benchmarks':
            benchmarks = await self.benchmark_scraper.fetch_benchmarks()
            if benchmarks:
                response = "📊 Industry Benchmarks:\n\n"
                for platform, data in benchmarks.items():
                    response += f"{platform} Benchmarks:\n"
                    for item in data:
                        response += f"{item['industry']}:\n"
                        response += f"CTR: {item.get('ctr', 'N/A')}\n"
                        response += f"CPC: {item.get('cpc', 'N/A')}\n\n"
            else:
                response = "Sorry, I couldn't fetch the benchmark data at the moment."
            await query.message.reply_text(response)

        elif query.data == 'cmd_faq':
            self.user_states[user_id] = {'current_step': 'faq'}
            await query.message.reply_text(
                "Please ask your digital marketing question, and I'll provide detailed guidance."
            )

        elif query.data.startswith('obj_'):
            state = self.user_states.get(user_id, {})
            objective = query.data.replace('obj_', '')
            state['objective'] = objective
            state['current_step'] = 'website'
            await query.message.reply_text(
                "Do you have a website? If yes, please share the URL."
            )

def main():
    # Replace with your tokens
    load_dotenv()
    groq_api_key = os.getenv('GROQ_API_KEY')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    
    # Create application
    app = Application.builder().token(telegram_token).build()
    
    # Initialize bot
    marketing_bot = MarketingBot(groq_api_key)

    # Add handlers
    app.add_handler(CommandHandler("start", marketing_bot.start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, marketing_bot.handle_message))
    app.add_handler(CallbackQueryHandler(marketing_bot.handle_callback))

    # Start polling
    print("Bot is starting...")
    app.run_polling(poll_interval=3)
    print("Bot stopped.")

if __name__ == '__main__':
    main()
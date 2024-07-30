from typing import Final
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TOKEN: Final ='The token goes here'
OWM_API_KEY: Final = 'your OWM_API_KEY'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_markup = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Share Location", request_location=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Hello! Please share your location to get weather details.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("You can ask me about the weather tomorrow.")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!!")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    latitude = location.latitude
    longitude = location.longitude
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OWM_API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        weather_message = (
            f"The weather is {weather_description}. "
            f"The temperature is {temperature}°C. "
            f"The humidity is {humidity}%. "
            f"The wind speed is {wind_speed} m/s."
        )
        await update.message.reply_text(weather_message)
    else:
        await update.message.reply_text("Error fetching weather data.")

def handle_response(text: str) -> str:
    processed: str = text.lower()
    if 'hello' in processed:
        return "Hey there!"
    if 'how are you' in processed:
        return "I'm good, thank you!"
    if 'my name is' in processed:
        return "Nice to meet you!"
    return "I do not understand what you wrote.."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: {text}')

    if message_type == 'group':
        if '@TaskTrek_bot' in text:
            new_text: str = text.replace('@TaskTrek_bot', '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    print("BOT:", response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
    print("Starting the bot...")
    app = Application.builder().token(TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Error handler
    app.add_error_handler(error)

    # Polls the bot for updates
    print("Polling...")
    app.run_polling(poll_interval=3)

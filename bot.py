import telebot
import datetime
import time
import requests
from bs4 import BeautifulSoup
import threading

TOKEN = '7899358317:AAE5btG2E2I3fv6UghUMQcAzmoom1x6K-uQ'
CHAT_ID = None
bot = telebot.TeleBot(TOKEN)

last_status = None  # чтобы не дублировать одно и то же

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(CHAT_ID, "✈️ Я отслеживаю рейс SU1251. Напомню вечером и утром, а ещё буду каждый час сообщать, не задержали ли его.")

@bot.message_handler(commands=['проверь'])
def manual_check(message):
    status = check_flight_status()
    bot.send_message(message.chat.id, f"📡 Текущий статус: {status}")

def check_flight_status():
    url = 'https://beg.aero/raspisanie/'
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            if 'SU1251' in row.text:
                return row.text.strip()
        return "⚠️ Рейс SU1251 не найден на табло."
    except Exception as e:
        return f"Ошибка при проверке: {e}"

def flight_monitoring():
    global last_status
    while True:
        if CHAT_ID:
            now = datetime.datetime.now()
            if now.date() == datetime.date(2025, 6, 25) or now.date() == datetime.date(2025, 6, 26):
                status = check_flight_status()
                if status != last_status:
                    bot.send_message(CHAT_ID, f"🕒 Обновление по рейсу SU1251:\n{status}")
                    last_status = status
        time.sleep(3600)  # раз в час

def send_timed_reminders():
    sent_evening = False
    sent_morning = False
    while True:
        now = datetime.datetime.now()
        if CHAT_ID:
            if now.date() == datetime.date(2025, 6, 25) and now.time().hour == 20 and not sent_evening:
                bot.send_message(CHAT_ID, "🌙 Напоминание: Завтра вылет SU1251 в 05:55. Подготовься заранее и ложись пораньше :)")
                sent_evening = True
            if now.date() == datetime.date(2025, 6, 26) and now.time().hour == 4 and not sent_morning:
                bot.send_message(CHAT_ID, "⏰ Доброе утро! Через 2 часа рейс SU1251. Проверь табло, гейт и не забудь зарядку для телефона.")
                sent_morning = True
        time.sleep(60)

threading.Thread(target=flight_monitoring).start()
threading.Thread(target=send_timed_reminders).start()

bot.polling()

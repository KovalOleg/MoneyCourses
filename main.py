import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import telebot

token = "2006479745:AAH_wIA6sd_XSSsaSOM6PtAm18w8Kq9anvM"
finance_api = "709f90cc4e08ba879fdf6ee0"
bot = telebot.TeleBot(token)
previous_data_about_current_course = None
update_time = 0
current_currency = "USD"


@bot.message_handler(commands=['start', 'help'])
def what_this_bot_doing(message):
    text = 'Hello! I can do this command:\n'+ \
           '/help - to get all possibilities \n '+\
           '/list - to get all info about international currensies' + \
           ' \n /exchange 10 USD to EUR - to exchange any currency to any other \n ' + \
           '/history USD/EUR for 7 days - to get info about valutes on last time \n ' \
           '(but this is not working because I have free plan on this api :() P.S. To replace this possibility I added command /test'
    bot.reply_to(message, text)


# Saving data from server in case we have nothing or our info is old
def getData(base):
    global previous_data_about_current_course, update_time, current_currency
    current_time = time.time()
    if previous_data_about_current_course == None or update_time == 0 or current_time - update_time > 600 or current_currency != base:
        responce = requests.get('https://v6.exchangerate-api.com/v6/' + finance_api + '/latest/' + base)
        previous_data_about_current_course = responce
        update_time = current_time
        current_currency = base


@bot.message_handler(commands=["exchange"])
def handler(message):
    global previous_data_about_current_course
    mess = message.text.split(" ")
    from_currency = mess[2] if isNumer(mess[1][0]) else mess[1][0]
    from_currency = 'USD' if from_currency == '$' else from_currency

    number = int(mess[1]) if isNumer(mess[1][0]) else int(mess[1][1:len(mess[1] - 1)])

    getData(from_currency)
    current_data = json.loads(previous_data_about_current_course.text)
    to_currency = mess[len(mess) - 1]
    course = current_data['conversion_rates'][to_currency]
    txt = "{price:.2f}"

    bot.reply_to(message, txt.format(price=number * course))


def isNumer(numer):
    for i in range(0, 10):
        if (numer == str(i)): return True
    return False


def buildGraph(points, days, name):
    data = {name: points}
    df = pd.DataFrame(data)
    x = np.arange(days)
    coor_x, coor_y = days, max(points)
    plt.axis([0, coor_x, 0, coor_y])
    plt.plot(x, df)
    plt.legend(data, loc=2)
    plt.savefig('1.png')


@bot.message_handler(commands="history")
def graph_handler(message):
    mess = message.text.split(' ')
    valuta = mess[1].split('/')
    curr = mess[3]
    sec_in_day = 86400

    points = []
    for i in range(int(curr), 0, -1):
        t = time.localtime(time.time() - sec_in_day * i)
        year = t.tm_year
        month = t.tm_mon
        day = t.tm_mday
        amount = 4.00
        first_currency, second_currency = valuta[0], valuta[1]

        response = requests.get(
            'https://v6.exchangerate-api.com/v6/' + finance_api + '/history/' + first_currency + '/' + str(
                year) + '/' + str(month) + '/' + str(day) + '/' + str(amount))

        y = json.loads(response.text)

        if y['result'] != 'error':
            value = y['conversion_amounts'][second_currency]
            points.append(value)
        else:
            bot.reply_to(message, 'Не вдалося отримати дані')
            return

    buildGraph(points, curr, mess[1])
    img = open('1.png', 'rb')
    bot.send_photo(message.from_user.id, img)


@bot.message_handler(commands=["test"])
def handl(message):
    points = [2, 3, 4, 1]
    buildGraph(points, 4, 'test')
    img = open('1.png', 'rb')
    bot.send_photo(message.from_user.id, img)


@bot.message_handler(commands=["list", "lst"])
def handle_text_doc(message):
    getData('USD')
    # Forming one message with info about
    y = json.loads(previous_data_about_current_course.text)
    formed_text = ""
    for i in y['conversion_rates']:
        formed_text += i + ": " + str(y['conversion_rates'][i]) + '\n'
    bot.reply_to(message, formed_text)


bot.infinity_polling()

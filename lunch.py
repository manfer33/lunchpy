#!/usr/bin/python
# coding=utf-8
from bs4 import BeautifulSoup
import  urllib2, unicodedata, logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

html='WebPage'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

week, date = {}, ''
init, end = [],[]

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def update_info():
    global week, date, init, end

    soup = BeautifulSoup(urllib2.urlopen(html).read(),"lxml")

    # Get lunch date
    date_elem = soup.find('h4')
    date = date_elem.contents[0].replace(' ','')
    date = date[date.find(':')+1:]

    since = map(int,date.split('-')[0].split('/'))
    until = map(int,date.split('-')[1].split('/'))
    init = datetime(since[2],since[1],since[0])
    end = datetime(until[2],until[1],until[0])

    # Get lunch info from table
    for row in soup.select("tr"):
        th, td = row.findAll("th"), row.findAll("td")
        if th:
            if len(th) == 1:
                day = row.find(['strong','span'])
                day = day.contents[0]
                day = strip_accents(day[:day.find(' ')].lower())
                week[day] = ""
        if td:
            no_serv = row.find('td', attrs={'align':'center'})
            if no_serv:
                week[day] = [no_serv.contents[0]].encode("utf-8")
            else:
                week[day] = map(lambda list: str(list.encode('utf-8'))[4:-5].replace('*','').split("<br/>"), [td[0], td[1], td[2]])
                week[day][0].pop(),week[day][1].pop(),week[day][2].pop()

def start(bot, update):
    keyboard = [[InlineKeyboardButton("Lunes", callback_data='lunes'),
                 InlineKeyboardButton("Martes", callback_data='martes')],
                 [InlineKeyboardButton("Miércoles", callback_data='miercoles'),
                 InlineKeyboardButton("Jueves", callback_data='jueves')],
                [InlineKeyboardButton("Viernes", callback_data='viernes')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Elige día de la semana:', reply_markup=reply_markup)

def button(bot, update):
    query = update.callback_query
    output = ""

    today = datetime.now()

    if not init < today < end:
        update_info()

    if len(week[query.data])>1:
        o0 = '\n'.join('{}'.format(k) for k in (week[query.data][0]))
        o1 = '\n'.join('{}'.format(k) for k in (week[query.data][1]))
        o2 = '\n'.join('{}'.format(k) for k in (week[query.data][2]))

        output = "{}\n{}\nPrimero\n{}\nSegundo\n{}\nPostre\n{}".format(date,query.data.upper(),o0,o1,o2)
    else:
        output = "{}\n{}\n{}".format(date,query.data.upper(),week[query.data][0])

    bot.edit_message_text(text=output,
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)

def today(bot, update):
    output = ""
    week_list = ['lunes','martes','miercoles','jueves','viernes']
    today = datetime.now()

    if not init < today < end:
        update_info()

    if today.weekday() > 4:
            output = "¡Información de la próxima semana a partir del lunes! :D"
    else:
        if len(week[week_list[today.weekday()]])>1:

            o0 = '\n'.join('{}'.format(k) for k in (week[week_list[today.weekday()]][0]))
            o1 = '\n'.join('{}'.format(k) for k in (week[week_list[today.weekday()]][1]))
            o2 = '\n'.join('{}'.format(k) for k in (week[week_list[today.weekday()]][2]))

            output = "{}\n{}\nPrimero\n{}\nSegundo\n{}\nPostre\n{}".format(date,week_list[today.weekday()].upper(),o0,o1,o2)
        else:
            output = "{}\n{}\n{}".format(date,week_list[today.weekday()].upper(),week[week_list[today.weekday()]][0])

    update.message.reply_text(text=output)

def help(bot, update):
    update.message.reply_text("Usa /hoy para ver el menú del día y /menu para consultar el resto de la semana.")

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

if __name__ == '__main__':
    updater = Updater(token='TOKEN')
    updater.dispatcher.add_handler(CommandHandler('menu', start))
    updater.dispatcher.add_handler(CommandHandler('hoy', today))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    update_info()

    updater.start_polling()
    updater.idle()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Bruno Stefoni
# Created Date: Mon May 4 18:54:00 PDT 2020
# =============================================================================
"""Este script es un template para hacer un bot de telegram
Hay dos ID clave que se pueden printear al llamar una funcion
update.message.chat_id:corresponde al ID del chat, sirve para enviarle mensajes
update.effective_user.id: corresponde al ID del usuario, sirve por ejemplo para
                          darle privilegios de admin a una cierta ID
"""
# =============================================================================

import MySQLdb
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram import Bot
import pandas as pd
import datetime as dt
import threading
from time import sleep


TOKEN = ""  # token del bot creada por BotFather
groupchat_ID = ""  # id del grupo de telegram si es que el bot pertenece a uno
id_admin = ""  # telegram id del admin, los id se obtienen diciendole al bot /ayuda

updater = Updater(token=TOKEN, use_context=False)  # maneja los llamados al bot globalmente
bot2 = Bot(token=TOKEN)  # para mandar mensajes directos ante eventos

n_version = "1.0"
seguro_telegramearlyexit = False  # evita que bot finalice accidentalmente

# --- ahora vienen las funciones que llaman al bot cada vez que un usuario le da un comando


def ayuda(bot, update):
    # esta funcion habla un poco acerca del bot
    bot.send_message(chat_id=update.message.chat_id, text="Este bot toma es un ejemplo")
    # printear la hora y el ID de quien pidio ayuda
    print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /ayuda")


def version(bot, update):
    # esta funcion dice qué versión del bot se está corriendo, solo para Admin
    if str(update.effective_user.id) == id_admin:
        bot.send_message(chat_id=update.message.chat_id, text="Bot de Telegram para X motivo, versión " + n_version)
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /version")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Acceso denegado")
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /version  - rechazado")


def shutdown():
    # esta funcion mata el hilo donde corre el bot
    if updater.is_idle:
        updater.is_idle = False
        updater.stop()


def stop(bot, update):
    # llama a funcion que mata el hilo del bot
    if seguro_telegramearlyexit:
        threading.Thread(target=shutdown).start()
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /stop")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Acceso denegado")
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /stop - rechazado")


def orden_stop(bot, update):
    # esta funcion ayuda a no detener el bot por accidente
    if str(update.effective_user.id) == id_admin:
        global seguro_telegramearlyexit
        seguro_telegramearlyexit = True
        bot.send_message(chat_id=update.message.chat_id, text="Orden lista")
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /orden66")


def jalisco(bot, update, args):
    # ejemplo de funcion que recibe un argumento
    if args:
        if args[0].isdigit():
            bot.send_message(chat_id=update.message.chat_id, text="Te gané con " + str(int(args[0]) + 1))
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Enviar un numero, por ejemplo /jalisco 15")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Enviar un numero, por ejemplo /jalisco 15")


def consulta_ejecucion(bot, update):
    # funcion que consulta al servidor, por ejemplo para ver encuestas
    db0 = MySQLdb.connect(host="ip del host sql",
                         user="tu usuario",
                         passwd="tu clave",
                         db="nombre de la base de datos!")

    cur0 = db0.cursor()

    cur0.execute("SELECT * FROM tablaX WHERE variableX > 100;")
    data_query_cur0 = [row for row in cur0.fetchall()]
    df = pd.DataFrame(data_query_cur0, columns=['col' + str(i) for i in range(11)])

    cur0.close()
    db0.close()

    return "Hay " + str(len(df.index)) + " personas con un nivel sobre 100"


def consulta_ahora(bot, update):
    # recibe la orden de un usuario para que consulte al servidor, solo para Admin

    if str(update.effective_user.id) == id_admin:
        bot.send_message(chat_id=update.message.chat_id, text="Consultando base de datos..")
        mensaje_a_enviar = consulta_ejecucion()
        bot.send_message(chat_id=update.message.chat_id, text=mensaje_a_enviar)
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /consulta_ahora")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Acceso denegado")
        print("[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + str(update.effective_user.id) + ": /consulta_ahora - rechazado")


def funcion_prueba():
    # hacer cualquier cosa, como dormir 5 segundos y hablar
    if groupchat_ID:
        for _ in range(3):
            sleep(5)
            bot2.send_message(chat_id=groupchat_ID, text="Hola esto es una alerta!")


def main():

    # se crea un hilo para hacer cualquier cosa mientras funciona el bot
    hilo_1 = threading.Thread(target=funcion_prueba)
    hilo_1.start()

    # antes de inicilizar el bot se agregan las funciones y sus nombres
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('ayuda', ayuda))
    dispatcher.add_handler(CommandHandler('version', version))
    dispatcher.add_handler(CommandHandler('consulta_ahora', consulta_ahora))
    dispatcher.add_handler(CommandHandler('jalisco', jalisco, pass_args=True))

    dispatcher.add_handler(CommandHandler('stop', stop))
    dispatcher.add_handler(CommandHandler('orden_stop', orden_stop))

    # por ultimo, se inicia el hilo del bot que escucha cada 3 segundos
    # este hilo debe ir en el main obligatoriamente
    updater.start_polling(poll_interval=3)
    updater.idle()


if __name__ == '__main__':
    main()

import telebot
import os

TOKEN = #Сюда идет токен

bot = telebot.TeleBot(TOKEN)
keyboard = telebot.types.ReplyKeyboardMarkup(True)
keyboard.row('/all', '/new_item', '/add_pic', '/swap')
keyboard.row('/delete', '/help', '/author')


@bot.message_handler(commands=['start', 'help', 'author'])
def basic_commands(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!', reply_markup=keyboard)
        bot.send_message(message.from_user.id, 'Выбери одну из моих функций или нажми на /help:')
        if not os.path.exists(f'todolists/{message.from_user.id}.txt'):
            create = open(f'todolists/{message.from_user.id}.txt', 'w+')
            create.close()
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Меня зовут TODO-list bot. '
                                               'Моя цель — помочь тебе составить список задач')
        bot.send_message(message.from_user.id, 'Подробнее ознакомиться со всеми командами ты можешь в README')
    elif message.text == '/author':
        bot.send_message(message.from_user.id, 'Мой автор: Михаэль Павлов, студент I курса СПбГУ')


@bot.message_handler(commands=['all', 'new_item', 'add_pic', 'delete', 'swap'])
def complex_commands(message):
    if message.text == '/all':
        todolist = open(f'todolists/{message.from_user.id}.txt').read().split(';')
        if len(todolist) == 1 and todolist[0] == '':
            bot.send_message(message.from_user.id, 'Твой лист пока пуст')
        else:
            for item in range(0, len(todolist)):
                if todolist[item][-1] == 'λ':
                    bot.send_message(message.from_user.id, f'{item + 1}. {todolist[item][:-1:]}')
                    image = open(f'pictures/{message.from_user.id}_{item + 1}.jpg', 'rb')
                    bot.send_photo(message.from_user.id, image)
                else:
                    bot.send_message(message.from_user.id, f'{item + 1}. {todolist[item]}')
    elif message.text == '/new_item':
        sent = bot.send_message(message.from_user.id, 'Напиши новую задачу:')
        bot.register_next_step_handler(sent, add_item)
    elif message.text == '/delete':
        sent = bot.send_message(message.from_user.id, 'Задачу под каким номером нужно удалить?')
        bot.register_next_step_handler(sent, delete_item)
    elif message.text == '/swap':
        sent = bot.send_message(message.from_user.id, 'Напиши через пробел номера задач, которые нужно переставить')
        bot.register_next_step_handler(sent, swap_items)
    elif message.text == '/add_pic':
        sent = bot.send_message(message.from_user.id, 'К задаче под каким номером нужно прикрепить картинку?')
        bot.register_next_step_handler(sent, addpicto_item_part1)


def add_item(message):
    content = open(f'todolists/{message.from_user.id}.txt', 'r').read().split(';')
    if len(content) == 1 and content[0] == '':
        new_item = message.text
    else:
        new_item = f';{message.text}'
    todolist = open(f'todolists/{message.from_user.id}.txt', 'a')
    todolist.write(new_item)
    todolist.close()
    bot.send_message(message.from_user.id, 'Задача успешно добавлена')


def swap_items(message):
    try:
        content = open(f'todolists/{message.from_user.id}.txt', 'r').read().split(';')
        swap = list(map(int, message.text.split(' ')))
        content[swap[0] - 1], content[swap[1] - 1] = content[swap[1] - 1], content[swap[0] - 1]
        if os.path.exists(f'pictures/{message.from_user.id}_{swap[0]}.jpg'):
            os.rename(f'pictures/{message.from_user.id}_{swap[0]}.jpg', 'pictures/temp1.jpg')
        if os.path.exists(f'pictures/{message.from_user.id}_{swap[1]}.jpg'):
            os.rename(f'pictures/{message.from_user.id}_{swap[1]}.jpg', 'pictures/temp2.jpg')
        if os.path.exists('pictures/temp2.jpg'):
            os.rename('pictures/temp2.jpg', f'pictures/{message.from_user.id}_{swap[0]}.jpg')
        if os.path.exists('pictures/temp1.jpg'):
            os.rename('pictures/temp1.jpg', f'pictures/{message.from_user.id}_{swap[1]}.jpg')
        todolist = open(f'todolists/{message.from_user.id}.txt', 'w')
        todolist.write(';'.join(content))
        todolist.close()
        bot.send_message(message.from_user.id, 'Задачи успешно переставлены')
    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, 'Но ведь таких задач нет')


def addpicto_item_part1(message):
    try:
        content = open(f'todolists/{message.from_user.id}.txt', 'r').read().split(';')
        if content[int(message.text) - 1].find('λ') == -1:
            temp = open('pictures/temp.txt', 'w')
            temp.write(f'{int(message.text)}')
            sent = bot.send_message(message.from_user.id, 'Хорошо, теперь можешь её отправлять')
            bot.register_next_step_handler(sent, addpicto_item_part2)
        else:
            bot.send_message(message.from_user.id, 'У этой задачи уже есть картинка')
    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, 'Но ведь такой задачи нет')


def addpicto_item_part2(message):
    try:
        temp = open('pictures/temp.txt', 'r').read()
        num = temp
        os.remove('pictures/temp.txt')
        photo = message.photo[-1]
        downloaded_file = bot.download_file(bot.get_file(photo.file_id).file_path)
        new_file = open(f'pictures/{message.from_user.id}_{num}.jpg', 'wb')
        new_file.write(downloaded_file)
        new_file.close()
        content = open(f'todolists/{message.from_user.id}.txt', 'r').read().split(';')
        content[int(num) - 1] += 'λ'
        todolist = open(f'todolists/{message.from_user.id}.txt', 'w')
        todolist.write(';'.join(content))
        todolist.close()
        bot.send_message(message.from_user.id, 'Картинка успешно прикреплена')
    except TypeError:
        bot.send_message(message.from_user.id, 'В следующий раз попробуй отправить картинку')


def delete_item(message):
    try:
        content = open(f'todolists/{message.from_user.id}.txt', 'r').read().split(';')
        del content[int(message.text) - 1]
        if os.path.exists(f'pictures/{message.from_user.id}_{int(message.text)}.jpg'):
            os.remove(f'pictures/{message.from_user.id}_{int(message.text)}.jpg')
        todolist = open(f'todolists/{message.from_user.id}.txt', 'w')
        todolist.write(';'.join(content))
        todolist.close()
        bot.send_message(message.from_user.id, 'Задача успешно удалена')
    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, 'Но ведь такой задачи нет')


@bot.message_handler(content_types=['photo'])
def audio_handler(message):
    bot.send_message(message.from_user.id, 'Лучше прикрепи эту картинку к какой-либо задаче')


@bot.message_handler(content_types=['voice'])
def audio_handler(message):
    bot.send_message(message.from_user.id, 'Настоящие мужчины не пользуются голосовыми сообщениями')


@bot.message_handler(func=lambda m: True)
def else_handler(message):
    bot.send_message(message.from_user.id, 'Прости, но я всего лишь бот и не могу отвечать тебе как человек')


bot.polling()

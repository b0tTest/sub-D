# Copyright 2021 TerminalWarlord under the terms of the MIT
# license found at https://github.com/TerminalWarlord/Subtitle-Downloader-Bot/blob/master/LICENSE
# Encoding = 'utf-8'
# Fork and Deploy, do not modify this repo and claim it yours
# For collaboration mail me at dev.jaybee@gmail.com


from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import shutil
import requests
import os
import glob
from bs4 import BeautifulSoup as bs
import time
from datetime import timedelta
from dotenv import load_dotenv
import zipfile

from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant, UserBannedInChannel


load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
api = int(os.environ.get('API_KEY'))
hash = os.environ.get('API_HASH')
workers = int(os.environ.get('WORKERS'))
app = Client("SubtitleDLbot", bot_token=bot_token, api_id=api, api_hash=hash, workers=workers)
cuttly = os.environ.get('CUTTLY_API')

UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "MyTestBotZ")

timestarted = timedelta(seconds=int(time.time()))

btn = [[InlineKeyboardButton('πΏ Channel', url="https://telegram.me/MyTestBotZ"),InlineKeyboardButton('πΏ BotsList', url="https://t.me/mybotzlist")]]
  
START = """Hello thereπ, \nI am a __**Subtitle Downloader Bot**__.\nGive me a Movie/Series name and I will fetch it from __**Subscene**__.\n\n__**Made with β₯οΈ by @OO7ROBot :**__"""

HELP = """**How to USE meh**...
\nβ’ __Send me any Movie/Series name and I will__ \n
__β’ i will Search for you it on `Subscene.com`\n
β’ Let you choose your preferable language.\n
β’ Download the subtitle, unzip and upload in `.srt/.ass` format__

**Made with β₯οΈ by @MyTestBotZ**
"""

ABOUT = """--**About Me**-- π

π€ **Name :** [Subtitle Downloader](https://telegram.me/Get_subtitlebot)

π¨βπ» **Creator :** [@OO7ROBot](https://telegram.me/oo7robot)

π’ **Channel :** [MyTestBotZ](https://telegram.me/mytestbotz)

π₯ **Bots List :** [My Botz List](https://telegram.me/mybotzlist)

π **Source :** [ Click Here](https://github.com/OO7ROBOT) (Prvt)

π **Language :** [Python3](https://python.org)

π§° **Framework :** [Pyrogram](https://pyrogram.org)

π‘ **Server :** [Heroku](https://heroku.com)

π― % Clone Bot

""" 

FORCE_SUBSCRIBE_TEXT = "**Sorry Dear You Must Join My Updates Channel for using me ππ....**\n\n__Due to Overload Only Channel Subscribers can Use this Bot__"


        
 
################################################
@app.on_message(filters.text & filters.private)
async def telegraph_upload(bot, update):
    if UPDATE_CHANNEL:
        try:
            user = await bot.get_chat_member(UPDATE_CHANNEL, update.chat.id)
            if user.status == "kicked":
                await update.reply_text(text="You are banned!")
                return
        except UserNotParticipant:
            await update.reply_text(
		  text=FORCE_SUBSCRIBE_TEXT,
		  reply_markup=InlineKeyboardMarkup(
			  [[InlineKeyboardButton(text="β Join Updates Channel β", url=f"https://telegram.me/{UPDATE_CHANNEL}")]]
		  )
	    )
            return
        except Exception as error:
            print(error)
            await update.reply_text(text="Something wrong. Contact <a href='https://telegram.me/oo7robot'>Developer</a>.", disable_web_page_preview=True)
            return

###### ----------------------------- ######

@app.on_message(filters.command('start'))
def start(client,message):
    reply_markup = InlineKeyboardMarkup(btn)
    app.send_message(chat_id=message.from_user.id, text=START,
                     parse_mode='md',
                     reply_markup=reply_markup)

@app.on_message(filters.command('help'))
def help(client,message):
    reply_markup = InlineKeyboardMarkup(btn)
    message.reply_text(reply_to_message_id= message.message_id,text=HELP, parse_mode='md', reply_markup=reply_markup)

@app.on_message(filters.command('about'))
def about(client,message):
    reply_markup = InlineKeyboardMarkup(btn)
    message.reply_text(reply_to_message_id= message.message_id,text=ABOUT, parse_mode='md', reply_markup=reply_markup)


@app.on_message(filters.command('uptime'))
def uptime(client, message):
    timecheck = timedelta(seconds=int(time.time()))
    uptime = timecheck - timestarted
    app.send_message(chat_id=message.from_user.id, text=f"__**Uptime :**__ __{uptime}__",
                     parse_mode='md')


@app.on_message(filters.text)
def search(client, message):     
    query = message.text.replace(" ", "+")
    data = {
        'query' : query,
        'l' : ''
    }

    res = requests.post('https://subscene.com/subtitles/searchbytitle', data=data)
    soup = bs(res.text, 'html.parser')
    results = soup.find('div', {'class': 'search-result'}).find_all('div', {'class': 'title'})
    kb = []
    i = 0
    l = 0
    for sub in results:
        if l < 10:
            sublink = sub.find('a').attrs['href'].split('/')[-1]
            subtitlename = sub.find('a').text
            if len(sublink)<64:
                kb.append([InlineKeyboardButton(f"{subtitlename}", callback_data=f'LANG*{sublink}')])
                i += 1
            else:
                pass

        else:
            pass
        l += 1
    if len(results) > i:
        kb.append([InlineKeyboardButton(f"Next β­", callback_data=f'SRCNX*{i}*{query}')])
    reply_markup = InlineKeyboardMarkup(kb)
    app.send_message(chat_id=message.chat.id,
                     text=f"__Showing Result for **{query}**\n"
                     f"\nChoose your desired Movie/Series:__",
                     parse_mode='md',
                     reply_markup=reply_markup)


@app.on_callback_query(filters.regex('SRCNX'))
def searchnext(client, callback_query):
    query = callback_query.data.split('*')[-1]
    data = {
        'query' : query,
        'l' : ''
    }
    res = requests.post('https://subscene.com/subtitles/searchbytitle', data=data)
    soup = bs(res.text, 'html.parser')
    results = soup.find('div', {'class': 'search-result'}).find_all('div', {'class': 'title'})
    kb = []
    i = int(callback_query.data.split('*')[-2]) + 1
    j = i - 1
    k = i + 10
    l = 0
    for sub in results:
        if l > j and l < k:
            sublink = sub.find('a').attrs['href'].split('/')[-1]
            subtitlename = sub.find('a').text
            if len(sublink)<64:
                kb.append([InlineKeyboardButton(f"{subtitlename}", callback_data=f'LANG*{sublink}')])
                i += 1
            else:
                pass
        else:
            pass
        l += 1

    if len(results) > i:
        kb.append([InlineKeyboardButton(f"Next β­", callback_data=f'SRCNX*{i}*{query}')])
    kb.append([InlineKeyboardButton(f"Previous β?οΈ", callback_data=f'SRCPR*{i}*{query}')])

    reply_markup = InlineKeyboardMarkup(kb)
    callback_query.edit_message_reply_markup(reply_markup=reply_markup)



@app.on_callback_query(filters.regex('SRCPR'))
def searchprev(client, callback_query):
    query = callback_query.data.split('*')[-1]
    data = {
        'query' : query,
        'l' : ''
    }
    res = requests.post('https://subscene.com/subtitles/searchbytitle', data=data)
    soup = bs(res.text, 'html.parser')
    results = soup.find('div', {'class': 'search-result'}).find_all('div', {'class': 'title'})
    kb = []
    i = int(callback_query.data.split('*')[-2])
    j = i - 21
    k = i - 10
    l = 0
    for sub in results:
        if l > j and l < k:
            sublink = sub.find('a').attrs['href'].split('/')[-1]
            subtitlename = sub.find('a').text
            if len(sublink)<64:
                kb.append([InlineKeyboardButton(f"{subtitlename}", callback_data=f'LANG*{sublink}')])
                i -= 1
            else:
                pass
        else:
            pass
        l += 1
    if j > 10:
        kb.append([InlineKeyboardButton(f"Previous β?οΈ", callback_data=f'SRCPR*{i}*{language}*{suburl}')])
    if len(results) > i:
        kb.append([InlineKeyboardButton(f"Next β­", callback_data=f'SRCNX*{i}*{query}')])
    reply_markup = InlineKeyboardMarkup(kb)
    callback_query.edit_message_reply_markup(reply_markup=reply_markup)



@app.on_callback_query(filters.regex('LANG'))
def chooselang(client, callback_query):
    sublink = callback_query.data.split('*')[-1]
    kb = [[InlineKeyboardButton("English π¬π§", callback_data=f'PREL*english*{sublink}')],
          [InlineKeyboardButton("Malayalam β₯οΈ", callback_data=f'PREL*malayalam*{sublink}')],
          [InlineKeyboardButton("Bengali π§π©", callback_data=f'PREL*bengali*{sublink}')],
          [InlineKeyboardButton("Hindi π?π³", callback_data=f'PREL*hindi*{sublink}')],
          [InlineKeyboardButton("Tamil π?π³", callback_data=f'PREL*tamil*{sublink}')],
          [InlineKeyboardButton("Arabic β£οΈ", callback_data=f'PREL*arabic*{sublink}')],
          [InlineKeyboardButton("Spanish πͺπΈ", callback_data=f'PREL*spanish*{sublink}')],
          [InlineKeyboardButton("Indonesian π?π©", callback_data=f'PREL*indonesian*{sublink}')]]
    reply_markup = InlineKeyboardMarkup(kb)
    app.edit_message_text(chat_id=callback_query.message.chat.id,
                          message_id=callback_query.message.message_id,
                          text=f"__Select a Subtitle Language__β€΅οΈ \n\n**Β© @MyTestBotZ**",
                          parse_mode='md',
                          reply_markup=reply_markup)


@app.on_callback_query(filters.regex('PREL'))
def langset(client, callback_query):
    language = callback_query.data.split('*')[-2]
    callback_query.answer(f"Preffered Language : {language.capitalize()}", show_alert=False)
    suburl = callback_query.data.split('*')[-1]
    url = f'https://subscene.com/subtitles/{suburl}/{language}'
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    allsubs = soup.find('tbody').find_all('tr')
    kb = []
    i = 0
    for subs in allsubs:
        try:
            if i < 10:
                subid = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-1]
                sublink = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-3]
                subname = subs.find('td', {'class': 'a1'}).find_all('span')[1].text.strip()
                if len(sublink) < 64:
                    kb.append([InlineKeyboardButton(f"{subname}", callback_data=f'DTL*{language}*{sublink}*{subid}')])
                    i += 1

                else:
                    pass
            else:
                break
        except:
            pass
    if i > 10:
        kb.append([InlineKeyboardButton(f"Next β­οΈ", callback_data=f'NXT*{i}*{language}*{suburl}')])
    try:
        reply_markup = InlineKeyboardMarkup(kb)
        app.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f"__Select a Subtitle__",
                              parse_mode='md',
                              reply_markup=reply_markup)
    except:
        app.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f"__Sorry no subtitle available for that specific language!\n"
                              f"Try another one!__",
                              parse_mode='md')


@app.on_callback_query(filters.regex('DTL'))
def subdetails(client, callback_query):
    language = callback_query.data.split('*')[-3]
    suburl = callback_query.data.split('*')[-2]
    subid = callback_query.data.split('*')[-1]
    kb = []
    # getsub
    url = f'https://subscene.com/subtitles/{suburl}/{language}/{subid}'
    callback_query.answer(f"Getting sub from : {url}", show_alert=False)
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    poster = soup.find('div', {'class': 'poster'}).find('img').attrs['src'].replace('154-', '')
    info = soup.find('div', {'id': 'details'}).find('ul').find_all('li')
    dload = "https://subscene.com" + soup.find('a', {'id': 'downloadButton'}).attrs['href']
    subdetails = []
    for a in info:
        try:
            w = a.text.replace('-', '')
            a = "".join(line.strip() for line in w.split("\n"))
            subdetails.append(a)
        except:
            pass
    subtext = "\n".join(subdetails)

    #cuttly
    data = requests.get(f"https://cutt.ly/api/api.php?key={cuttly}&short={dload}").json()["url"]
    shortened_url = data["shortLink"]

    kb = [[InlineKeyboardButton(f"πΎ Download", callback_data=f'DOWNLOAD*{shortened_url}')]]
    reply_markup = InlineKeyboardMarkup(kb)
    app.send_photo(caption=f'__{subtext}__\n\n**Β© @Get_Subtitlebot**',
                   photo=poster,
                   chat_id=callback_query.message.chat.id,
                   parse_mode='md',
                   reply_markup=reply_markup)




@app.on_callback_query(filters.regex('DOWNLOAD'))
def download(client, callback_query):
    callback_query.answer(f"Downloading!!!", show_alert=False)
    link = callback_query.data.split('*')[-1]
    # unzip
    url = requests.get(link).url
    r = requests.head(url)
    a = r.headers
    filename = a['Content-Disposition'].split('=')[-1]
    directory = a['Content-Disposition'].split('=')[-1].replace('.zip', '')
    with open(filename, 'wb') as f:
        im = requests.get(link)
        f.write(im.content)
    with zipfile.ZipFile(filename,"r") as zip_ref:
        zip_ref.extractall(directory)
    try:
        a = glob.glob(f'./{directory}/*srt', recursive=True)
        for file in a:
            app.send_document(document=file,
                              caption=f"**{filename}\n\nΒ© @Get_SubtitleBot**",
                              chat_id=callback_query.message.chat.id,
                              parse_mode='md')
        app.delete_messages(chat_id=callback_query.message.chat.id,
                                message_ids=callback_query.message.message_id)
    except:
        a = glob.glob(f'./{directory}/*', recursive=True)
        for file in a:
            app.send_document(document=file,
                              caption=f"**{filename}\n\nΒ© @Get_SubtitleBot**",
                              chat_id=callback_query.message.chat.id,
                              parse_mode='md')
        app.delete_messages(chat_id=callback_query.message.chat.id,
                            message_ids=callback_query.message.message_id)
    try:
        os.remove(filename)
        shutil.rmtree(directory)
    except:
        pass



@app.on_callback_query(filters.regex('NXT'))
def nextres(client, callback_query):
    language = callback_query.data.split('*')[-2]
    suburl = callback_query.data.split('*')[-1]
    url = f'https://subscene.com/subtitles/{suburl}/{language}'
    print(url)
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    allsubs = soup.find('tbody').find_all('tr')
    kb = []
    i = int(callback_query.data.split('*')[-3]) + 1
    j = i - 1
    k = i + 10
    l = 0
    for subs in allsubs:
        try:
            if l > j and l < k:
                subid = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-1]
                sublink = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-3]
                subname = subs.find('td', {'class': 'a1'}).find_all('span')[1].text.strip()
                if len(sublink) < 64:
                    kb.append([InlineKeyboardButton(f"{subname}", callback_data=f'DTL*{language}*{sublink}*{subid}')])
                    i += 1

                else:
                    pass
            else:
                pass
            l += 1

        except:
            pass
    if len(allsubs) > i:
        kb.append([InlineKeyboardButton(f"Next β­οΈ", callback_data=f'NXT*{i}*{language}*{suburl}')])
    kb.append([InlineKeyboardButton(f"Previous β?οΈ", callback_data=f'PRV*{i}*{language}*{suburl}')])
    reply_markup = InlineKeyboardMarkup(kb)
    a = app.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f"__Select a Subtitle__",
                              parse_mode='md',
                              reply_markup=reply_markup)

@app.on_callback_query(filters.regex('PRV'))
def prevres(client, callback_query):
    language = callback_query.data.split('*')[-2]
    suburl = callback_query.data.split('*')[-1]
    url = f'https://subscene.com/subtitles/{suburl}/{language}'
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    allsubs = soup.find('tbody').find_all('tr')
    kb = []
    i = int(callback_query.data.split('*')[-3])
    j = i - 21
    k = i - 10
    l = 0
    for subs in allsubs:
        try:
            if l > j and l < k:
                subid = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-1]
                sublink = subs.find('td', {'class': 'a1'}).find('a').attrs['href'].split('/')[-3]
                subname = subs.find('td', {'class': 'a1'}).find_all('span')[1].text.strip()
                if len(sublink) < 64:
                    kb.append([InlineKeyboardButton(f"{subname}", callback_data=f'DTL*{language}*{sublink}*{subid}')])
                    i -= 1

                else:
                    pass
            else:
                pass
            l += 1

        except:
            pass
    if j > 10:
        kb.append([InlineKeyboardButton(f"Previous β?οΈ", callback_data=f'PRV*{i}*{language}*{suburl}')])
    if len(allsubs) > i:
        kb.append([InlineKeyboardButton(f"Next β­οΈ", callback_data=f'NXT*{i}*{language}*{suburl}')])

    reply_markup = InlineKeyboardMarkup(kb)
    app.edit_message_text(chat_id=callback_query.message.chat.id,
                              message_id=callback_query.message.message_id,
                              text=f"__Select a Subtitle__\n\n**Β© @MyTestBotZ**",
                              parse_mode='md',
                              reply_markup=reply_markup)

app.run()

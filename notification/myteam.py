#!/usr/bin/python3

import io
from bot.bot import Bot
from bot.handler import MessageHandler, NewChatMembersHandler
from bot.types import Format

class Myteam():
    def __init__(self, token, chat):
        self.token = token
        self.bot = Bot(token=self.token, api_url_base='https://api.internal.myteam.mail.ru/bot/v1')
        self.chat = chat

    def send_report_text(self, message):
        self.bot.send_text(chat_id=self.chat, text=message, parse_mode="HTML")

    def file_send(self, job_id,):
        # file = open(f'out/2cf0a00c-85eb-4839-8198-623935169090_confluence.csv')
        with io.StringIO() as file:
            file.write(u'x' * 100)
            file.name = "123123.txt"
            file.seek(0)
            response = self.bot.send_file(chat_id=self.chat, file=file.read(), caption=f"Report-{job_id}")
        file_id = response.json()['fileId']

    def run(self, message):
        print("START MYTEAM")
        print(message)
        self.send_report_text(message)


if __name__ == '__main__':
    print("Can't start script")
    exit()
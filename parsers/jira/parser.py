#!/usr/bin/python3

import logging
import warnings
from text import handler
from requests import HTTPError
from atlassian.errors import (
    ApiError
)
from atlassian.rest_client import AtlassianRestAPI
from atlassian import Jira
from bs4 import BeautifulSoup
from pprint import pprint

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


class JiraParser():
    def __init__(self, conf: dict):
        self.url = conf['url']
        self.user = conf['login']
        self.password = conf['password']
        self.type = 'jira'
        self.conf = conf
        self.wrapper = self.connect()

    def connect(self):
        if self.conf['oauth'] == True:
            with open(self.conf['private_key']) as f:
                key_cert_data = f.read()

            oauth2_dict = {
                "access_token": self.conf['client_id'],
                "access_token_secret": self.conf['client_secret'],
                "consumer_key": self.conf['consumer_key'],
                "key_cert": key_cert_data}
            jira = Jira(
                url=self.url,
                oauth=oauth2_dict)
        else:
            jira = Jira(
                url=self.url,
                username=self.user,
                password=self.password)

        return jira


    def make_childs_oneline(self, data: list) -> str:
        str = ' '.join(data)
        return str

    def get_all_comments(self, comments: str):
        data = []

        for comment in comments:
            c = comment['body']
            data.append(BeautifulSoup(c, "lxml").get_text(strip=True))

        if len(data) != 0:
            out_data = self.make_childs_oneline(data)
        else:
            out_data = None
        return out_data

    def run(self):
        jprojects = self.wrapper.projects(included_archived=None)

        spaces = []
        if len(self.conf['spaces']) == 0:
            for jp in jprojects:
                issues_count = self.wrapper.get_project_issues_count(jp['key'])
                spaces.append([jp['key'], issues_count])
        else:
            for s in self.conf['spaces']:
                issues_count = self.wrapper.get_project_issues_count(s)
                spaces.append([s, issues_count])
        # pprint(spaces)

        data_dict = {}
        for space, count in spaces:
            start_count = 0
            icount = []
            for i in range(0, count, 100):
                jpi = self.wrapper.get_all_project_issues(f"'{space}'", fields='*all', start=i, limit=100)
                icount += jpi

                for i in jpi:
                    pages_dict = {}
                    pages_dict['title'] = i['fields']['summary']
                    pages_dict['body'] = i['fields']['description']
                    pages_dict['id'] = i['id']
                    pages_dict['key'] = i['key']
                    pages_dict['space'] = i['fields']['project']['key']
                    pages_dict['comments'] = self.get_all_comments(i['fields']['comment']['comments'])
                    data_dict[i['id']] = pages_dict

                    if len(data_dict) == 10:
                        handler.process_text(data_dict, self.conf, self.type)
                        data_dict = {}

                start_count += 100


if __name__ == '__main__':
    print("Can't start script")
    exit()

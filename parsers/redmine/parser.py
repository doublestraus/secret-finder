#!/usr/bin/python3

import aiohttp
import asyncio
import json
import csv
import difflib
import argparse
import re
import time
import logging
import base64
import requests
from pprint import pprint
from aiohttp import ClientSession
from terminaltables import AsciiTable
from datetime import datetime

startup_config = {}

header = None
def proj_to_file(data_list):
    with open('temp/temp_projects_ids.csv', 'w') as fout:
        fout.write("id,identifier\n")
        for i in data_list:
            fout.write(i[0] + "," + i[1])
            fout.write('\n')


def issues_to_file(data_list):
    with open('temp/temp_issues_ids.csv', 'w') as fout:
        fout.write("id,\n")
        for i in data_list:
            fout.write(i + ",")
            fout.write('\n')


async def fetch(url, session):
    header = {"Authorization": "Basic cmVkbWluZTpLZE41OW0hTA=="}
    async with session.get(url, headers = header, timeout = -1) as response:
        x = await response.json()
        return x


async def get_all_projects(session, number_of_projects):
    projects = []
    tasks = []
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y-%H:%M:%S", named_tuple)
    print("[" + str(time_string) + "] Getting all projects...")
    sem = asyncio.Semaphore(2000)
    header = {"Authorization": "Basic cmVkbWluZTpLZE41OW0hTA=="}
    # conn = aiohttp.TCPConnector(limit=250, limit_per_host=10)
    # auth = aiohttp.BasicAuth(login=startup_config['login'], password=startup_config['password'], encoding='utf-8')
    async with ClientSession() as session:
        for i in range(0, number_of_projects + 1):
            task = asyncio.ensure_future(fetch(startup_config['projects_url'] + "?offset=" + str(i) + "&limit=1", session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        print("Got " + str(number_of_projects) + " projects")
        pprint(responses)
        projects_list = []
        for i in responses:
            project_list = i['projects']
            for j in project_list:
                # print("ID: " + str(j['id']) + " IDENTIFIER: " + str(j['identifier']))
                projects_list.append([str(j['id']), str(j['identifier'])])
        proj_to_file(projects_list)
        return projects_list


async def get_all_issues(counter, project_id, number_of_issues):
    issues = []
    tasks = []
    named_tuple = time.localtime()
    time_string = time.strftime("%m/%d/%Y-%H:%M:%S", named_tuple)
    print("[" + str(time_string) + "] [" + str(counter) + "] Getting issues for " + project_id)
    # sem = asyncio.Semaphore(200000)
    # conn = aiohttp.TCPConnector(limit=1000, limit_per_host=10)
    # auth = aiohttp.BasicAuth(login=startup_config['login'], password=startup_config['password'], encoding='utf-8')
    header = {"Authorization": "Basic cmVkbWluZTpLZE41OW0hTA=="}
    async with ClientSession(headers=header) as session:
        for i in range(0, number_of_issues + 1):
            task = asyncio.ensure_future(fetch(startup_config['issues_url'] + "?project_id=" + project_id + "&offset=" + str(i) + "&limit=1&status_id=*", session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        print("Got " + str(number_of_issues) + " issues")
        if responses[0] == None:
            return []
        else:
            for i in responses:
                issues_list = i['issues']
                for j in issues_list:
                    #print("ID: " + str(j['id']) + " IDENTIFIER: " + str(j['identifier']))
                    issues.append(str(j['id']))
            return issues


def get_count_projects(session):
    res = session.get(startup_config['projects_url']).json()
    count = res['total_count']
    return count


def init_session(login: str, passwd: str) -> object:
    s = requests.Session()
    s.auth = (login, passwd)
    return s


def run(conf: dict):
    """

    :return:
    """
    global startup_config
    global header
    startup_config = {
        "url": conf['url'],
        "login": conf['login'],
        "password": conf['password'],
        "projects_url": conf['url'] + "/projects.json",
        "issues_url": conf['url'] + "/issues.json",
        "issue_url": conf['url'] + "/issues/",
    }
    # print(conf)
    session = init_session(startup_config['login'], startup_config['password'])
    proj_count = get_count_projects(session)
    pprint(proj_count)

    try:
        ioloop = asyncio.get_event_loop()
        projects = ioloop.run_until_complete(get_all_projects(session, proj_count))
        pprint(projects)
        issues_list = []
        counter = 1
        for i in  projects:
            try:
                init_response = session.get(startup_config['issues_url'] + "?project_id=" + i[0] + "&offset=0&limit=1&status_id=*").json()
                number_of_issues = init_response['total_count']
            except:
                number_of_issues = 0
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(get_all_issues(counter, i[0], number_of_issues))
            issues_temp = loop.run_until_complete(future)
            issues_list.append(issues_temp)
            counter += 1
            number_of_issues = 0

        issues_list = sum(issues_list, [])
        issues_to_file(issues_list)

        # issues = ioloop.run_until_complete(process_text(res))
        # print_table(const.table_data)
    except Exception as ex:
        print(ex)
    finally:
        ioloop.close()


if __name__ == '__main__':
    print("Can't start script")
    exit()
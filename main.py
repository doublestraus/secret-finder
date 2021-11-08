#!/usr/bin/python3

import json
import argparse
import time
import traceback
import sys
import uuid
import parsers.confluence.parser as confluence_parser
import parsers.jira.parser as jira_parser
import parsers.redmine.parser as redmine_parser
from termcolor import colored, cprint
from datetime import datetime


def generate_job_id():
    return str(uuid.uuid4())


def check_conf(service_name: str):
    conf = {}
    if config[service_name]['url'] and len(config[service_name]['url']) != 0:
        conf['url'] = config[service_name]['url']
    else:
        raise Exception(f'{service_name} url error')

    if config[service_name]['credentials']['login'] and len(config[service_name]['credentials']['login']) != 0:
        conf['login'] = config[service_name]['credentials']['login']
    else:
        raise Exception(f'{service_name} login error')

    if config[service_name]['credentials']['password'] and len(config[service_name]['credentials']['password']) != 0:
        conf['password'] = config[service_name]['credentials']['password']
    else:
        raise Exception(f'{service_name} password error')

    if 'spaces' in config[service_name]:
        conf['spaces'] = config[service_name]['spaces']
    else:
        raise Exception('Spaces error')

    if 'oauth' in config[service_name]:
        conf['oauth'] = config[service_name]['oauth']
        conf['client_id'] = config[service_name]['credentials']['client_id']
        conf['client_secret'] = config[service_name]['credentials']['client_secret']
        conf['consumer_key'] = config[service_name]['credentials']['consumer_key']
        conf['private_key'] = config[service_name]['credentials']['private_key']
    else:
        raise Exception('Spaces error')



    if 'context_capture_span' in config['base_config']:
        conf['context_capture_span'] = config['base_config']['context_capture_span']
    else:
        conf['re_scan'] = 50

    if config['base_config']['re_scan']:
        conf['re_scan'] = config['base_config']['re_scan']
    else:
        conf['re_scan'] = True

    if config['base_config']['uuid_scan']:
        conf['uuid_scan'] = config['base_config']['uuid_scan']
    else:
        conf['uuid_scan'] = True

    if config['base_config']['twartefacts_scan']:
        conf['twartefacts_scan'] = config['base_config']['twartefacts_scan']
    else:
        conf['twartefacts_scan'] = True

    if config['base_config']['experimental_scan']:
        conf['experimental_scan'] = config['base_config']['experimental_scan']
    else:
        conf['experimental_scan'] = False

    if config['base_config']['gdocs_search']:
        conf['gdocs_search'] = config['base_config']['gdocs_search']
    else:
        conf['gdocs_search'] = False

    if config['base_config']['notifications']['myteam']['enabled'] is True:
        conf['myteam_notifications'] = config['base_config']['notifications']['myteam']

    if config['base_config']['notifications']['defectDojo']['enabled'] is True:
        conf['defecdojo_notifications'] = config['base_config']['notifications']['defectDojo']

    conf['badlist'] = config['lists']['badlist']
    conf['badrootlist'] = config['lists']['badrootlist']
    conf['job_id'] = generate_job_id()

    return conf


def run(config: dict):
    if not isinstance(config['lists']['badlist'], list):
        raise Exception('badlist error in config file')

    if not isinstance(config['lists']['badrootlist'], list):
        raise Exception('badrootlist error in config file')

    if args.redmine is True:
        conf = check_conf('redmine')
        print_start_out(conf['url'], 'redmine', conf['job_id'])
        redmine_parser.run(conf)

    if args.confluence is True:
        conf = check_conf('confluence')
        # print(conf)
        print_start_out(conf['url'], 'confluence', conf['job_id'])
        c = confluence_parser.ConfluenceParser(conf)
        c.run()

    if args.jira is True:
        conf = check_conf('jira')
        # print(conf)
        print_start_out(conf['url'], 'jira', conf['job_id'])
        j = jira_parser.JiraParser(conf)
        j.run()


def print_start_out(url: str, type: str, job_id: str):
    msg_1 = f"Start {type} parser: {url}"
    msg_2 = f"Started job ID: {job_id}"
    print(colored(msg_1, 'white', on_color='on_cyan', attrs=['bold','blink']))
    print(colored("".join(["=" * len(msg_1)]), 'magenta', on_color='on_white', attrs=['bold','blink']))
    print(colored(msg_2, 'white', on_color='on_cyan', attrs=['bold','blink']))


def get_config(path: str):
    with open(path) as json_file:
        config_data = json.load(json_file)
    return config_data


if __name__ == '__main__':
    start_time = time.time()
    try:
        parser = argparse.ArgumentParser(description='Sensitive finder v0.1')
        parser.add_argument('--config', help='Path to json config file', default='config.json')
        parser.add_argument('--redmine', help='Run Redmine parser', action='store_true', default=False)
        parser.add_argument('--confluence', help='Run Confluence parser', action='store_true', default=False)
        parser.add_argument('--jira', help='Run Jira parser', action='store_true', default=False)
        parser.add_argument('--debug', help='Enable debug', action='store_true', default=False)

        args = parser.parse_args()
        try:
            config = get_config(args.config)
        except Exception as ex:
            print(ex)
            sys.exit(0)

        try:
            run(config)
        except Exception as ex:
            print(ex)
            if args.debug == True:
                print(traceback.format_exc())
    finally:
        print("time elapsed: {:.2f}s".format(time.time() - start_time))
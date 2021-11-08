#!/usr/bin/python3

import csv
import os.path
import unicodedata
from notification import myteam
from notification import defectdojo
from datetime import datetime
from termcolor import colored, cprint


def generate(data: list, conf: dict, type: str):
    # table_data = [['Ticket #', 'Re check', 'UUID check', 'Diff check']]
    # table_data.append(data)
    job_id = conf['job_id']
    file_path = f'out/{job_id}_{type}.csv'
    if type == 'confluence' or type == 'jira':
        table_data_head = [['Ticket #', 'URL', 'Space', 'Context', 'Re check', 'UUID check', 'Gdocs links', 'TeamViewer', 'Possible password', 'Possible password  score']]
        if 'myteam_notifications' in conf:
            send_confluence_notification(data, conf)
        if 'defecdojo_notifications' in conf:
            send_in_dojo(data, 'confluence', conf)
    else:
        table_data_head = [['Ticket #', 'URL', 'Re check', 'Context', 'UUID check', 'Diff check']]

    if os.path.isfile(file_path) == True:

        write_csv_table(data, file_path)
    else:
        open(file_path, "w+")
        write_csv_table(table_data_head, file_path)
        write_csv_table(data, file_path)


def send_in_dojo(report, type, conf):
    '''
    #todo
    NOT WORK
    :param report:
    :param type:
    :param conf:
    :return:
    '''
    data = read_csv(report)
    dd = defectdojo.DefectDojo(api_key=conf['defecdojo_notifications']['api_key'],
                               user=conf['defecdojo_notifications']['user'],
                               host=conf['defecdojo_notifications']['defectDojo_url'],
                               type=type
                               )

    # eng_id = dd.create_eng(conf['job_id'])
    a = dd.add_finding(data)
    # dd.test()
    # dd.upload_findings(data)


def send_confluence_notification(data, conf):
    mt = myteam.Myteam(token=conf['myteam_notifications']['bot_secret'],
                       chat=conf['myteam_notifications']['channel_id'])
    for d in data:
        # context_str = unicodedata.normalize("NFKD", str(d[3]))
        message = f"<b>Ticket #:</b> <pre>{d[0]}</pre>\r\n "\
                    f"<b>Link:</b> {d[1]} \r\n"\
                    f"<b>Space:</b> <pre>{d[2]}</pre>\r\n"\
                    f"<b>Finded words:</b> {d[4]}\r\n"\
                    f"<b>Context:</b> {d[3]}\r\n"\
                    f"<b>UUID's:</b> {d[5]}\r\n"\
                    f"<b>External services links:</b> {d[6]}\r\n"

        mt.run(message)


def send_confluence_summary_report(d, conf):
    print(conf)
    mt = myteam.Myteam(token=conf['myteam_notifications']['bot_secret'],
                       chat=conf['myteam_notifications']['channel_id'])

    message = f"<b>Всего найдено:</b> <pre>{d['all']}</pre>\r\n "\
                f"<b>Найдено пространств:</b> <pre>{d['count_space']} </pre>\r\n"\
                f"<b>Найдено с помощью регулярныйх выражений:</b> <pre>{d['re_count']}</pre>\r\n"\
                f"<b>Найдено UUID:</b> <pre>{d['uuid_count']}</pre>\r\n"\
                f"<b>Найдено Google доков:</b> <pre>{d['gdocs_count']}</pre>\r\n" \
                f"<b>Найдено TeamViewer id:</b> <pre>{d['tw_count']}</pre>\r\n" \
                f"<b>Job id:</b> <pre>{d['job_id']}</pre>\r\n"

    mt.run(message)
    mt.file_send(d['job_id'])


def write_csv_table(table_data: list, file_path):
    with open(file_path, mode='a') as tickets_csv:
        tickets_csv = csv.writer(tickets_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for td in table_data:
            tickets_csv.writerow(td)


def prepare_summary_report(file_path, conf):
    report_dict = {}
    o = read_csv(file_path)
    report_dict['all'] = len(o[1:])
    raw_spaces = []
    print(len(o[1:]))
    for i in o[1:]:
        raw_spaces.append(i[2])

    spaces = list(set(raw_spaces))
    report_dict['count_space'] = len(spaces)
    report_dict['re_count'] = 0
    report_dict['uuid_count'] = 0
    report_dict['gdocs_count'] = 0
    report_dict['tw_count'] = 0
    for i in o[1:]:
        #RE check
        if i[4] != 'N/A':
            report_dict['re_count'] += 1
        #UUID
        if i[5] != 'N/A':
            report_dict['uuid_count'] += 1
        #GDOCS links
        if i[6] != 'N/A':
            report_dict['gdocs_count'] += 1
        #TW ids
        if i[7] != 'N/A':
            report_dict['tw_count'] += 1

    report_dict['job_id'] = conf['job_id']
    print(f"{report_dict}")

    send_confluence_summary_report(report_dict, conf)


def read_csv(file_path: str):
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        return data


if __name__ == '__main__':
    print("Can't start script")
    exit()
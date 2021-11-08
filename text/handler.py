#!/usr/bin/python3

import re
import report
import unicodedata

def sanitise(s: str) -> object:
    """

    :param s:
    :return:
    """
    return re.sub('[!@#$,"\'()]', '', s)


def find_uuid(s: str) -> object:
    """

    :param s:
    :return:
    """
    c = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', re.I)
    return c.match(s)


def find_tw_id(s: str) -> object:
    """
    :param s:
    :return:
    """
    # c = re.compile(r'\d([0-9-\s]{9,11})\d')
    c = re.compile(r'\d+( \d+)+')
    return c.search(s)


def prepare_text(s: str):
    str = " ".join(s.splitlines())
    str_raw = sanitise(str)
    str_out = str_raw.lower().split()
    descr_set = set(str_out)
    return descr_set


def has_cyrillic(pw):
    a = bool(re.search('[а-яА-Я]', pw))
    # print("has cyrillic" + str(a))
    return a


def get_pw_strength(pw):
    password_user = pw
    score = 0
    try:
        if has_cyrillic(password_user) is False:
            if len(password_user) <= 5:
                score = 1
            elif password_user == password_user.lower():
                score = 1
            elif password_user == password_user.upper():
                score = 1
            else:
                while score == 0:
                    for x in range(33, 48):
                        ascii_str = chr(x)
                        if password_user.find(ascii_str) >= 0:
                            score = score + 3
                    for y in range(97, 123):
                        ascii_lower = chr(y)
                        if password_user.find(ascii_lower) >= 0:
                            score = score + 1
                    for w in range(65, 91):
                        # print(w)
                        ascii_upper = chr(w)
                        if password_user.find(ascii_upper) >= 0:
                            score = score + 2
                    for z in range(48, 58):
                        ascii_num = chr(z)
                        if password_user.find(ascii_num) >= 0:
                            score = score + 2
        else:
            score = 1
    except Exception:
        score = 1

    return score


def process_text(retrieved_data: dict, conf: dict, type: str):
    """
    :param retrieved_data:
    :return:
    """
    out_data = []
    chunk = len(retrieved_data)
    # print(f"start process text chunk {chunk}")
    # print(retrieved_data)
    for id, data in retrieved_data.items():
        # out_data.append(id)
        s = "{} {} {}".format(data['title'], data['body'], data['comments'])
        # print(s)
        text = prepare_text(s)
        raw_text = " ".join(s.splitlines())
        # print(raw_text)

        context_list = []
        full_context = "N/A"
        n_word = "N/A"
        pp_strength = "N/A"
        if conf['re_scan'] == True:
            base_out_list = []
            for root in conf['badrootlist']:
                c = re.search(rf'.?({root}).?', raw_text)
                # print(raw_text)
                if c is not None:
                    base_out_list.append(c.group(0))
                    # print(base_out_list)
                    # context = re.search(r"(.{,20})(" + root + ")(.{,20})", raw_text)

                    span_L = c.span()[0] - conf['context_capture_span']
                    span_R = c.span()[1] + conf['context_capture_span']
                    context_left = raw_text[span_L:c.span()[0]]
                    context_right = raw_text[c.span()[1]:span_R]
                    context_list = context_right.split()
                    # print(c.span())
                    # context_list.append(unicodedata.normalize("NFKD", context.group(0)))
                    # print(c.span())
            base_out = ' '.join(base_out_list)
            if base_out == '':
                base_out = "N/A"
            else:
                full_context = "{}{}{}".format(context_left, base_out_list[0], context_right)
                try:
                    n_word = context_list[0]
                except IndexError:
                    n_word = 0

                invalid = ['!', '"', '#', '$', '%', '&', '\\', '(', ')', '*', '+', ',', '-', '.', '/',
                           ':', ';', '<', '=', '>', '?', '@', '[', "'", ']', '^', '`', '{', '|', '}', '~', ' ', '_']
                if n_word in invalid:
                    n_word = context_list[1]

                pp_strength = get_pw_strength(n_word)


        uuid_out_list = []
        if conf['uuid_scan'] == True:
            for word in text:
                if find_uuid(word) is not None:
                    uuid_out_list.append(find_uuid(word).group(0))

            if len(uuid_out_list) == 0:
                uuid_out_list = 'N/A'

        digits_artefacts_str = 'N/A'
        if conf['twartefacts_scan'] == True:
            c = re.search(
                '(\D|^)(((1(?P<tag1>-|\s))?\d{3}(?P<tag2>-|\s)\d{3}(?P=tag2)\d{3})|((m|s)\d{2}(?P<tag3>-|\s)\d{3}(?P=tag3)\d{3}))(\D|$)',
                raw_text)
            if c is not None:
                digits_artefacts_str = c.group(0)

        gdocs = "N/A"
        if conf['gdocs_search'] == True:
            c = re.search(
                '(?P<url>https?://docs.google.com[^\s]+)',
                raw_text)
            if c is not None:
                gdocs = c.group("url")

        if base_out != 'N/A' or digits_artefacts_str != 'N/A' or gdocs != 'N/A':
            if type == 'confluence':
                url = f"{conf['url']}/pages/viewpage.action?pageId={id}"
            elif type == 'jira':
                url = f"{conf['url']}/browse/{data['key']}"
            else:
                url = "N/A"
            out_data.append([id,
                             url,
                             data['space'],
                             full_context,
                             base_out,
                             uuid_out_list,
                             gdocs,
                             digits_artefacts_str,
                             n_word,
                             pp_strength])

    report.generate(out_data, conf, type)
    return out_data


if __name__ == '__main__':
    print("Can't start script")
    exit()
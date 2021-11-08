#!/usr/bin/python3

import logging

from text import handler
from requests import HTTPError
from atlassian.errors import (
    ApiError
)
from atlassian.rest_client import AtlassianRestAPI
from atlassian import Confluence
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


class ConfluenceParser():
    def __init__(self, conf: dict):
        self.url = conf['url']
        self.user = conf['login']
        self.password = conf['password']
        self.type = 'confluence'
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
            confluence = Confluence(
                url=self.url,
                oauth=oauth2_dict,
                verify_ssl=False)
        else:
            confluence = Confluence(
                url=self.url,
                username=self.user,
                password=self.password,
                verify_ssl=False)

        return confluence

    def get_page_child_by_type(self, page_id, type='comment', start=None, limit=None):
        params = {}
        if start is not None:
            params["start"] = int(start)
        if limit is not None:
            params["limit"] = int(limit)

        url = "/rest/api/content/{page_id}/child/{type}?expand=body.view".format(page_id=page_id, type=type)
        log.info(url)

        try:
            response = AtlassianRestAPI.get(self.wrapper, path=url, params=params)
        except HTTPError as e:
            if e.response.status_code == 404:
                # Raise ApiError as the documented reason is ambiguous
                raise ApiError(
                    "There is no content with the given id, "
                    "or the calling user does not have permission to view the content",
                    reason=e,
                )

            raise

        return response.get("results")

    def get_all_pages_from_space(self, space):
        res = self.wrapper.get_all_pages_from_space(space, start=0, limit=1000, status=None, expand=None, content_type='page')
        return res

    def get_page_by_id(self, id: int):
        res = self.wrapper.get_page_by_id(id, expand='space,history,body.view,metadata.labels', status=None, version=None)
        return res

    def get_page_child_by_id(self, id):
        res = self.get_page_child_by_type(id, type='comment', start=None, limit=None)
        return res

    def get_all_spaces(self, limit: int = 100):
        res = self.wrapper.get_all_spaces(start=0, limit=limit, expand=None)
        return res

    def make_childs_oneline(self, data: list) -> str:
        str = ' '.join(data)
        return str

    def get_all_comments(self, id: int):
        data = []
        res = self.get_page_child_by_id(id)
        for r in res:
            # data.append(BeautifulSoup(r['body']['view']['value'], "lxml").text)
            data.append(BeautifulSoup(r['body']['view']['value'], "lxml").get_text(strip=True))

        if len(data) != 0:
            out_data = self.make_childs_oneline(data)
        else:
            out_data = None
        return out_data

    def run(self):
        """
        :return:
        """
        space_list = []
        pages_id_list = []
        data_dict = {}

        # Get spaces from confluence
        if len(self.conf['spaces']) == 0:
            spaces = self.get_all_spaces(limit=100)
            for s in spaces['results']:
                space_list.append(s['key'])
        else:
            for s in self.conf['spaces']:
                space_list.append(s)

        # Get all pages from spaces
        for space in space_list:
            pages = self.get_all_pages_from_space(space)
            for page in pages:
                pages_id_list.append([page['id'], space])

        for id in pages_id_list:
            page_id = int(id[0])
            space_name = id[1]
            print(f"Get page {page_id} in space {space_name}")
            pages_dict = {}
            temp_page = self.get_page_by_id(page_id)
            pages_dict['title'] = temp_page['title']
            pages_dict['body'] = BeautifulSoup(temp_page['body']['view']['value'], "lxml").get_text()
            pages_dict['comments'] = self.get_all_comments(page_id)
            pages_dict['space'] = space_name
            data_dict[page_id] = pages_dict
            # Create chunk and process text
            if len(data_dict) == 10:
                handler.process_text(data_dict, self.conf, self.type)
                data_dict = {}


if __name__ == '__main__':
    print("Can't start script")
    exit()
#!/usr/bin/python3

import json
import requests
import requests.exceptions


class DefectDojo():
    """
    Initialize a DefectDojo API instance.
    """
    def __init__(self, api_key, user, host, user_agent=None, verify_ssl=False, api_version='v2', timeout=60, debug=True):
        self.api_key = api_key
        self.user = user
        self.host = host + '/api/' + api_version + '/'
        self.verify_ssl = verify_ssl
        self.api_version = api_version
        self.timeout = timeout

        if not user_agent:
            self.user_agent = 'DefectDojo_api'
        else:
            self.user_agent = user_agent

        self.debug = debug

    def get_users(self, username=None, limit=20):
        params = {}
        if limit:
            params['limit'] = limit

        if username:
            params['username'] = username

        return self._request('GET', 'users/', params)

    def _request(self, method, url, params=None, data=None, files=None):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        if data:
            data = json.dumps(data)

        headers = {
            'User-Agent': self.user_agent,
            'Authorization' : "Token " + self.api_key
        }

        if not files:
            headers['Content-Type'] = 'application/json'

        try:
            if self.debug:
                print(method + ' ' + self.host + url)
                print(params)
                print(headers)

            response = requests.request(method=method, url=self.host + url, params=params, data=data, files=files,
                                        headers=headers,
                                        timeout=self.timeout,
                                        verify=self.verify_ssl)

            if self.debug:
                print(response.status_code)
                print(response.text)


        #     try:
        #         if response.status_code == 201: #Created new object
        #             object_id = response.headers["Location"].split('/')
        #             key_id = object_id[-2]
        #             try:
        #                 data = int(key_id)
        #             except:
        #                 data = response.json()
        #
        #             return DefectDojoResponse(message="Upload complete", data=data, success=True)
        #         elif response.status_code == 204: #Object updates
        #             return DefectDojoResponse(message="Object updated.", success=True)
        #         elif response.status_code == 400: #Object not created
        #             return DefectDojoResponse(message="Error occured in API.", success=False, data=response.text)
        #         elif response.status_code == 404: #Object not created
        #             return DefectDojoResponse(message="Object id does not exist.", success=False, data=response.text)
        #         elif response.status_code == 401:
        #             return DefectDojoResponse(message="Unauthorized.", success=False, data=response.text)
        #         elif response.status_code == 414:
        #             return DefectDojoResponse(message="Request-URI Too Large.", success=False)
        #         elif response.status_code == 500:
        #             return DefectDojoResponse(message="An error 500 occured in the API.", success=False, data=response.text)
        #         else:
        #             data = response.json()
        #             return DefectDojoResponse(message="Success", data=data, success=True, response_code=response.status_code)
        #     except ValueError:
        #         return DefectDojoResponse(message='JSON response could not be decoded.', success=False, data=response.text)
        # except requests.exceptions.SSLError:
        #     return DefectDojoResponse(message='An SSL error occurred.', success=False)
        # except requests.exceptions.ConnectionError:
        #     return DefectDojoResponse(message='A connection error occurred.', success=False)
        # except requests.exceptions.Timeout:
        #     return DefectDojoResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.',
        #                              success=False)
        except requests.exceptions.RequestException:
            return DefectDojoResponse(message='There was an error while handling the request.', success=False)




class DefectDojoResponse(object):
    """
    Container for all DefectDojo API responses, even errors.

    """

    def __init__(self, message, success, data=None, response_code=-1):
        self.message = message
        self.data = data
        self.success = success
        self.response_code = response_code

    def __str__(self):
        if self.data:
            return str(self.data)
        else:
            return self.message

    def id(self):
        if self.response_code == 400: #Bad Request
            raise ValueError('Object not created:' + json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': ')))
        return int(self.data)

    def count(self):
        return self.data["meta"]["total_count"]

    def data_json(self, pretty=False):
        """Returns the data as a valid JSON string."""
        if pretty:
            return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.data)



if __name__ == '__main__':
    pass
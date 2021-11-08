#!/usr/bin/python3

from notification.DefectDojoApi import *
from datetime import date
from pprint import pprint


class DefectDojo():
    """
    Initialize a DefectDojo API instance.
    """
    def __init__(self, api_key, user, host, type, ):
        self.api_key = api_key
        self.user = user
        self.host = host
        self.type = type
        self.wrapper = DefectDojoAPIv2(host, api_key, user, debug=False)

    def add_finding(self, data):
        today = date.today()
        # print(engagement_id)
        finding = self.wrapper.create_finding(title="test ss finding123",
                                              description="test ss descr",
                                              found_by=[139],
                                              product_id=12,
                                              severity='Medium',
                                              cwe=0,
                                              date=today.strftime("%Y-%m-%d"),
                                              engagement_id=86,
                                              user_id='sec',
                                              test_id=2,
                                              impact='test impact',
                                              active='true',
                                              verified='No',
                                              mitigation='no',
                                              numerical_severity='None'
                                            )
        print(finding)

    def upload_findings(self, data):
        for t in data:
            print(t)
        # upload = self.wrapper.upload_scan()


    def test(self):
        a = self.wrapper.list_products()
        pprint(a.data)
        # for i in a:
        #     print(i)

    def create_eng(self, job_id):
        today = date.today()
        eng = self.wrapper.create_engagement(name=f'Scan {self.type} job_id {job_id}',
                                             product_id=12,
                                             status='Completed',
                                             lead_id=2,
                                             target_start=today.strftime("%Y-%m-%d"),
                                             target_end=today.strftime("%Y-%m-%d"),
                                             engagement_type='Interactive'
                                             )
        # data = json.loads(eng)
        # print(data.id())
        # print(eng.id())
        return eng.id()


if __name__ == '__main__':
    print("Can't start script")
    exit()
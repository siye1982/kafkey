#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
import unittest
from app import create_app
import app

__author__ = 'panda'


class MessageTestCase(unittest.TestCase):


    def obj_to_json(self, obj):
        return json.dumps(obj, encoding='utf8', ensure_ascii=False, indent=2)


    def json_to_obj(self,json_str):
        return json.loads(json_str, encoding='utf8')


    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_es_client(self):
        self.assertTrue(app.es is not None)

    def test_query(self):
        res = app.es.search(index="kafka_msg_log_2016.03.17", body={"query": {"match_all": {}}})
        print("Got %d Hits" % res['hits']['total'])

    # 根据mid获取整个消息传递链信息
    def test_query_by_mid(self):
        res = app.es.search(
                index="kafka_msg_log_2016.03.17",
                body={
                        "from": 0,
                        "size": 10000,
                        "query": {
                            "bool": {
                                "must": {
                                    "term": {
                                        "mid": "96d223ed-203c-4807-a73d-3f3cdbecb57c"
                                    }
                                }
                            }
                        }
                     }
                )
        for obj in res['hits']['hits']:
            print self.obj_to_json(obj['_source'])

        # print("Got %d Hits" % res['hits']['total'])

    # 统计有哪些msg传递过程中缺失四个过程
    def test_aggs_broke_mid(self):
        res = app.es.search(
                index="kafka_msg_log_2016.03.17",
                body={
                        "from": 0,
                        "size": 10000,
                        "query": {
                            "bool": {
                                "must": {
                                    "missing": {
                                        "field": "etype"
                                    }
                                }
                            }
                        },
                        "aggs": {
                            "mid": {
                                "terms": {
                                    "field": "mid",
                                    "size": 10000
                                    # "min_doc_count": 3
                                },
                                "aggs": {
                                    "mid_count": {
                                        "value_count": {
                                            "field": "mid"
                                        }
                                    }
                                }
                            }
                        }
                    }
                )
        count = 0
        for obj in res['aggregations']['mid']['buckets']:
            if obj['doc_count'] < 4 :
                count = count + 1
                print 'mid: [' + obj['key'] + ']  count: [' + str(obj['doc_count']) + ']'
            # print self.obj_to_json(obj)
        print 'count: [' + str(count) + ']'







        # 统计有哪些msg传递过程中缺失四个过程
    def test_aggs_broke_mid2(self):
        res = app.es.search(
                index="kafka_msg_log_2016.03.17",
                body={
                        "from": 0,
                        "size": 10000,
                        "query": {
                            "bool": {
                                "must": {
                                    "missing": {
                                        "field": "etype"
                                    }
                                }
                            }
                        },
                        "aggs": {
                            "mid": {
                                "terms": {
                                    "field": "mid",
                                    "size": 10000
                                    # "min_doc_count": 3
                                },
                                "aggs" : {
                                    "total_stage" : {
                                        "sum" : {
                                            "field" : "stage",
                                            "missing": 4
                                        }
                                    }
                                }
                            }
                        }
                    }
                )
        count = 0
        for obj in res['aggregations']['mid']['buckets']:
            count = count + 1
            print 'mid: [' + obj['key'] + ']  count: [' + str(obj['doc_count']) + ']'
            # print self.obj_to_json(obj)
        print 'count: [' + str(count) + ']'






    # 统计一天范围内所有错误的异常
    def test_aggs_error(self):
        res = app.es.search(
                index="kafka_msg_log_2016.03.17",
                body={
                        "from": 0,
                        "size": 10000,
                        "query": {
                            "bool": {
                                "must_not": {
                                    "missing": {
                                        "field": "etype"
                                    }
                                }
                            }
                        },
                        "aggs" : {
                            "error_count" : {
                                "date_histogram" : {
                                    "field" : "timestamp",
                                    "interval" : "10m",
                                    "format" : "yyyy-MM-dd HH:mm"
                                }
                            }
                        }
                    }
                )
        for obj in res['aggregations']['error_count']['buckets']:
            print 'datetime: [' + obj['key_as_string'] + ']  count: [' + str(obj['doc_count']) + ']'


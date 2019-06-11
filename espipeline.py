#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: tango 
@file: es_.py 
@time: 2019/04/24
@desc: 
    
"""
import datetime
import time
import hashlib
from elasticsearch import Elasticsearch

class EsPipeline(object):
    init_config = {
        "settings": {
            "number_of_shards": "2",
            "number_of_replicas": "1"
        },
        "mappings":
            {
                "spu": {
                    "dynamic": "strict",
                    "properties": {
                        "title": {"type": "text", "store": "yes", "analyzer": "ik_max_word",
                                  "search_analyzer": "ik_max_word"},
                        "spu_id": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "desc ": {"type": "keyword"},
                        "brand ": {"type": "keyword"},
                        "site_name": {"type": "keyword"},
                        "status ": {"type": "integer"},
                        "sku": {"properties": {
                            "spec": {"type": "text", "store": "yes", "analyzer": "ik_max_word",
                                     "search_analyzer": "ik_max_word"},
                            "sku_id": {"type": "keyword"},
                            "price": {"type": "float"}
                        }},
                        "date": {"type": "date",
                                 "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"}
                    }
                }

            }

    }

    def __init__(self, host="127.0.0.1:9200", index="goods", doc_type="sku"):
        self.es = Elasticsearch(hosts=[host])
        self.doc_type = doc_type
        self.index = index
        if not self.es.indices.exists(index=index):
            self.es.indices.create(index=index, body=self.init_config)

    def process_item(self,item,spider):
        if isinstance(item,DetailItem):
            data=dict(item)
            info={}
            spu_info = data.get("data",{}).get("spu_info")
            sku_info = data.get("data",{}).get("sku_info",[])
            _id = self.to_hash(spu_info.get("title")+str(spu_info.get("spu_id"))+spu_info.get("site_name"))
            info["title"] = spu_info.get("title")
            info["spu_id"] = spu_info.get("spu_id")
            info["category"] = spu_info.get("category_three") or spu_info.get("category_two")
            info["des"] = spu_info.get("feature")
            info["brand"] = spu_info.get("brand")
            info["site_name"] = spu_info.get("site_name")
            info["date"] = get_second()
            info["sku"] = [ {"spec":tmp.get("spec"),"sku_id":tmp.get("sku_id"),"price":tmp.get("discount_price")} for tmp in sku_info]
            if self.query_data(id=_id):
                self.update_data(id=_id,data=info,spider=spider)
            else:
                self.create_data(id=_id,data=info,spider=spider)
        return item

    def update_data(self,id,data,spider):
        """

        :param data:
        :return:
        """
        try:
            self.es.update(index=self.index, doc_type=self.doc_type,id=id,body={"doc":data})
        except Exception as e:
            spider.logger.error("update failed! :%s"%(e,))

    def create_data(self, id,data,spider):
        """
        one:
        self.es.index(index=index,doc_type=self.doc_type,body=data)
        more:
        actions = [
        {
            '_op_type': 'index',
            '_index': "http_code",  //index
            '_type': "error_code",  //type
            '_source': d
        }
            for d in data
            ]
        helpers.bulk(self.es,actions)
        :return:data:{"title":"","":""}
        """
        try:
            self.es.index(index=self.index, doc_type=self.doc_type, body=data,id=id)
        except Exception as e:
            spider.logger.error("ES insert faild :%s" % (e,))

    def delete_data(self, id="", query=None):
        """
        1. self.es.delete()
        2. self.es.delete_by_query()

        :param id: doc's _id
        :return:
        """
        if not query:
            self.es.delete(index=self.index, doc_type=self.doc_type, id=id)
        else:
            self.es.delete_by_query(index=self.index, doc_type=self.doc_type, body=query)

    def query_data(self, query="",id=None):
        """
        self.es.get(index=self.index, doc_type=self.doc_type,id=id) #没结果会报错
        ex:
                {
            "query": {
                "bool": {
                    "must": {
                        "bool" : { "should": [
                              { "match": { "title": "Elasticsearch" }},
                              { "match": { "title": "Solr" }} ] }
                    },
                    "must": { "match": { "authors": "clinton gormely" }},
                    "must_not": { "match": {"authors": "radu gheorge" }}
                }
            }
        }
        fuzzy:
            {
	        "que    ry": {
	            "multi_match" : {
	                "query" : "comprihensiv guide",
	                "fields": ["title", "summary"],
	                "fuzziness": "AUTO"
	            }
	        },
	        "_source": ["title", "summary", "publish_date"],
	        "size": 1
	    	}
        wildcard:
            {
        	"query": {
            "wildcard" : {
                "authors" : "t*"
            }
		        }
		    "_source": ["title", "authors"],
		        }
        Reg:
		        {
		    "query": {
		        "regexp" : {
		            "authors" : "t[a-z]*y"
		        }
		    },
		    "_source": ["title", "authors"],
		    "highlight": {
		        "fields" : {
		            "authors" : {}
		        }
		    }
			}
        :param query: comform to elasticsearch-dsl
        :return:
        """
        if id:
            query={"query":{"term":{"_id":"%s"%(id,)}}}
        result = self.es.search(index=self.index, doc_type=self.doc_type, body=query)
        return result.get("hits", {}).get("hits", [])


    @staticmethod
    def to_hash(field):
        return hashlib.md5(str(field).encode("utf8")).hexdigest()[:16]

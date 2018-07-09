import json, os, requests
from elasticsearch import Elasticsearch, helpers
import pprint
from time import sleep

def get_recipes_all(recipe_id=None):
  if recipe_id:
    try:
      print('現在のID:',recipe_id)
      url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?'
      st_load = {
        'applicationId': os.environ['RAKUTEN_APP_ID'],
        'categoryId': recipe_id
      }
      r = requests.get(url, params=st_load)
      res = r.json()
      data = res['result']
      save_recipes(data)  # ここで時間稼ぎも兼ねてsaveする
      sleep(3)  # 高速でAPIを叩くと止まるため待つ
    except:
      print("Error")
      sleep(10)  # 高速でAPIを叩くと止まるため待つ
      pass
  elif recipe_id==None:
    # Maxは55
    for i in range(10, 55 + 1):
      try:
        print('現在のID:',i)
        url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?'
        st_load = {
          'applicationId': os.environ['RAKUTEN_APP_ID'],
          'categoryId': i
        }
        r = requests.get(url, params=st_load)
        res = r.json()
        # pp = pprint.PrettyPrinter(indent=2)
        data = res['result']
        # pp.pprint(result)
        save_recipes(data)  # ここで時間稼ぎも兼ねてsaveする
        sleep(10)  # 高速でAPIを叩くと止まるため待つ
      except:
        print("Error")
        sleep(10)  # 高速でAPIを叩くと止まるため待つ
        pass
    # return result

def save_recipes(data):
  es = Elasticsearch([os.environ.get('BONSAI_URL')] or ['http://localhost:9200'])
  actions = []
  pp = pprint.PrettyPrinter(indent=2)
  for datapoint in data:
    pp.pprint(datapoint)
    es.index(index='cook', doc_type='recipe', body=datapoint)
    # actions.append({
    #   "_index": "cook",
    #   "_type":  "recipe",
    #   "_source": datapoint
    # })
  # helpers.bulk(es, actions)

def search_by_material(material_list):
  for material in material_list:
    print('食材は{}です。'.format(material))
    es = Elasticsearch([os.environ.get('BONSAI_URL')] or ['http://localhost:9200'])
    res = es.search(index='cook',body={ "query": { "bool": { "must": [ { "match_phrase": { "recipeMaterial": material } } ] } } })
    if res['hits']['total'] == 0:
      continue
    else:
      print(res['hits']['hits'])
      return res['hits']['hits']
  return False

# if __name__ == '__main__':
  # data = get_recipes_all()
  # search_by_material('ばなな')
  # search_by_material('水')
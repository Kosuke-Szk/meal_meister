import requests
from keras import models

class UtilClass:
  is_model_loaded = False

  def change_to_loaded(self):
    self.is_model_loaded = True

  def get_status(self):
    return self.is_model_loaded


def count_words_at_url(url):
    resp = requests.get(url)
    print(len(resp.text.split()))
    return len(resp.text.split())

def load_model():
    print('New model')
    # app.jinja_env.globals['model'] = models.load_model('inception_v3.h5')
    # app.jinja_env.globals['graph'] = tf.get_default_graph()
    model = models.load_model('inception_v3.h5')
    # graph = tf.get_default_graph()
    print('Loaded the model')
    print('This is rq', model)
    return model
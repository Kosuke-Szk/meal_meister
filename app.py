from flask import Flask, redirect, request, jsonify, abort
from keras import models
import numpy as np
from PIL import Image
import io

from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input, decode_predictions
import tensorflow as tf
import os
import sys

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)
model = None

# Set my LINE data
channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('event!!!!!!:', event.reply_token)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

def load_model():
    global model
    global graph
    model = models.load_model('inception_v3.h5')
    graph = tf.get_default_graph()
    model.summary()
    print('Loaded the model')

def model_predict(img_path, model):
    with graph.as_default():
        img = image.load_img(img_path, target_size=(224,224))
        # Preprocessing the image
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)
        return preds

@app.route('/predict', methods=['POST'])
def predict():
    if request.files and 'picfile' in request.files:
        img = request.files['picfile']
        img.save('./test.jpg')
        preds = model_predict('./test.jpg', model)
        pred_class = decode_predictions(preds, top=1)
        result = str(pred_class[0][0][1])
        print(result)
        return result
    return None

# @app.route('/currentimage', methods=['GET'])
# def current_image():
#     fileob = open('test.jpg', 'rb')
#     data = fileob.read()
#     return data

if __name__ == '__main__':
    # load_model()
    app.run()

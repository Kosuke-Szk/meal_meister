from flask import Flask, redirect, request, jsonify, abort
from keras import models
import numpy as np
import translate
import recipe
import japanese_conv
import io
from io import BytesIO

from rq import Queue
from worker import conn

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
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)
from PIL import Image

app = Flask(__name__)
q = Queue(connection=conn)

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
    q.enqueue(load_model)
    return "hello world!"

@app.route("/get_recipes_Cfd454aD")
def get_recipes_all():
    recipe.get_recipes_all()

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
    text = event.message.text

    messages = [
        TextSendMessage(text=text),
        TextSendMessage(text='画像を送ってみてね'),
    ]

    reply_message(event, messages)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    image = BytesIO(message_content.content)
    image = Image.open(image)
    recipe_list, object_name = predict(image)
    if recipe_list:
        print(recipe_list)
        for recipe in recipe_list:
            try:
                messages = [
                    TextMessage(text='{}が見えるな〜'.format(object_name)),
                    TextSendMessage(text=str(recipe['_source']['recipeTitle'])),
                    TextSendMessage(text=str(recipe['_source']['recipeUrl']))
                ]
                reply_message(event, messages)
            except Exception as e:
                print("error:", e)
                reply_message(event, TextSendMessage(text='エラーが発生しました'))
    else:
        print("No recipe hit")
        try:
            messages = [
                TextMessage(text='{}が見えるな〜'.format(object_name)),
                TextSendMessage(text="レシピはないみたい・・・")
            ]
            reply_message(event, messages)
        except Exception as e:
            print("error:", e)
            reply_message(event, TextSendMessage(text='エラーが発生しました'))

def reply_message(event, messages):
    line_bot_api.reply_message(
        event.reply_token,
        messages=messages,
    )

def load_model():
    try:
        model = app.jinja_env.globals['model']
        graph = app.jinja_env.globals['graph']
    except:
        print('New model')
        app.jinja_env.globals['model'] = models.load_model('inception_v3.h5')
        app.jinja_env.globals['graph'] = tf.get_default_graph()
        print('Loaded the model')

def model_predict(img_path, model):
    with app.jinja_env.globals['graph'].as_default():
        img = image.load_img(img_path, target_size=(224,224))
        # Preprocessing the image
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = model.predict(x)
        return preds

def predict(img):
    model = app.jinja_env.globals['model']
    img.save('./test.jpg')
    preds = model_predict('./test.jpg', model)
    pred_class = decode_predictions(preds, top=1)
    result = str(pred_class[0][0][1])
    result = str(translate.get_translated_text(result))
    result_list = [japanese_conv.kata_to_hira(result), japanese_conv.hira_to_kata(result)]
    recipe_list = recipe.search_by_material(result_list)
    return recipe_list, result

# @app.before_request
# def before_request():


import http.client, urllib.parse, uuid, json, os, sys

host = 'api.cognitive.microsofttranslator.com'
path = '/translate?api-version=3.0'
# Translate to Japan.
params = "&to=ja";

def translate (content):
    headers = {
        'Ocp-Apim-Subscription-Key': os.environ['MICROSOFT_TRANSLATE_KEY'],
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    conn = http.client.HTTPSConnection(host)
    conn.request ("POST", path + params, content, headers)
    response = conn.getresponse ()
    return response.read ()

def get_translated_text(text):
    requestBody = [{
        'Text' : text,
    }]
    content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
    result = translate(content)
    output = json.loads(result)
    output = output[0]['translations'][0]['text']
    return output

if __name__ == '__main__':
    text='Hello'
    get_translated_text(text)
import json
import quart
import quart_cors
from quart import request, render_template
import os
from lc import get_relevant_info_from_question
from dotenv import load_dotenv
from posthog import Posthog

load_dotenv()

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

posthog = Posthog(project_api_key=os.getenv("POSTHOG_API_KEY"), host='https://app.posthog.com')

@app.route('/', methods=['GET'])
async def hello():
    posthog.capture("pageview", "main")
    return await render_template('index.html')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")
    
@app.get("/logo.png")
async def plugin_logo():
    filename = 'askmfm.png'
    return await quart.send_file(filename, mimetype='image/gif')

@app.get("/legal")
async def legal():
    return await render_template('legal.html')

@app.route('/relevant-info', methods=['POST'])
async def get_relevant_info():
    try:
        request_data = await request.get_json(force=True)
        question = request_data['question']
        relevant_info = get_relevant_info_from_question(question)
        posthog.capture("question", question)
        return quart.Response(response=json.dumps({'status': 'success', 'relevant_info': relevant_info}), status=200)
    except Exception as e:
        print(str(e))
        return quart.Response(response=json.dumps({'status': 'error', 'message': str(e)}), status=400)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=os.getenv("PORT"))

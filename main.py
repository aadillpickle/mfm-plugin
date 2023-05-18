import json
import quart
import quart_cors
from quart import request
import os
import openai
from operand.client import OperandServiceClient, SearchRequest
from dotenv import load_dotenv

load_dotenv()

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")

openai.api_key = os.getenv("OPENAI_API_KEY")
operandClient = OperandServiceClient("https://mcp.operand.ai", os.getenv("OPERAND_API_KEY"))

def operand_search_relevant_info(question):
    relevant_info = []
    req = SearchRequest(
        query=question,
        max_results=10,
    )
    resp = operandClient.search(req)
    file_ids_and_names = {}

    # print(resp.files)
    files = resp.files.items()
    for file_id, file in files:
        file_ids_and_names[file_id] = file.name
  
    for match in resp.matches:
        snippet = match.snippet
        snippet_file_id = match.file_id
        file_name = file_ids_and_names[snippet_file_id]
        podcast_title = str(file_name[:-4])
        podcast_link = ""
        with open('titles_and_links.json') as f:
            data = json.load(f)
            #check if the first 20 chars of the podcast title match the first 20 chars of any of the json keys
            for key in data.keys():
                if podcast_title[:20] == key[:20]:
                    podcast_link = data[key]
            # podcast_link = data[podcast_title]
            relevant_info.append({
                "snippet": snippet,
                "podcast_title": podcast_title,
                "link": podcast_link  
            })
    return relevant_info

@app.route('/', methods=['GET'])
async def hello():
    return 'Hello, World!'

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
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.route('/relevant-info', methods=['POST'])
async def get_relevant_info():
    try:
        request_data = await request.get_json(force=True)
        question = request_data['question']
        relevant_info = operand_search_relevant_info(question)
        return quart.Response(response=json.dumps({'status': 'success', 'relevant_info': relevant_info}), status=200)
    except Exception as e:
        print(str(e))
        return quart.Response(response=json.dumps({'status': 'error', 'message': str(e)}), status=400)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
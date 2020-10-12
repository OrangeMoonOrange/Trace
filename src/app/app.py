from flask import Flask
from src.kde import pipeline
from concurrent.futures import ThreadPoolExecutor
from flask import request
executor = ThreadPoolExecutor(1)

app = Flask(__name__)

@app.route('/v1/')
def genroadnet():
    start = request.args.get("start")
    end = request.args.get("end")
    executor.submit(pipeline.runUpdateData2Map,start,end)
    return 'Function is running is backend.'

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
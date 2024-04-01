import platform
import psutil
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/",methods=['GET'])
def system_info():
    system_info = {
            'hostname':platform.node(),
            'os':platform.system(),
            'memory': {
                'total':round(psutil.virtual_memory().total/(1024**3),2),
                'available':round(psutil.virtual_memory().available/(1024**3),2)},
            'disk':{
                'total':round(psutil.disk_usage('/').total/(1024**3),2),
                'available':round(psutil.disk_usage('/').free/(1024**3),2)}
            }
    return jsonify(system_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0")

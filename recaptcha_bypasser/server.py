import requests
import json
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/token")
def token():
    token = request.args["captcha"]
    return jsonify({"token": token})
    # tilesIds = [60512168067021]
    # query = 'mutation { buyNewLandfield( captcha: "' + token + '", tiles: ' + str(tilesIds) + ', center: "7.367535, 45.717207", description: "Pollein", location: "Pollein, Aosta Valley, Italy", promoCodeId: "undefined" ) { landfield { id, thumbnail, description, location, forSale, price, center, tileIndexes, owner { username }, transactionSet { price, timeStr, previousOwner { username, } owner { username, } } } } }'
    # response = _exec(query)  
    # return jsonify(response)

if __name__ == "__main__":
    # e = Earth()
    # s = requests.Session()

    # with open("./cookies.json", 'r') as jsonCookies:
    #     loggedCookies = json.load(jsonCookies)
    #     s.cookies.set(**loggedCookies)
    app.run(debug=True)
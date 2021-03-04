from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return 'Hello World!'

@app.route("/<dave>")
def generateResponse(dave):
    # if dave.isupper():
    #     return("Welcome, " + dave.lower() + ", to my CSCB20 website")
    # elif dave.islower():
    #     return("Welcome, " + dave.upper() + ", to my CSCB20 website")
    # else:
    #     return "Go fuck yourself"
    return dave

if __name__ == "__main__":
    app.run(debug=True)
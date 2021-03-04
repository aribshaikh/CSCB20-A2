from flask import Flask

app = Flask(__name__)

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

@app.route("/")
def home():
    return "Hello World"

@app.route("/<dave>")
def generateResponse(dave):
    if dave.islower() and not hasNumbers(dave):
        return("Welcome, " + dave.upper() + ", to my CSCB20 website") 
    elif dave.isupper() and not hasNumbers(dave):
        return("Welcome, " + dave.lower() + ", to my CSCB20 website") 
    else:
        result = ""
        for i in dave:
            if not i.isnumeric():
                result += i
    return ("Welcome, " + result + ", to my CSCB20 website") 

if __name__ == "__main__":
    app.run()

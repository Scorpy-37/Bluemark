# Imports

import subprocess
import webbrowser
import traceback
import datetime
import requests
import tempfile
import pathlib
import json
import time
import sys
import re
import os



# Base functions

def getLocalFile(filename):
    return os.path.join(pathlib.Path(__file__).parent.resolve(), filename)

def toURI(file):
    return pathlib.Path(file).resolve().as_uri()

def filter(input_string):
    pattern = r'[^A-Za-z0-9]'
    filtered_string = re.sub(pattern, '', input_string)
    return filtered_string

def getColor(color):
    color = color.lower()
    colorCode = "\033[0m"
    if color == "reset" or color == -1:
        colorCode = '\033[0m'
    elif color == "header" or color == 0:
        colorCode = '\033[95m'
    elif color == "okblue" or color == 1:
        colorCode = '\033[94m'
    elif color == "okcyan" or color == 2:
        colorCode = '\033[96m'
    elif color == "okgreen" or color == 3:
        colorCode = '\033[92m'
    elif color == "warning" or color == 4:
        colorCode = '\033[93m'
    elif color == "fail" or color == 5:
        colorCode = '\033[91m'
    elif color == "bold" or color == 6:
        colorCode = '\033[1m'
    elif color == "underline" or color == 7:
        colorCode = '\033[4m'
    return colorCode

def setColor(color):
    print(getColor(color))

def resetColor():
    print('\033[0m')



# LLM functions

def inferLLM(user, system="", model="local-model"):
    chat = []
    if system != "":
        chat.append({"role": "system", "content": system})
    chat.append({"role": "user", "content": user})

    payload = {
        "model": model,
        "messages": chat,
        "max_tokens": config["max_tokens"]
    }
    
    if not config.get("thinking", True):
        payload["reasoning_effort"] = "none"
        payload["enable_thinking"] = False

    response = requests.post(config["address"], json=payload)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]



# Base variables

config = json.loads(open(getLocalFile("config.json")).read())



# Runtime

def run_evaluation():
    for f in os.listdir(getLocalFile("results")):
        file = json.loads(open(getLocalFile("results/"+f), encoding="UTF-8").read())
        
        start = datetime.datetime.now()
        model = file["model"]
        data = file["answers"]

        results = {
            "model": model,
            "scores": []
        }

        def writeEvaluation():
            open(getLocalFile("evaluations/"+str(start).replace(':', '-')+".json"), 'w').write(json.dumps(results, indent=4))

        q = -1
        for entry in data:
            q += 1
            
            question = entry["question"]
            response = entry["response"]
            answer = config["questions"][q][1]
            length = round(entry["end"] - entry["start"])

            if question.startswith("{file:"):
                f = question[6:-1]
                c = open(getLocalFile(f), encoding="utf-8").read()
                question = c

            if answer.startswith("{file:"):
                f = answer[6:-1]
                c = open(getLocalFile(f), encoding="utf-8").read()
                answer = c



            print("="*5 + " Evaluating model "+model+", question "+str(q+1)+" " + "="*5)

            setColor("okblue")
            print("Question:")
            print(question)

            setColor("warning")
            print("Response:")
            print(response)

            setColor("okgreen")
            print("Answer:")
            print(answer)

            resetColor()
            
            
            
            score = ""
            while score == "":
                score = input("Score > ")

                if score.startswith("/"):
                    try:
                        ns = {
                            "question": question,
                            "response": response,
                            "answer": answer,
                            "config": config
                        }
                        exec(open(getLocalFile("scripts/" + score[1:] + ".py"), encoding="utf-8").read(), ns)
                    except:
                        setColor("fail")
                        print("Error occured while running command:\n\n" + traceback.format_exc())
                        resetColor()
                    score = ""



            results["scores"].append({})
            
            results["scores"][q]["ttc"] = length
            results["scores"][q]["dnf"] = entry["dnf"]
            
            try:
                results["scores"][q]["score"] = float(score)
            except:
                results["scores"][q]["score"] = score



            writeEvaluation()

try:
    run_evaluation()
    input("All evaluations completed, press ENTER to exit")
except Exception as e:
    setColor("fail")
    print("An uncaught error occurred during runtime!")
    traceback.print_exc()
    resetColor()
    input("Press ENTER to exit")
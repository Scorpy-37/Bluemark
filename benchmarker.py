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

def toUri(file):
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
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"]
    }
    
    if not config.get("thinking", True):
        payload["reasoning_effort"] = "none"
        payload["enable_thinking"] = False

    response = requests.post(config["address"], json=payload)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]



# Runtime functions

def format_time(value):
    days = int(value // 86400)
    hours = int(value % 86400 // 3600)
    minutes = int(value % 3600 // 60)
    seconds = int(value % 60)

    return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

def get_avg_resp_time(response_times):
    if len(response_times) <= 0:
        return 0
    return sum(response_times) / len(response_times)

def get_elapsed_time(started):
    return format_time(time.time() - started)

def get_estimated_time(remaining, response_times):
    resp_time = get_avg_resp_time(response_times)
    if (resp_time == 0):
        return "?"

    return format_time(remaining * resp_time)



# Base variables

config = json.loads(open(getLocalFile("config.json")).read())



# Runtime

def run_benchmarks():
    # Load info    
    models = config["models"]
    system_prompt = config["system_prompt"]
    questions = config["questions"]

    # Print info and wait for confirmation
    print("Models: "+str(len(models)))
    print("Questions: "+str(len(questions)))
    remaining = len(models) * len(questions)
    
    proceed = input("\nAre you sure you want to proceed? (y)\n> ")
    if str(proceed).strip().lower() != "y":
        return
    
    # Test loop
    response_times = []
    tests_started = time.time()

    for m in range(len(models)):
        model = models[m]

        info = {
            "model": model,
            "benchmarking_start": time.time(),
            "benchmarking_end": -1,
            "answers": []
        }

        for q in range(len(questions)):
            question = questions[q][0]

            if question.startswith("{file:"):
                f = question[6:-1]
                c = open(getLocalFile(f), encoding="utf-8").read()
                question = c

            info["answers"].append({
                "question": question,
                "response": "",
                "dnf": False,
                "start": time.time(),
                "end": -1
            })

            os.system("cls")

            print("Model "+str(model))
            print("Question "+str(q+1))
            print("\n" + '-' * 20 + "\n")
            setColor("warning")
            print('"' + question + '"')
            resetColor()
            print("\n" + '-' * 20 + "\n")
            print("Time taken: " + str( get_elapsed_time(tests_started)) )
            print("Time left: " + str( get_estimated_time(remaining, response_times)) )
            print("Questions left: " + str(remaining))

            try:
                info["answers"][q]["response"] = inferLLM(question, system_prompt, model)
            except Exception as e:
                setColor("fail")
                print(str(e))
                resetColor()
                
            if len(info["answers"][q]["response"].strip()) == 0:
                info["answers"][q]["dnf"] = True
            
            info["answers"][q]["end"] = time.time()
            response_times.append(info["answers"][q]["end"] - info["answers"][q]["start"])

            remaining -= 1
            time.sleep(1)

        info["benchmarking_end"] = time.time()

        open(getLocalFile("results/"+filter(model)+".json"), 'w', encoding="UTF-8").write(json.dumps(info))
        time.sleep(1)

try:
    run_benchmarks()
    input("All benchmarks completed, press ENTER to exit")
except Exception as e:
    setColor("fail")
    print("An uncaught error occurred during runtime!")
    traceback.print_exc()
    resetColor()
    input("Press ENTER to exit")
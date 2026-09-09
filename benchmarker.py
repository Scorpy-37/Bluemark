try:
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
    
    scriptPath = pathlib.Path(__file__).parent.resolve()
    def getLocalFile(filename):
        return os.path.join(scriptPath, filename)

    def toUri(file):
        return pathlib.Path(file).resolve().as_uri()

    max_tokens = 4096
    def inferLLM(user, system="", model="local-model"):
        url = open(getLocalFile("address.ip"), 'r').read() + "chat/completions"

        chat = []
        if system != "":
            chat.append({"role": "system", "content": system})
        chat.append({"role": "user", "content": user})

        payload = {
            "model": model,
            "messages": chat,
            "max_tokens": max_tokens
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

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

    models = open(getLocalFile("models.txt")).read().strip().split("\n")
    systemprompt = open(getLocalFile("systemprompt.txt")).read().strip()
    rounds = int(open(getLocalFile("rounds.txt")).read().strip())
    questions = []

    for question_file in os.listdir("questions"):
        question = open(getLocalFile("questions/"+question_file), encoding="UTF-8").read()
        questions.append(question)

    print("Models: "+str(len(models)))
    print("Questions: "+str(len(questions)))
    print("Rounds: "+str(rounds))

    left = len(models) * len(questions) * rounds
    print("Total inferences: "+str(left))

    proceed = input("\nAre you sure you want to proceed? (y)\n> ")

    if str(proceed).strip().lower() == "y":
        response_times = []
        started = time.time()

        def get_avg_resp_time():
            if len(response_times) <= 0:
                return 0
            return sum(response_times) / len(response_times)
        def get_elapsed_time():
            value = time.time() - started

            days = int(value // 86400)
            hours = int(value % 86400 // 3600)
            minutes = int(value % 3600 // 60)
            seconds = int(value % 60)

            return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
        def get_estimated_time(remaining):
            resp_time = get_avg_resp_time()
            if (resp_time == 0):
                return "?"

            value = remaining * resp_time

            days = int(value // 86400)
            hours = int(value % 86400 // 3600)
            minutes = int(value % 3600 // 60)
            seconds = int(value % 60)

            return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

        for m in range(len(models)):
            model = models[m]

            info = {
                "model": model,
                "benchmarking_start": time.time(),
                "benchmarking_end": 0,
                "answers": {}
            }

            for r in range(rounds):
                rid = "round"+str(r+1)
                info["answers"][rid] = {}
                for q in range(len(questions)):
                    question = questions[q]

                    info["answers"][rid][q] = {
                        "question": question,
                        "response": "NONE",
                        "start": time.time(),
                        "end": 0
                    }

                    os.system("cls")

                    print("Model "+str(model))
                    print("Round "+str(r+1))
                    print("Question "+str(q+1))
                    print("")
                    print("Elapsed time: "+str(get_elapsed_time()))
                    print("Questions left: "+str(left))
                    print("Estimated time left: "+str(get_estimated_time(left)))
                    print("")
                    print(question)

                    response = "FAILED"
                    try:
                        sp = systemprompt
                        if q+1 >= 16:
                            sp = ""
                        response = inferLLM(question, sp, model)
                    except Exception as e:
                        print(str(e))

                    info["answers"][rid][q]["response"] = str(response)
                    info["answers"][rid][q]["end"] = time.time()

                    response_times.append(info["answers"][rid][q]["end"] - info["answers"][rid][q]["start"])

                    left -= 1
                    time.sleep(1)

            info["benchmarking_end"] = time.time()

            open(getLocalFile("results/"+filter(model)+".json"), 'w', encoding="UTF-8").write(json.dumps(info))
            time.sleep(10)
    input("Done! Press ENTER to exit.")
except Exception as e:
    print("An uncaught error occured during runtime!")
    traceback.print_exc()
    input("Press ENTER to exit.")
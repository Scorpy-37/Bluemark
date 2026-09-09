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

    def toURI(file):
        return pathlib.Path(file).resolve().as_uri()

    def inferLLM(user, system="", model="local-model"):
        url = open(getLocalFile("address.ip"), 'r').read() + "chat/completions"

        chat = []
        if system != "":
            chat.append({"role": "system", "content": system})
        chat.append({"role": "user", "content": user})

        payload = {
            "model": model,
            "messages": chat
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def filter(input_string):
        pattern = r'[^A-Za-z0-9]'
        filtered_string = re.sub(pattern, '', input_string)
        return filtered_string
    
    def getCodeBlock(response):
        rspl = response.split("\n")
        
        lined = ""
        for i in range(len(rspl)):
            lined += str(i+1) + " | " + rspl[i] + "\n"
        
        resp = inferLLM(lined, """
You are a highly precise and accurate coding assistant.
Your job is simple: look at the given script and say the code start line and code end line.
Do NOT say anything else. Your message must be just two numbers seperated by a space with NO formatting.
If there are multiple code blocks prefer the most complete one.
IMPORTANT: For HTML code always mark **THE ENTIRE HTML BLOCK**, not just the <script> part.
            """)
        resp = resp.strip().replace("\"","").replace("'","").replace("\n", " ").replace("  ", " ")
        
        stl = -1
        enl = -1
        try:
            stl = int(resp.split(" ")[0])
            enl = int(resp.split(" ")[1])
        except Exception:
            pass

        code = ""
        if stl != -1 and enl != -1:
            for i in range(len(rspl)):
                if stl <= i and enl >= i:
                    code += rspl[i] + "\n"

        code = code.strip()
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        return code

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

    def runAsPython(response):
        try:
            code = response.split("```python")[-1].split("```")[0]

            with tempfile.TemporaryFile(mode="w+b") as err:
                p = subprocess.Popen(
                    [sys.executable, "-c", code],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stderr=err,
                )

                p.wait()

                err.seek(0)
                errors = err.read().decode(errors="replace")

            if len(errors) > 0:
                setColor("fail")
                print("Script threw errors:")
                print(errors)
                resetColor()
        except Exception as e:
            setColor("fail")
            print("Error:")
            print(str(e))
            resetColor()

    def runAsHTML(response):
        try:
            code = response.split("```html")[-1].split("```")[0]

            htmlfile = getLocalFile("test/test.html")
            open(htmlfile, 'w', encoding="UTF-8").write(code)
            webbrowser.open(toURI(htmlfile))
        except Exception as e:
            setColor("fail")
            print("Error:")
            print(str(e))
            resetColor()

    def checkCounting(response):
        txt = getColor("warning")
        num = 1
        for word in response.strip().split(" "):
            if word == str(num):
                txt += word
                num += 1
            elif num > 1:
                txt += getColor("fail") + num
                num += 1
        txt += getColor("reset")
        return txt

    def runAs2D(response):
        boxes = []
        for b in response.lower().split("box("):
            try:
                boxtxt = b.split(")")[0]
                coords = boxtxt.split(",")
                comp = []
                for c in range(len(coords)):
                    coord = float(coords[c].strip())
                    comp.append(coord)

                boxes.append((comp[0], comp[1], comp[2], comp[3]))
            except:
                pass

        open(getLocalFile("data/2d_boxes.txt"), 'w', encoding="UTF-8").write(str(boxes))

        with tempfile.TemporaryFile(mode="w+b") as err:
            p = subprocess.Popen(
                [sys.executable, "-c", open(getLocalFile("scripts/visualize_2d.py"), encoding="UTF-8").read()],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stderr=err,
            )

            p.wait()

            err.seek(0)
            errors = err.read().decode(errors="replace")

        if len(errors) > 0:
            setColor("fail")
            print("Script threw errors:")
            print(errors)
            resetColor()

    def runAs3D(response):
        boxes = []
        for b in response.lower().split("box("):
            try:
                boxtxt = b.split(")")[0]
                coords = boxtxt.split(",")
                comp = []
                for c in range(len(coords)):
                    coord = float(coords[c].strip())
                    comp.append(coord)
                boxes.append((comp[0], comp[1], comp[2], comp[3], comp[4], comp[5]))
            except:
                pass

        open(getLocalFile("data/3d_boxes.txt"), 'w', encoding="UTF-8").write(str(boxes))

        with tempfile.TemporaryFile(mode="w+b") as err:
            p = subprocess.Popen(
                [sys.executable, "-c", open(getLocalFile("scripts/visualize_3d.py"), encoding="UTF-8").read()],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stderr=err,
            )

            p.wait()

            err.seek(0)
            errors = err.read().decode(errors="replace")

        if len(errors) > 0:
            setColor("fail")
            print("Script threw errors:")
            print(errors)
            resetColor()


    answers = open(getLocalFile("answers.txt"), encoding="UTF-8").read().strip().split("\n")
    for f in os.listdir(getLocalFile("results")):
        file = json.loads(open(getLocalFile("results/"+f), encoding="UTF-8").read())
        start = datetime.datetime.now()

        model = file["model"]
        data = file["answers"]

        results = {
            "model": model,
            "questions": {}
        }

        def writeEvaluation():
            open(getLocalFile("evaluations/"+str(start).replace(':', '-')+".json"), 'w').write(json.dumps(results, indent=4))

        for a in data["round1"]:
            for r in data:
                entry = data[r][a]
                question = entry["question"]
                response = entry["response"]
                answer = answers[int(a)]
                length = round(entry["end"] - entry["start"])

                rname = r
                qname = "q"+str(int(a)+1)
                print("="*5 + " Evaluating "+model+", question "+str(int(a)+1)+" "+str(rname) + " " + "="*5)

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

                    if score.strip().lower() == "/python":
                        score = ""
                        runAsPython(response)
                    if score.strip().lower() == "/html":
                        score = ""
                        runAsHTML(response)
                    if score.strip().lower() == "/count":
                        score = ""
                        checkCounting(response)
                    if score.strip().lower() == "/2d":
                        score = ""
                        runAs2D(response)
                    if score.strip().lower() == "/3d":
                        score = ""
                        runAs3D(response)

                if rname not in results["questions"]:
                    results["questions"][rname] = {}
                if qname not in results["questions"][rname]:
                    results["questions"][rname][qname] = {}
                results["questions"][rname][qname]["ttc"] = length
                try:
                    results["questions"][rname][qname]["score"] = float(score)
                except:
                    results["questions"][rname][qname]["score"] = score

                writeEvaluation()



    input("Done! Press ENTER to exit.")
except Exception as e:
    print("An uncaught error occured during runtime!")
    traceback.print_exc()
    input("Press ENTER to exit.")
from openai.error import *
import openai
import time

class ChatGPTOracle:
    def __init__(self, SHOW_MESSAGE):
        self.show_message = SHOW_MESSAGE
        # please put the tokens here
        openai.organization = ""
        openai.api_key = ""

    def ask_question(self, description, node):
        if node == 'root':
            return 1, ""
        node = node.split("-")[-1]
        message = description + ". Based on the description above, is it an item in category " + node + "?"
        completion = None
        while True:
            try:
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user",
                         "content": message}
                    ]
                )
                break
            except:
                time.sleep(1)
                continue

        reply = completion.choices[0].message.content
        if self.show_message:
            print("Is it an item in category " + node + "?")
            print(reply)
        flag = 0
        if reply.find("No") >= 0:
            flag = 0
        if reply.find("Yes") >= 0:
            flag = 1

        if flag == 1:
            # return 1
            return 1, "Is it an item in category " + node + "?\n" + reply
        else:
            # return 0
            return 0, "Is it an item in category " + node + "?\n" + reply

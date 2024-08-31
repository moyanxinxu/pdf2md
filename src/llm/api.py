import requests
from hp_api import hp

url = hp.api


def md_text_iter(file_path, batch_size=64):
    with open(file_path, "r") as file:
        lines = len(file.readlines())
        for i in range(0, lines, batch_size):
            yield "".join(file.readlines()[i : i + batch_size])


for data in md_text_iter("../result.md"):
    header = {
        "model": hp.model,
        "messages": [
            {
                "role": "user",
                "content": f"""{hp.prompt}\n{data}""",
            },
        ],
        "stream": hp.stream,
    }

    response = requests.post(url, json=header)

    if response.status_code == 200:
        print(response.json()["message"]["content"])
    else:
        print(f"request failed: {response.status_code}")

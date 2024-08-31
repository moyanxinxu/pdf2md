import requests
from hp_api import hp

url = hp.api


def md_text_iter(file_path, batch_size=64):
    """Iterate over the lines of a file with batch_size."""
    with open(file_path, "r") as file:
        batch = []
        for line in file:
            batch.append(line.strip())
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:  # Yield any remaining lines that didn't fill a full batch
            yield batch


for data in md_text_iter("../result.md"):
    header = {
        "model": hp.model,
        "messages": [
            {
                "role": "user",
                "content": f"""{hp.prompt}\n{' '.join(data)}""",
            },
        ],
        "stream": hp.stream,
    }

    response = requests.post(url, json=header)

    if response.status_code == 200:
        print(response.json()["message"]["content"])
    else:
        print(f"request failed: {response.status_code}")

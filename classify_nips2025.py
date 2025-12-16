import json
from zai import ZhipuAiClient
import copy
from loguru import logger
import os

input_file = 'neurips2025_all_papers.json'
logger.add("nips.log")

def classify_single_paper(paper, client, selected, updated):
    logger.info("classify paper id {}, paper title is {}, paper abstract is {}".format(paper["id"], paper["title"], paper["abstract"]))
    user_request = "Please give me a score, which is a integer between 1 and 10, indicating this paper's relevance about your research interest. The paper's tile is {}, and its abstract is {}. Please give your response in a plain text json object, the object contains 4 keys, the first is 'score', its value is the score; the second is 'Relevant Aspects', the third is 'Irrelevant Aspects' and the last is 'Summary'. Do not use any markdown gramma in your response".format(paper["title"], paper["abstract"])
    # print(user_request)
    response = client.chat.completions.create(
        model='glm-4.6',
        messages=[
            {'role': 'system', 'content': 'You are an experienced expert about machine learning systems, especially focus on large language model\'s training optimization and inference optimization, aiming better gpu ultilization  and scalbility, higher throughput and lower latency.'},
            {'role': 'user', 'content': user_request},
        ],
    )
    response_contet = response.choices[0].message.content
    # print("paper id {}, response: {}".format(paper["id"], response_contet))
    logger.info("classify paper id {}, llm response_contet is {}".format(paper["id"], response_contet))
    response_obj = json.loads(response_contet)
    # print(response_obj)
    paper_cpy = copy.deepcopy(paper)
    paper_cpy['classify'] = response_obj
    updated.append(paper_cpy)
    if response_obj['score'] > 6:
        logger.info("find mlsys paper with id {}".format(paper["id"]))
        paper_selected = copy.deepcopy(paper)
        paper_selected['classify'] = response_obj
        selected.append(paper_selected)

def main():
    data = None
    api_key = os.environ['zai_key']
    client = ZhipuAiClient(api_key=api_key)
    with open(input_file, "r") as f:
        json_content = f.read()
        data = json.loads(json_content)

    output_file = open('output.json', "w+")
    updated_file = open('updated.json', "w+")

    sum = 0
    selected = []
    updated = []
    for paper in data:
        try:
            sum = sum + 1
            print(sum)
            classify_single_paper(paper, client, selected, updated)
        except:
            logger.error("classify paper {} fail".format(paper["id"]))
            continue
    json.dump(updated, updated_file)
    json.dump(selected, output_file)
    print("total number of papers {}".format(sum))

if __name__ == '__main__':
    main()






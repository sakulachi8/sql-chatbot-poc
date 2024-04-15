import os
from typing import List
from uuid import uuid4

import openai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex


from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
import os
os.environ["OPENAI_API_TYPE"] = ""
os.environ["OPENAI_API_VERSION"] = ""
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""
os.environ["AZURE_OPENAI_ENDPOINT"] = ""

import openai

openai.api_type = ""
openai.api_key = ""
openai.api_base = ""
openai.api_version = ""
search_endpoint = ""
search_key = ""
index_name = ""



def get_search_connection(index=index_name):
    credential = AzureKeyCredential(search_key)
    client = SearchClient(endpoint=search_endpoint, index_name=index, credential=credential)
    return client

def search_documents(search_text, index=index_name, skuid="2785BA"):
    client = get_search_connection(index)
    print(client)
    if index == index_name and skuid:
        results = client.search(skuid)
        print(results)
       
    else:
        results = client.search(search_text)
    client.close()
    if index != index_name:
        return list(results)[:20]
   
    summary_dict = {}
    for result in results:
        # Access document values using key names
        order_quantity = result.get('order_quantity')  # Use .get() for safer access
        order_date = result.get('order_date')
        skuid = result.get('skuid')
    # ... add other values you need ...

    # You can build the summary as needed using these values
    summary_dict[result['skuid']] = f"Order quantity: {order_quantity}, Order date: {order_date}, SKU: {skuid}" 
    # get top 5 summary list
    print(f"Summary: {summary_dict}")
    return list(summary_dict.values())[:5]

def request_to_model(input, index=index_name, project_name='Proposal', instructions="Use this data to answer user prompt:"):

    prompt = input.messages[-1].prompt
    skuid= input.messages[-1].skuid
    print(prompt)
    my_context = search_documents(prompt, index, skuid=skuid)
    print(my_context)
    search_content = ''
    for item in my_context:
        search_content += f"```\n {item} \n```"
    post_prompt = "Do not give me any information about procedures and service features that are not mentioned in the PROVIDED CONTEXT."
    # if project_name=='Legal':
    #     chat_history.append({"role": "system", "content": f"{instructions} \n### CONTEXT \n{search_content} \n### END OF CONTEXT\n\n###QUESTION \n {prompt} END OF QUESTION \n"})
    #     prompt = instructions
    # else:
    #     chat_history.append({"role": "system", "content": f"{instructions} \n### CONTEXT \n{search_content} \n### END OF CONTEXT\n"})
    chat_history=[{"role": "user", "content": f"{prompt} \n {my_context}"}]
    response = openai.chat.completions.create(
        messages=chat_history,
        model="gpt35",
        max_tokens=4000,
        temperature=0.1,
        top_p=0.9
    )
    # return my_context
    return response.choices[0].message.content


if __name__ == "__main__":
    credential = AzureKeyCredential(search_key)
    client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    index_list = client.list_indexes()
    # ['langchain-vector-demo', 'legal-custom-index', 'model1-staffing-us-20230826121455-ae3b-index-chunk', 'model1-staffing-us', 'model2-staffing-overseas-index', 'model2-staffing-overseas', 'model3-network-services-index', 'model3-network-services', 'model4-clinic-cboc-index', 'model4-clinic-cboc', 'search-document', 'smc-url-test-index', 'sterling-ai-text-index']
    print([index.name for index in index_list])
    client.close()

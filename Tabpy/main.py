from tabpy.tabpy_tools.client import Client
import chromadb
import numpy as np
tabpy_client = Client('http://localhost:9004/')

def trial(a, b):
    query = a
    stockcode = b
    return [1 if x == 6 else 0 for x in stockcode]
tabpy_client.deploy('trial', trial, override=True)


def vectorsearh(a, b):
    query = a[0]
    stockcode = b
    chroma_client = chromadb.PersistentClient(path='/Users/chengmankitt/Pycharm/Portfolio/ChromaDB')
    feature_collection = chroma_client.get_collection('feature_MVP')
    results = feature_collection.query(query_texts=query, n_results=10, include=['distances', 'documents'])

    items = {}
    for i in range(len(results["ids"][0])):
        id = int(results['ids'][0][i].split('_')[0])
        distance = results['distances'][0][i]
        if id not in items and len(items.keys()) < 5:
            items[id] = distance

    dis_list = []
    for j in range(len(stockcode)):
        if stockcode[j] in items:
            dis_list.append(items[stockcode[j]])
        else:
            dis_list.append(0)
    return dis_list
tabpy_client.deploy('vectorsearh', vectorsearh, override=True)



import chromadb
import os
from openai import OpenAI
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedding_function = SentenceTransformerEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path='/Users/chengmankitt/Pycharm/Portfolio/ChromaDB')
pdf_collection = chroma_client.get_or_create_collection('AR_PDF_MVP', embedding_function=embedding_function)
feature_collection = chroma_client.get_or_create_collection('feature_MVP', embedding_function=embedding_function)
chroma_client.list_collections()
api_key = os.environ["OPENAI_API_KEY"]
llm = OpenAI()


def augment_multiple_query(query, model="gpt-3.5-turbo"):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful expert financial research assistant. Your users are asking questions in an annual report. "
                       "Suggest up to five additional related questions to help them find the information they need, for the provided question. "
                       "Suggest only short questions without compound sentences. Suggest a variety of questions that cover different aspects of the topic."
                       "Make sure they are complete questions, and that they are related to the original question."
                       "Output one question per line. Do not number the questions."
        },
        {"role": "user", "content": query}
    ]

    response = llm.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    content = content.split("\n")
    return content


def rag(query, retrieved_documents, model="gpt-3.5-turbo"):
    information = "\n\n".join(retrieved_documents)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful expert financial research assistant. Your users are asking questions about information contained in an annual report."
                       "You will be shown the user's question, and the relevant information from the annual report. Answer the user's question using only this information."
        },
        {"role": "user", "content": f"Question: {query}. \n Information: {information}"}
    ]

    response = llm.chat.completions.create(
        model=model,
        messages=messages,
    )
    content = response.choices[0].message.content
    return content


directory = "/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP"
pdf_list = sorted(os.listdir(directory))[1::]
code_mvp = [i.split('_')[0] for i in pdf_list]
code_mvp


def pnameRAG(stock_code):
    original_query = ("What are the products or services do they sell, according to the SEGMENT INFORMATION?")
    augmented_queries = [
        "What is the breakdown of revenue by product or service?",
        "How has the product mix evolved over the past few years?",
        "What new products or services have been introduced recently?",
        "Are there any plans to expand the product or service offerings in the future?",
        "How do the company's products or services differ from competitors?",
        "Can you provide information on any new products or services launched during the year?"]
    queries = [original_query] + augmented_queries
    metadata = {'stockcode': {"$eq": stock_code}}
    results = pdf_collection.query(query_texts=queries, n_results=8, include=['documents', 'embeddings'],
                                   where=metadata)
    retrieved_documents = results['documents']
    unique_documents = set()
    for documents in retrieved_documents:
        for document in documents:
            unique_documents.add(document)
    p_query = f'''
    Your tasks is to extract relevant data from the provided texts to do product comparison analysis in annual reports.

    From the information below, delimited by two quotes extract the list of products/services according to the session: Notes in Consolidated Financial Statements. 
    Information: ''{original_query}''

    Please answer only the product/service names and SEPERATE by a comma in python list format.
    '''
    output = rag(query=p_query, retrieved_documents=unique_documents)
    return list(output.split(', '))


def descriptionRAG(product_name):
    d_original_query = f'What is {product_name} and what do they do?'
    d_augmented_queries = [
        f"How do {product_name} contribute to the company's revenue?",
        f"What specific {product_name} does the company offer?",
        f"How are {product_name} differentiated from the company's core products?",
        f"What is the market demand for {product_name} in the industry?",
        f"How does the company ensure the quality and delivery of {product_name} to customers?"
    ]

    queries = [d_original_query] + d_augmented_queries
    results = pdf_collection.query(where=metadatas, query_texts=queries, n_results=5,
                                   include=['documents', 'embeddings'])
    retrieved_documents = results['documents']

    unique_documents = set()
    for documents in retrieved_documents:
        for document in documents:
            unique_documents.add(document)

    query = f'''
    Your task is to generate a short summary of a product of the company to compare and contrast with the product in another company.

    Summarise the text chunks below, delimited by two quotation marks, in 6 sentences,
    and focusing on any aspects that mentioned how business earn money by this product and new initiatives.

    product name: ''{product_name}''
    original_query: ''{d_original_query}''

    '''
    d_output = rag(query=query, retrieved_documents=unique_documents)
    return d_output


for i in range(len(code_mvp)):
    print(code_mvp[i])
    stock_code = code_mvp[i]
    metadatas = {'stockcode': {"$eq": stock_code}}
    output = pnameRAG(code_mvp[i])
    for j in range(len(output)):
        pd_output = descriptionRAG(output[j])
        print(pd_output)
        ids = f'{stock_code}_0{j + 1}'
        input_metadatas = {'stockcode': stock_code}
        feature_collection.add(
            metadatas=input_metadatas,
            ids=ids,
            documents=pd_output
        )
        print(f'finished ids:{ids}')
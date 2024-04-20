from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os
from datetime import datetime
from more_itertools import batched
import uuid

embedding_function = SentenceTransformerEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path='/Users/chengmankitt/Pycharm/Portfolio/ChromaDB')
collection = chroma_client.get_or_create_collection("AR_PDF_MVP", embedding_function=embedding_function)


directory = "/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP"
pdf_list = sorted(os.listdir(directory))[1::]

def PDFinject(filename):
    reader = PdfReader(f'/Users/chengmankitt/Pycharm/Portfolio/Doc_AR_pdf_MVP/{filename}')
    pdf_texts = [p.extract_text().strip() for p in reader.pages]
    pdf_texts = [text for text in pdf_texts if text]

    character_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=0,
        separators=["\n\n", "\n", "(?<=\. )", " ", ""]
    )

    character_split_texts = character_splitter.split_text('\n\n'.join(pdf_texts))
    token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)

    token_split_texts = []
    for text in character_split_texts:
        token_split_texts += token_splitter.split_text(text)
    return token_split_texts

def addtochroma(token_split_texts, filename):
    ids = [str(uuid.uuid4()) for _ in range(len(token_split_texts))]
    stockcode = filename.split('_')[0]
    metadatas = [{'stockcode': stockcode} for i in range(len(token_split_texts))]
    for batch in batched(range(len(token_split_texts)), 166):
        batch_ids = ids[batch[0]:batch[-1] + 1]
        batch_metadatas = metadatas[batch[0]:batch[-1] + 1]
        batch_documents = token_split_texts[batch[0]:batch[-1] + 1]
        collection.add(
            metadatas=batch_metadatas,
            ids=batch_ids,
            documents=batch_documents
        )


for i in range(len(pdf_list)):
    start = datetime.now()
    token_split_texts = PDFinject(pdf_list[i])
    end = datetime.now()
    print(end-start)
    print(f'Done {pdf_list[i]} PDF injection')
    start = datetime.now()
    addtochroma(token_split_texts, pdf_list[i])
    end = datetime.now()
    print(end-start)
    print(f'Done {pdf_list[i]} Add to chroma')



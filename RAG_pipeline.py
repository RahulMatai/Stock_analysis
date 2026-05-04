import data_fetcher as df
import yfinance as yf
import pprint
import json
import boto3
import json
import config as cfg
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
#from langchain.embeddings import BedrockEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings

ticker = "RELIANCE.NS"
stock = yf.Ticker(ticker)
fundamentals = df.get_fundamentals(stock)
financials_text = df.financials_to_text(stock)
news = df.get_news(stock)


def prepare_text (fundamentals, financials_text, news):
    fundamentals= json.dumps(fundamentals)
    financials_text= json.dumps(financials_text)
    news =  json.dumps(news)
    combined = f"FUNDAMENTALS:\n{fundamentals}\n\nFINANCIALS:\n{financials_text}\n\nNEWS:\n{news}"
    return combined
    
def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(text)
    return texts

#combined = prepare_text(fundamentals, financials_text, news)
#chunks = chunk_text(combined)
#print(f"Total chunks: {len(chunks)}")

def get_embedding(text):
    client = boto3.client("bedrock-runtime",cfg.AWS_REGION)
    model_id = cfg.amazon_titan_id
    input_text = text
    native_req = {"inputText":input_text}
    request = json.dumps(native_req)
    response = client.invoke_model(modelId=model_id, body=request)
    model_response = json.loads(response["body"].read())
    embedding = model_response["embedding"]
    input_token_count = model_response["inputTextTokenCount"]
    return embedding
    
def create_vector_store(chunks):
    embeddings_client = BedrockEmbeddings(
        model_id=cfg.amazon_titan_id, 
        region_name=cfg.AWS_REGION
    )
    vectorstore = FAISS.from_texts(chunks, embeddings_client)
    return vectorstore

#combined = prepare_text(fundamentals, financials_text, news)
#vectorstore = create_vector_store(chunks)
#chunks = chunk_text(combined)
#print(type(vectorstore))
def search_vectorstore(vectorstore,query):
    res = vectorstore.similarity_search(query,k=3)
    return res
    

#combined = prepare_text(fundamentals, financials_text, news)
#chunks = chunk_text(combined)
#vectorstore = create_vector_store(chunks)
#results = search_vectorstore(vectorstore, "Is Reliance making profit?")
#for r in results:
    print(r.page_content)
    print("---")




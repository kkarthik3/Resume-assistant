from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.dataload.pdf_extractor import PDFWithLinksLoader
from dotenv import load_dotenv
from pymongo.operations import SearchIndexModel
import time
from apis.dbconnection import connect_to_mongo
from apis.model import embeddings

load_dotenv()


def get_embeddings(text):
    return embeddings.embed_query(text)

def dataloader():
    loader = PDFWithLinksLoader("https://kkarthik3.github.io/K-Karthikeyan.pdf")
    data = loader.load()
    return data

def chunkandloaddata(data,collection):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    documents = text_splitter.split_documents(data)
    collection.delete_many({})
    docs_to_insert = [{
                    "text": doc.page_content,
                    "embedding": get_embeddings(doc.page_content)
                    } for doc in documents]
    collection.insert_many(docs_to_insert)


def create_index(client,collection):
    index_name="vector_index"
    existing_indexes = list(collection.list_search_indexes(index_name))
    print("Existing indexes: ",existing_indexes)

    if existing_indexes:
        print(f"Index '{index_name}' already exists. Deleting it.")
        collection.drop_search_index(index_name)
        while True:
            indices = list(collection.list_search_indexes(index_name))
            print(indices)
            if not indices:
                break
            time.sleep(2.5)


    search_index_model = SearchIndexModel(
    definition = {
        "fields": [
        {
            "type": "vector",
            "numDimensions": 768,
            "path": "embedding",
            "similarity": "cosine"
        }
        ]
    },
    name = index_name,
    type = "vectorSearch"
    )

    collection.create_search_index(model=search_index_model)

    print("Polling to check if the index is ready. This may take up to a minute.")
    predicate=None
    if predicate is None:
        predicate = lambda index: index.get("queryable") is True
    while True:
        indices = list(collection.list_search_indexes(index_name))
        if len(indices) and predicate(indices[0]):
            break
        time.sleep(5)
    print(index_name + " is ready for querying.")


def main():
    client, collection = connect_to_mongo()
    chunkandloaddata(dataloader(),collection)
    create_index(client,collection)
    

if __name__ == "__main__":
    main()
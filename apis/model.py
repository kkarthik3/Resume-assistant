from langchain_groq import ChatGroq
from langchain_aws import ChatBedrock
from langchain_huggingface import HuggingFaceEmbeddings
import os
import boto3



# bedrock = boto3.client(
#     "bedrock",
#     region_name="us-east-1",
#     aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#     aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
# )

# model =ChatBedrock(
#     model_id="anthropic.claude-3-sonnet-20240229-v1:0",
#     model_kwargs=dict(temperature=0),client=bedrock
# )

model = ChatGroq(model="llama-3.1-70b-versatile",temperature=0)


#embeddings
embedding_model_name = 'jinaai/jina-embeddings-v2-base-en'
embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs={'device': 'cpu'})
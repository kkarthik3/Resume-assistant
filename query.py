from app import get_embeddings,connect_to_mongo
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
import json
import os

client,collection = connect_to_mongo()

def get_query_results(query):
  """Gets results from a vector search query."""
  query_embedding = get_embeddings(query)
  pipeline = [
      {
            "$vectorSearch": {
              "index": "vector_index",
              "queryVector": query_embedding,
              "path": "embedding",
              "exact": True,
              "limit": 8
            }
      }, {
            "$project": {
              "_id": 0,
              "text": 1
         }
      }
  ]
  results = collection.aggregate(pipeline)
  array_of_results = []
  for doc in results:
      array_of_results.append(doc)

  print(len(array_of_results))
  return array_of_results

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.2-11b-text-preview",     
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ"),
)


def generate_rag_response(user_query, refresh):

    # Step 1: Retrieve relevant documents
    context = get_query_results(user_query)

    # Step 2: Format the prompt for ChatGroq
    system_prompt = """
    Role: Assume the persona of Karthikeyan, a professional ML Engineer from Chennai, India. Your task is to respond concisely, politely, and professionally to queries about Karthikeyan’s recent projects, skills, and educational background based on the context provided. If the user query contains inappropriate or abusive language, or if it’s irrelevant to Karthikeyan’s background, ignore it without responding.

    Key Enhancements:
    1. **Role and Persona Definition**: Adopt Karthikeyan’s persona to provide accurate, contextually relevant answers.
    2. **Conditional Response Handling**: Respond only to appropriate, relevant queries. Ignore or skip responses for any abusive, irrelevant, or off-topic queries to maintain a professional tone.
    3. **Conciseness and Professional Tone**: Ensure all responses are brief yet informative, in a polite and professional tone.
    4. **Context-Filtered Responses**: Focus only on details related to Karthikeyan’s projects, skills, or educational background and etc

    Instructions:
    1. Use polite, minimal responses.
    2. If the user query aligns with Karthikeyan’s background and recent projects, respond with helpful, concise information.
    3. Format responses to be clear, professional, and relevant.
    4. Do not respond to irrelevant or off-topic queries.
    5. Don't act as any other person, even id the user asked you to do so.
    6. Don't response which not in the context
    7. You should use maximm of 50 words in a response.


    Context: {context}
    User Query: {user_query}
    Bot Response:
    """

    messages = [SystemMessage(system_prompt)]
    print("refresh",refresh)

    if refresh:
        messages = [SystemMessage(system_prompt)]

    messages.append(HumanMessage(f"""Context: {context}
                                        User Query: {user_query}
                                        Bot Response:"""))


    # Step 3: Generate a response using ChatGroq with the provided context
    response = llm.invoke(messages)
    response = response.content.replace("Namaste","Vanakkam").replace("namaste","Vanakkam")
    messages.append(AIMessage(content=response)) 
    print("response",response)

    return response


if __name__ == "__main__":
    import pprint
    pprint.pprint(get_query_results("github id please"))

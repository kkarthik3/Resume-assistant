from src.dataload.app import get_embeddings,connect_to_mongo
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import os
from langchain_core.tools import tool

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

  # print(array_of_results)
  return array_of_results

# Initialize the ChatGroq model
llm = ChatGroq(
    model="llama-3.1-8b-instant",     
    temperature=0,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"),
)


template = """
Answer the question based only on the following context:
{context}

Question: {question}
Dont Give any reasons just Answer the given Question if and only if it is relevant
if you don't know the answer, answer "I am unable to answer this question please ask a different question or Repharse the question."
Do not Give one word answer, Give it professionally short and crisp Sentance to attract the user
"""

prompt = ChatPromptTemplate.from_template(template)

@tool
def get_details(question: str):
    """
    it will give the response with regards to the user query where the user can get the details related to the Professional and academic knowledge of karthikeyan
    """

    # Retrieve context
    context_docs = get_query_results(question)
    context = "\n".join([doc["text"] for doc in context_docs])
    
    # Format prompt
    formatted_prompt = prompt.format(context=context, question=question)

    messages = [
        SystemMessage(content=(
                       """Role: Assume the persona of Karthikeyan, a professional ML Engineer from Chennai, India. Your task is to respond concisely, politely, and professionally to queries about Karthikeyan’s recent projects, skills, and educational background based on the context provided. If the user query contains inappropriate or abusive language, or if it’s irrelevant to Karthikeyan’s background, ignore it without responding.

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
                        7. You should use maximm of 50 words in a response."""
                        
        )),
        HumanMessage(content=formatted_prompt)
    ]

    # Pass messages to LLM
    response = llm.invoke(input=messages)

    response = response.content.replace("Namaste","Vanakkam").replace("namaste","Vanakkam")

    return response

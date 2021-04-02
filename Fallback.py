from typing import Optional
from fastapi import FastAPI
import json
from transformers import AutoTokenizer, pipeline, AutoModelForQuestionAnswering
import pymongo
from pymongo import MongoClient
from pydantic import BaseModel

#MongoDB setup
client = pymongo.MongoClient("mongodb://admin:Allegra2021@cluster0-shard-00-00.0vn9n.mongodb.net:27017,cluster0-shard-00-01.0vn9n.mongodb.net:27017,cluster0-shard-00-02.0vn9n.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-3p5mf2-shard-0&authSource=admin&retryWrites=true&w=majority")

#KB Search collection
db = client["KnowledgeBase"]
collection = db["KB1"]

#FAQ Search Collection
db1 = client["FAQ"]
collectionFAQ = db1["FAQ1"]

#Choose the pretrained model that you're using
nlp = pipeline("question-answering")
tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")


class Query(BaseModel):
    question: str
    subject: str
    
app = FastAPI()

@app.post("/")
def Search(query: Query):
    KBList = []
    Results = {}
    MongoSearchKB = collection.find({"subject": query.subject}) #Search the database for the content
    MongoSearchFAQ = collectionFAQ.find({"$text": {"$search": query.question}}) #Search the database for the content
    for x in MongoSearchKB: #Loop through the content and have the Transformer analyse
        S1 = nlp(question=query.question, context=x['content'])
        Dict = {}
        Dict["Answer"] = (S1['answer'])
        Dict["Score"] = (S1['score'])
        Dict["Page"] = (x['pageNumber'])
        Dict["Link"] = (x['DocumentLocation'])
        Dict["Passage"] = (x['content'])
        Dict["Location"] = (x['location'])
        KBList.append(Dict)
    KBList = sorted(KBList, key=lambda k: k['Score'], reverse=True) # Sort items by their score
    Results["Answers"] = KBList[:1] #Turn into JSON for Watson Assistant only returning top 3
    # FAQ Search
    FAQList = [{"Score": 0, "Answer": ""}] #Populate a blank answer so that something is always returned. (Easier for IBM Watson to work through)
    for y in MongoSearchFAQ: #Loop through the FAQ content and have the Transformer analyse
        S2 = nlp(question=y['KBQuestion'], context=query.question)
        Dict = {}
        Dict["Answer"] = (y['answer'])
        Dict["Score"] = (S2['score'])
        FAQList.append(Dict)
    FAQList = sorted(FAQList, key=lambda k: k['Score'], reverse=True) # Sort items by their score
    Results["FAQs"] = FAQList[:1] #Turn into JSON for Watson Assistant only returning top 1
    Results["Payload"] = [{"Question": query.question, "Subject": query.subject}]
    return Results
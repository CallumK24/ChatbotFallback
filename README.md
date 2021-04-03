## Setup

create a virtual environment

Download the repository 

```
git clone https://github.com/CallumK24/ChatbotFallback.git
```

```jsx
pip install -r requirements.txt
```

Sign up to Mongo Atlas (Optional)

[https://www.mongodb.com/](https://www.mongodb.com/) 

If you are using Mongo you will need to replace FAQ and KB as your collections if you don't name yours that. Don't forget to whitelist your IP address otherwise you will constantly receive a timeout message

To run the code type 

```jsx
uvicorn FileName:app —reload
```

To make your endpoint accesible to an external application you will need Ngrok. Once signed up you will need to paste the URL into Watson.

[https://ngrok.com/](https://ngrok.com/) 

Ensure that Ngrok is pointing to the same port as your uvicorn instance by adding http 8000 to your ./ngrok command

Question and Answering models provided by HuggingFace 

[https://huggingface.co/](https://huggingface.co/)

## **Use case**

Being able to have a fall back for when you don’t have prebuilt content is always preferable to just falling back to “I don’t know please ask again” knowledge base integrations are increasingly common when bundled with your SaaS Chatbot provider.

It's surprisngly simple to create a fall back for Watson using HuggingFace transformers, FastAPI and MongoDB in just 60 lines of code you’re able to return a message back to Watson with a potential answer to the question. A lot of the models available on HuggingFace are great at general open domain Question Answering but when it comes to something that’s closed domain such as IT service management you’re not going to always reliably get the answers you want without retraining the model but it's accurate enough to start to play around with. 

Watson makes a call to our FastAPI endpoint. FastAPI connects to MongoDB and pulls potential answers. HuggingFace ranks those answers from the KnowledgeBase and then returns a dictionary of the top 3 ranking results, once done we use the MongoDB index to search to try and find an FAQ to return and passes the answers back to Watson. With Watson choosing to use the hghest scoring result.

The two use cases are simple but distinct:

1) You don't have an intent that you're confidently able to provide an answer as a user and so will search the entire database for an answer. - This is an idea that doesn't scale well over hundreds of documents as hundreds of documents are going to be analysed. We can however align our database to keywords that we have as entities within 

2) You have an intent but none of your answers have been triggered by their entities. In this instance you can filter by align to your intent to shorten down the data to work through.

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/a143dfbc-ff71-4fb3-8fe2-4a5362de4293/Screenshot_2021-03-18_at_15.01.23.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/a143dfbc-ff71-4fb3-8fe2-4a5362de4293/Screenshot_2021-03-18_at_15.01.23.png)

**For KnowledgeBase answers:**

- In my MongoDB database I’m storing a few things:
- The link to the where the information is located,
- the page number if there's more than one.
- The passage that I want to have HF analyse.

I’m returning more than just the answer and the score to Watson as I want to write a response that’s a bit more interactive feeling to an end user I want them to understand a bit more about why I’ve returned the answer that I have. Primarily because sometimes the answer isn’t right and I want it to be obvious that something is wrong but also to help users understand why they have received the answer they have. I am only attempting this fall back search to try and brute force a good answer but I've already not been succesful in my Virtual Assistant. 

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/0ebb6560-537d-49e6-95ba-2391b22217ae/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/0ebb6560-537d-49e6-95ba-2391b22217ae/Untitled.png)

**For FAQ answers:**

These are usually stored in pretty standard question and answer pairs so why do anything different?

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/69061d08-37e5-4073-8ec0-b80f3d568bd3/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/69061d08-37e5-4073-8ec0-b80f3d568bd3/Untitled.png)

**MongoDB setup**

I've used MongoDB as it's a fairly simple and easy way to scale and add answer but there's nothing stopping you from implementing a simpe dictionary directly in the Python code if you want to remove this step. 

Setup is relatively simple, using Pymongo to connect to the database and do a search you can connect your instance in Mongo DB Atlas and get the code specific to your database as you follow the setup through. 

Ngrok setup. 

To enable Watson to connect with the code running locally on your computer you're going to need to use Ngrok to connect. The setup is really easy just make sure that your port is pointing to the same as 

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/1424a06e-7afc-42fb-9d75-7097818df1b6/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/1424a06e-7afc-42fb-9d75-7097818df1b6/Untitled.png)

**In Watson**

I've chosen to use Watson as it's what I'm most familiar with. I set the keys and values I want to send. I'm setting the subject as a context here but you can either select it as an entity or an intent using @Entity or intents[0].intent

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/c21b25c6-88a4-43f5-883e-1860207b4ec1/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/c21b25c6-88a4-43f5-883e-1860207b4ec1/Untitled.png)

Then configuring responses I check to see if the generated HF Transformer score is higher than the FAQ score and that the Answer score is higher than 35%

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ab295a05-ba53-44e7-95ab-475cf04e0ccf/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ab295a05-ba53-44e7-95ab-475cf04e0ccf/Untitled.png)

If not then that means FAQ is the higher scoring of the two and we move on to provide that answer if that score is also above 35%

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e83183ec-5751-4750-8f43-148e5c7c84c7/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e83183ec-5751-4750-8f43-148e5c7c84c7/Untitled.png)

If none of those conditions are satisfied then we fall back to the standard

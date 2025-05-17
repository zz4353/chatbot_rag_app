<div align="center">
        <h1>VNU-RAG-Chatbot</h1>
            <p>An AI-powered Q&A Chatbot about Vietnam National University</p>
            <p>
            <a href="https://github.com/zz4353/chatbot_rag_app/graphs/contributors">
                <img src="https://img.shields.io/github/contributors/zz4353/chatbot_rag_app" alt="Contributors" />
            </a>
            <a href="">
                <img src="https://img.shields.io/github/last-commit/zz4353/chatbot_rag_app" alt="last update" />
            <a href="https://github.com/zz4353/chatbot_rag_app/network/members">
		        <img src="https://img.shields.io/github/forks/zz4353/chatbot_rag_app" alt="forks" />
	        </a>
	        <a href="https://github.com/zz4353/chatbot_rag_app/stargazers">
		        <img src="https://img.shields.io/github/stars/zz4353/chatbot_rag_app" alt="stars" />
	        </a>
</div>

# VNU RAG Chatbot App
This is an app that combines Elasticsearch, Langchain and a number of different LLMs (We used openai) to create a chatbot experience with ELSER with Vietnam National University data.

![Screenshot of the sample app](data/example_running.gif)

# Technology used
- Framework: Langchain
- Search engine + database: Elasticsearch
- Frontend:
    - HTML
    - SVG
    - JSON
    - React with TypeScript and JSX
    - TypeScript
    - CSS
    - JavaScript
- Backend:
    - Flask
    - Python

# How to run

## Init
- Copy [env.example](env.example) to `.env` and fill in values noted inside.
- Download all libraries in requirements.txt using ```pip install -r requirements.txt```
- Install Nodejs, yarn: https://nodejs.org/en
- Create an empty folder named `data_json`
- ```cd data``` and run ```python craw_data.py``` to craw data to `data_json` folder
## Run app
- 1: cd frontend
    - npm install -g yarn
    - yarn install
- 2: Run
    - Terminal 1:
        - flask create-index (If you have already run this command, you do not need to run it again)
        - flask run --port=3001
    - Terminal 2:
        - cd frontend
        - yarn start

- The app will be available at https://localhost:3001
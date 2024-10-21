### read demo errors file
### prompt  update: add json output
### combine promt with file to prepare a query
### ask gpt with result query - it should return exception type + suggest changes

### фокус 1
### подконнектить пару реальных сорцов (код, схему базы данных) - не AI фокус
### сделать промпт чтобы аддишнл контекст запрос возвращался структурно чтобы тула могла доставать файлы / доки сама
### фокус 2
### сделать streamlit чат интерфейс с этим с явным степ-бай-степ чтобы это не выглядело просто как чат о задаче - а это должен быть явный процесс где не ты как инженер драйваешь процесс, а ассистент иногда тебя спрашивает
### не стесняйтесь писать код chatGPT (или антропиком) =)


# 📄 Document question answering template

A simple Streamlit app that answers questions about an uploaded document via OpenAI's GPT-3.5.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://document-question-answering-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

# IMDBot
A Python GPT-based Chatbot for querying data from IMDB non-commercial dataset

## Installation

Run:
```bash
pip install toml openai
```
**Note:** This bot is designed using the latest version of the OpenAI API (1.3.5), released on November 6th, 2023. If you have an older version
of the this Python library installed, run:
```bash
pip install --upgrade openai
```

Once installed, set your OpenAI API Key as an environment variable:
```bash
export OPENAI_API_KEY="YOUR_KEY"
```


## Downloading Data
1. Download the [IMDB dataset](https://datasets.imdbws.com/)
1. Extract all files
1. Place all TSV files under a directory named `/data` in this repo


## Build local DB
Run:
```bash
python create_local_db.py
```
This will generate a file called `imdb.db`


## Run bot
Run:
```bash
python ask.py
```

You may also use the following optional flags:
```
  -m MODEL, --model MODEL   Name of OpenAI chat model to use [default: gpt-4]
  -v, --verbose             Enable verbose mode [default: False]
```

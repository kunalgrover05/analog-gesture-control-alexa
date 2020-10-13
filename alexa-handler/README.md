Flask server for handling requests coming using Alexa custom skill endpoint. Read more about Alexa custom skills [here](https://developer.amazon.com/en-IN/alexa/alexa-skills-kit). This is only needed if you want to activate your gesture-recognition script using an Alexa command *"Launch gesture control"*. 

## Getting started
1- Install dependencies from `requirements.txt`.
2- Setup `config.py` and run the server using `python server.py`
3- Point your Alexa custom skill to your endpoint. If your IP is not static, you might have to use a tunnel proxy such as [NGrok](https://ngrok.com/) or [PageKite](https://pagekite.net/)
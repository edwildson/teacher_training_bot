# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Dict, Text, Any, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

from pymongo import MongoClient

from datetime import datetime

import re

class ActionGetEmail(Action):
    def name(self) -> Text:
        return "action_get_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Por favor, informe seu e-mail.")

        return [SlotSet("email", None)]

class ActionSaveEmail(Action):

    def name(self) -> Text:
        return "action_save_email"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        message = tracker.latest_message.get('text')
        email = re.findall('\S+@\S+', message)[0]

        print("Criando conexão")
        # Crie uma conexão com o servidor MongoDB
        client = MongoClient("mongodb://mongo")
        print("Conexão criada")


        print("Selecionando DB")
        # Selecione um banco de dados
        db = client['amadeus_bot']
        print("DB selecionado")

        print("Selecionando coleção")
        # Selecione uma coleção
        collection = db['teachers']
        print("Coleção selecionada")

        timestamp = datetime.utcnow()

        result = collection.update_one(
            {'email': f'{email}'}, # Critérios de pesquisa
            {'$set': {'nome': 'Prof. Girafales', 'updated_at': timestamp}, }, # Valores a serem atualizados
            upsert=True # Insere um novo documento se não encontrar nenhum documento correspondente
        )
        
        dispatcher.utter_message(text=f"O email é: {email}") # Extrai o email usando expressão regular
        return [SlotSet("email", email)]
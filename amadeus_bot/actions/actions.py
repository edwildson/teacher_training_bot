from typing import Dict, Text, Any, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
import logging

from pymongo import MongoClient

from datetime import datetime

import re

class ActionGetEmail(Action):
    def name(self) -> Text:
        return "action_get_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info("informe seu email")
        dispatcher.utter_message(text="Por favor, informe seu e-mail.")

        return [SlotSet("email", None)]

class ActionSaveEmail(Action):

    def name(self) -> Text:
        return "action_save_email"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        email = tracker.get_slot("email")

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
        
        return None

class ConfirmEmailAction(Action):
    def name(self):
        return "confirm_email"

    def run(self, dispatcher, tracker, domain):
        logging.info("Confirmando email")
        message = tracker.latest_message.get('text')
        email = re.findall(r'\S+@\S+', message)[0]

        buttons = [
            {"title": "Sim", "payload": "/acao1"},
            {"title": "Não", "payload": "/acao2"},
        ]

        message = {
            "text": f'O seu email é {email}?',
            "buttons": buttons
        }

        dispatcher.utter_message(text=message["text"], buttons=message["buttons"])

        return [SlotSet("email", email)]  # Atualize os slots se necessário

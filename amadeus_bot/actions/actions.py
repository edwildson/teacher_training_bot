from typing import Dict, Text, Any, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset
import logging

from pymongo import MongoClient
from bson import ObjectId

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
        return "action_email_confirmation"

    def run(self, dispatcher, tracker, domain):
        logging.info("Confirmando email")
        message = tracker.latest_message.get('text')
        email = re.findall(r'\S+@\S+', message)[0]

        buttons = [
            {"title": "Sim", "payload": "este é meu email"},
            {"title": "Não", "payload": "este não é meu email"},
        ]

        message = {
            "text": f'O seu email é {email}?',
            "buttons": buttons
        }

        dispatcher.utter_message(text=message["text"], buttons=message["buttons"])

        return [SlotSet("email", email)]  # Atualize os slots se necessário

class ActionCheckEmail(Action):

    def name(self) -> Text:
        return "action_check_email"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        email = tracker.get_slot("email")
        logging.info(f"checando email... ({email})")

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

        teacher = collection.find_one({'email': f'{email}'})

        logging.info(teacher)

        if teacher:
            logging.info('encontrou')
            dispatcher.utter_message(text=f"Olá, {teacher['name']}")
            return [
                SlotSet("teacher", teacher['name']),
                SlotSet("teacher_id", str(teacher['_id'])),
            ]
        else:
            logging.info('não encontrou')
            dispatcher.utter_message(template="utter_fim_conversa")
            return None

class ActionStartTraining(Action):
    def name(self):
        return "action_start_training"

    def run(self, dispatcher, tracker, domain):
        teacher_id = tracker.get_slot("teacher_id")
        logging.info(f"Iniciando treinamento ({teacher_id})")
        

        # Crie uma conexão com o servidor MongoDB
        client = MongoClient("mongodb://mongo")
        
        # Selecione um banco de dados
        db = client['amadeus_bot']
       
        # Selecione uma coleção
        collection = db['training']

        training = collection.find({'teacher_id': f'{teacher_id}'}).sort("_id", -1).limit(1)

        logging.info(f"training: {training}")
        
        if training.count_documents() == 1:
            dispatcher.utter_message(text=f"Bem vindo novamente ao treinamento")
            
            buttons = [
                {"title": "Sim", "payload": "continuar treinamento"},
                {"title": "Não", "payload": "sair"},
            ]

            message = {
                "text": f'Gostaria de continuar o treinamento agora?',
                "buttons": buttons
            }

            dispatcher.utter_message(text=message["text"], buttons=message["buttons"])
        else:
            buttons = [
                {"title": "Sim", "payload": "continuar treinamento"},
                {"title": "Não", "payload": "sair"},
            ]

            message = {
                "text": f'Gostaria de iniciar o treinamento agora?',
                "buttons": buttons
            }

            dispatcher.utter_message(text=message["text"], buttons=message["buttons"])


        # message = tracker.latest_message.get('text')
        # email = re.findall(r'\S+@\S+', message)[0]

        # buttons = [
        #     {"title": "Sim", "payload": "este é meu email"},
        #     {"title": "Não", "payload": "este não é meu email"},
        # ]

        # message = {
        #     "text": f'O seu email é {email}?',
        #     "buttons": buttons
        # }

        # dispatcher.utter_message(text=message["text"], buttons=message["buttons"])

        return []  # Atualize os slots se necessário


class ActionTraining(Action):
    def name(self):
        return "action_training"

    def run(self, dispatcher, tracker, domain):
        teacher_id = tracker.get_slot("teacher_id")

        logging.info(f"Capturando contexto de treinamento do professor ({teacher_id})")


        # Crie uma conexão com o servidor MongoDB
        client = MongoClient("mongodb://mongo")
        
        # Selecione um banco de dados
        db = client['amadeus_bot']
       
        # Selecione uma coleção
        collection = db['teachers']
      
        timestamp = datetime.utcnow()

        documento_id = ObjectId(teacher_id)

        teacher = collection.find_one({'_id': documento_id})
        
        logging.info(teacher)

        if teacher is not None:
            if teacher is not None and 'challenge' in teacher:
                challenge = teacher['challenge']

                # Inicia treinamento a partir do último
                logging.info(f"Beleza porra, pegou o desafio: ${challenge}")
                dispatcher.utter_message(text=f"Beleza porra, pegou o desafio: ${challenge}")

                if challenge == 4:
                    dispatcher.utter_message(
                        text=f"Você já finalizou o treinamento. Não se esqueça \
                        de responder o formulário: http://goo.gl/docs/123. \
                        "
                    )
            else:
                # Lida com a situação em que o objeto teacher é None ou não possui a propriedade "challenge"
                logging.info(f"Beleza porra, não tem desafio")
                dispatcher.utter_message(text=f"Beleza porra, não tem desafio")
        else:
            # Inicia treinamento do 0
            logging.info(f"Aí deu ruim")
            dispatcher.utter_message(text=f"Aí deu ruim")

        
        return []  # Atualize os slots se necessário

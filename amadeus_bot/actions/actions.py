from typing import Dict, Text, Any, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, UserUttered, FollowupAction
import logging
import math
import time

from pymongo import MongoClient
from bson import ObjectId

from datetime import datetime, date

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
            {'$set': {'updated_at': timestamp}, }, # Valores a serem atualizados
            upsert=True # Insere um novo documento se não encontrar nenhum documento correspondente
        )
        
        return None

class ConfirmEmailAction(Action):
    def name(self):
        return "action_email_confirmation"

    def run(self, dispatcher, tracker, domain):
        logging.info("Confirmando email")
        message = tracker.latest_message.get('text')
        email = str(re.findall(r'\S+@\S+', message)[0]).lower()

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
                SlotSet("teacher_name", teacher['name']),
                SlotSet("teacher_id", str(teacher['_id'])),
            ]
        else:
            logging.info('não encontrou')
            dispatcher.utter_message(response="utter_nao_encontrado")

            restart_action = [FollowupAction(name='action_restart')]

            return restart_action

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
        
        if training.count() == 1:
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


class ActionBeforeTraining(Action):
    def name(self):
        return "action_before_training"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

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
            if 'done' in teacher:
                done = teacher['done']

                logging.info(f"Done: {done}")

                if done is True:
                    dispatcher.utter_message(
                        text=f"Você já finalizou o treinamento. Não se esqueça de responder o formulário: http://goo.gl/docs/123."
                    )
                    return [SlotSet("done", True)]
            elif 'last_quest_date' in teacher:
                last_quest_date = teacher['last_quest_date']

                if last_quest_date == date.today().strftime('%d-%m-%Y'):
                    dispatcher.utter_message(
                        text=f"Você já finalizou os desafios do dia de hoje, volte amanhã para novos desafios"
                    )
                    return [SlotSet("today", True)]
                
            buttons = [
                {"title": "Sim", "payload": "iniciar desafios"},
                {"title": "Não", "payload": "sair"},
            ]

            message = {
                "text": f'Gostaria de iniciar os desafios agora?',
                "buttons": buttons
            }

            dispatcher.utter_message(text=message["text"], buttons=message["buttons"])
               
            # Lida com a situação em que o objeto teacher é None ou não possui a propriedade "challenge"
            # logging.info(f"Beleza porra, não tem desafio")
            # dispatcher.utter_message(text=f"Beleza porra, não tem desafio")
        else:
            # Inicia treinamento do 0
            logging.info(f"Aí deu ruim")
            dispatcher.utter_message(text=f"Aí deu ruim")

        
        return []  # Atualize os slots se necessário

class ActionTraining(Action):
    def name(self):
        return "action_training"

    def save_training_time(self, teacher_id, challenge, question_number):
        # logging.info(f"Capturando contexto de treinamento do professor ({teacher_id})")


        # Crie uma conexão com o servidor MongoDB
        client = MongoClient("mongodb://mongo")
        
        # Selecione um banco de dados
        db = client['amadeus_bot']
       
        # Selecione uma coleção
        collection = db['teachers']
      
        timestamp = datetime.utcnow()

        documento_id = ObjectId(teacher_id)

        teacher = collection.find_one({'_id': documento_id})

        collection = db['challenges']
               
        desafios = collection.find_one({'challenge': math.floor(challenge)})

        training_time = {
            'challenge': math.floor(challenge),
            'question_number': question_number,
            'datetime': datetime.now().strftime("%H:%M:%S %m/%d/%Y"),
            'teacher_id': documento_id,
            'created_at': timestamp,
        }

        if challenge == desafios['last']:
            training_time['last'] = True
            collection = db['teachers']
            collection.update_one(
                {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                {'$addToSet': {
                    'training_time': training_time,
                }, # Valores a serem atualizados
                }
            )
        
        elif question_number == 0:
            training_time['first'] = True
            collection = db['teachers']
            collection.update_one(
                {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                {'$addToSet': {
                    'training_time': training_time,
                }, # Valores a serem atualizados
                }
            )

        else:
            collection = db['teachers']
            collection.update_one(
                {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                {'$addToSet': {
                    'training_time': training_time,
                }, # Valores a serem atualizados
                }
            )

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        teacher_id = tracker.get_slot("teacher_id")

        # logging.info(f"Capturando contexto de treinamento do professor ({teacher_id})")


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
            # Selecione uma coleção
            collection = db['challenges']

            documento_id = ObjectId(teacher_id)
            challenge = 1

            logging.info(f"...")

            if 'last_quest_date' in teacher:
                last_quest_date = teacher['last_quest_date']
                
                if last_quest_date == date.today().strftime('%d-%m-%Y'):
                    dispatcher.utter_message(
                        text=f"Você já finalizou os desafios do dia de hoje, volte amanhã para novos desafios"
                    )

                    return [SlotSet("today", True)]

            if 'challenge' in teacher:
                challenge = teacher['challenge']
                collection = db['challenges']
               
                desafios = collection.find_one({'challenge': math.floor(float(challenge))})

                logging.info(f"continuando treinamento")

                if challenge == desafios['last']:
                    last_quest_date = teacher.get('last_quest_date', None)

                    logging.info(f"chegou ao final de um desafio")

                    if last_quest_date is None:
                        dispatcher.utter_message(
                            text=f"Você já finalizou os desafios do dia de hoje, volte amanhã para novos desafios"
                        )

                        collection = db['teachers']
                        collection.update_one(
                            {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                            {'$set': {'last_quest_date': date.today().strftime('%d-%m-%Y'), 'updated_at': timestamp}, }, # Valores a serem atualizados
                        )

                        return [SlotSet("today", True)]
                    else:
                        logging.info(f"iniciando próximo desafio")
                        challenge = float(str(math.floor(challenge)+1) + "." + "0")
                        desafios = collection.find_one({'challenge': math.floor(challenge)})
                
                # Inicia treinamento a partir do último
                logging.info(f"Beleza, pegou o desafio: {challenge}")

                # if challenge == 4:
                #     # dispatcher.utter_message(
                #     #     text=f"Você já finalizou o treinamento. Não se esqueça de responder o formulário: http://goo.gl/docs/123."
                #     # )
                #     logging.info(f"Done, vaze!")
                #     return [SlotSet("done", True)]

                buttons = [
                    {"title": "Feito", "payload": "iniciar desafios"},
                    {"title": "Ajuda", "payload": "sair"},
                ]

                question_number = int(str(challenge)[2:])

                logging.info(f"{question_number+1} desafio")
                next_question_number = float(str(math.floor(challenge)) + "." + str(question_number+1))
                logging.info(f"proximo desafio: {question_number+1}")

                last_date = date.today().strftime('%d-%m-%Y') if next_question_number == desafios['last'] else None
                
                while desafios["questions"][question_number].get('is_info', False) is True:
                    message = {
                        "text": f'{desafios["questions"][question_number]["question"]}',
                        "tip": f'{desafios["questions"][question_number]["tip"]}',
                        "buttons":  None if desafios["questions"][question_number].get('is_info', False) is True else buttons,
                        "image": desafios["questions"][question_number].get("img_path", None),
                    }

                    dispatcher.utter_message(
                        text=message["text"],
                        buttons=None if message["tip"] else message["buttons"],
                        parse_mode='MarkdownV2',
                    )

                    if message['tip']:
                        dispatcher.utter_message(
                            text=message["tip"],
                            buttons=None if message["image"] else message["buttons"],
                            parse_mode='MarkdownV2',
                        )

                    if message['image']:
                        logging.info(f"Enviando a primeira foto")
                        dispatcher.utter_message(
                            image=message["image"][0],
                        )
                        logging.info(f"Enviando a segunda foto")
                        dispatcher.utter_message(
                            image=message["image"][1],
                            buttons=message["buttons"],
                        )

                    self.save_training_time(teacher_id, challenge, question_number)

                    challenge = next_question_number
                    question_number = int(str(challenge)[2:])

                    logging.info(f"{question_number+1} desafio")

                    next_question_number = str(str(math.floor(challenge)) + "." + str(question_number+1)) if question_number == 9 else float(str(math.floor(challenge)) + "." + str(question_number+1))

                    last_date = date.today().strftime('%d-%m-%Y') if next_question_number == desafios['last'] else None

                logging.info(f"saiu do while")
                message = {
                    "text": f'{desafios["questions"][question_number]["question"]}',
                    "tip": f'{desafios["questions"][question_number]["tip"]}',
                    "buttons":  None if desafios["questions"][question_number].get('is_info', False) is True else buttons,
                    "image": desafios["questions"][question_number].get("img_path", None),
                }

                dispatcher.utter_message(
                    text=message["text"],
                    buttons=None if message["tip"] else message["buttons"],
                    parse_mode='MarkdownV2',
                )

                if message['tip']:
                    dispatcher.utter_message(
                        text=message["tip"],
                        buttons=None if message["image"] else message["buttons"],
                        parse_mode='MarkdownV2',
                    )
                if message['image']:
                    logging.info(f"Enviando a primeira foto")
                    dispatcher.utter_message(
                        image=message["image"][0],
                    )
                    logging.info(f"Enviando a segunda foto")
                    dispatcher.utter_message(
                        image=message["image"][1],
                        buttons=message["buttons"],
                    )
                
                self.save_training_time(teacher_id, challenge, question_number)

                collection = db['teachers']
                collection.update_one(
                    {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                    {'$set': {
                        'challenge': next_question_number,
                        'last_quest_date': last_date,
                        'updated_at': timestamp}, 
                    }, # Valores a serem atualizados
                )

            else:
                logging.info(f"Primeiro desafio desafio")
                collection = db['challenges']
                desafios = collection.find_one({'challenge': challenge})

                # Inicia treinamento a partir do último
                logging.info(f"Desafios: {desafios}")

                buttons = [
                    {"title": "Feito", "payload": "iniciar desafios"},
                    {"title": "Ajuda", "payload": "sair"},
                ]

                message = {
                    "text": f'{desafios["questions"][0]["question"]}',
                    "tip": f'{desafios["questions"][0]["tip"]}',
                    "buttons":  buttons if {desafios["questions"][0].get('is_info', False)} else None,
                    "image": desafios["questions"][0].get("img_path", None),
                }
                
                dispatcher.utter_message(
                    text=message["text"],
                    buttons=None if message["tip"] else message["buttons"],
                    parse_mode='MarkdownV2',
                )

                if message['tip']:
                    dispatcher.utter_message(
                        text=message["tip"],
                        buttons=None if message["image"] else message["buttons"],
                        parse_mode='MarkdownV2',
                    )
                if message['image']:
                    logging.info(f"Enviando a primeira foto")
                    dispatcher.utter_message(
                        image=message["image"][0],
                    )
                    logging.info(f"Enviando a segunda foto")
                    dispatcher.utter_message(
                        image=message["image"][1],
                        buttons=message["buttons"],
                    )

                logging.info(f"Atualizando desafio do {teacher['email']}")

                self.save_training_time(teacher_id, challenge, 0)

                collection = db['teachers']
                collection.update_one(
                    {'email': f'{teacher["email"]}'}, # Critérios de pesquisa
                    {'$set': {'challenge': 1.1, 'updated_at': timestamp}, }, # Valores a serem atualizados
                )
        else:
            # Inicia treinamento do 0
            logging.info(f"Aí deu ruim")
            dispatcher.utter_message(text=f"Aí deu ruim")

        
        return []  # Atualize os slots se necessário


class ActionFinish(Action):
    def name(self) -> Text:
        return "action_finish"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info(f"Você finalizou o treinamento, não se esqueça de responder o formulário que será enviado para você.")
        dispatcher.utter_message(text="Você finalizou o treinamento, não se esqueça de responder o formulário que será enviado para você.")
        return [UserUtteranceReverted()]
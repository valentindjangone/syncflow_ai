import json
from fastapi import HTTPException
import openai
import os
import MySQLdb
import uuid
import random
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from scipy.stats import mannwhitneyu
import datetime
from datetime import datetime, timedelta
from nltk.corpus import stopwords
from collections import Counter
import re
import nltk


load_dotenv()

#
def extract_mission_details(mission):
    messages = [{
            "role": "system",
            "content": """
                        You are a project manager who has contributed to the creation of hundreds of companies, all in different fields, which allows you to have global expertise. 
                        """},
                        {
            "role": "user",
            "content": f"As a mission provider on the platform, you benefit from an AI assistant that helps you to extract technical details from a mission so you can frame your needs rapidly and accurately.\
                Here is the mission description : {mission}"
                }]

    function = {
        "name": "mission",
        "description" : "A function that takes in a mission description and returns a list of technical deductions",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "name" : {
                    "type" : "string",
                    "description" : "A synthetic name of the mission"
                },
                "abstract" : {
                    "type" : "string",
                    "description" : "A reformulated, synthetic description of the mission"
                },
                "detail" : {
                "type" : "string",
                "description" : "An advanced technical reformulation of the mission. Don't add vague emphasis on the quality demanded." #"highlight important details with the html tags <b> </b and make it readable with <br> </br>" 
                },
                "roles": {
                "type": "array",
                "description": "A list of the different required roles to accomplish the mission, roles must be related to tech/developpement/design.",
                "items": {
                    "type": "object",
                    "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "name of the role" #"emoji related to the role + name of the role"
                    },
                    "skills_required": {
                        "type": "array",
                        "items": {
                        "type": "string"
                        },
                        "description": "List of skills required for the role"
                    },
                    "reason" : {
                        "type" : "string",
                        "description" : "The reason why this role is required"
                        
                    }
                    },
                    "required": ["role_name", "skills_required", "reason"]
                }
                },
                "budget": {
                    "type": "object",
                    "description": "Budget details of the mission if mentioned in the mission or a fair assessment of the budget",
                    "properties": {
                        "total": {
                            "type": "number",
                            "description": "The total cost of the mission"
                        },
                        "roles_budget": {
                            "type": "array",
                            "description": "Budget allocation for each role involved in the mission",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role_name": {
                                        "type": "string",
                                        "description": "Name of the role"
                                    },
                                    "allocated_budget": {
                                        "type": "number",
                                        "description": "Budget allocated for this role"
                                    }
                                },
                                "required": ["role_name", "allocated_budget"]
                            }
                        }
                    },
                    "required": ["total", "roles_budget"]
                }
                
                
                
                },
                "required": ["name", "abstract", "detail", "roles", "budget"]
            
            }
        }

    response = openai.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        functions=[function],
        function_call={"name": "mission"}, # this forces calling `function`
    )

    raw_response = response.model_dump()
    raw_response['prompt_cost'] = response.usage.prompt_tokens * 0.01/1000
    raw_response['completion_cost'] = response.usage.completion_tokens * 0.03/1000
    raw_response['cost'] = {'prompt' : raw_response['prompt_cost'], 'completion' : raw_response['completion_cost'], 'total' : raw_response['prompt_cost'] + raw_response['completion_cost']}
    raw_response['id'] = uuid.uuid1()

    mission_dict = json.loads(response.model_dump()['choices'][0]['message']['function_call']['arguments'])
    mission_dict['id'] = uuid.uuid1()
    mission_dict['created'] = raw_response['created']
    mission_dict['metadata_id'] = raw_response['id']

    return mission_dict, raw_response

def update_mission_details(mission_id, mission_update):
    # Connexion à la base de données MySQL en utilisant la fonction existante
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        # Construction de la requête SQL pour mettre à jour la mission
        update_query = "UPDATE processed_mission SET "
        update_parts = []
        params = []

        if mission_update.abstract is not None:
            update_parts.append("mission_abstract = %s")
            params.append(mission_update.abstract)

        if mission_update.detail is not None:
            update_parts.append("mission_detail = %s")
            params.append(mission_update.detail)

        # Ajoutez d'autres champs ici si nécessaire

        update_query += ", ".join(update_parts)
        update_query += " WHERE id = %s"
        params.append(str(mission_id))

        # Exécution de la requête
        cursor.execute(update_query, params)
        conn.commit()

    except MySQLdb.Error as e:
        print(f"Error updating mission: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    finally:
        cursor.close()
        conn.close()

    return {"message": "Mission updated successfully"}

def generate_mission(n=10, model="gpt-4-1106-preview", temperature=0.85):

    skills = [
        "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "Go", "Rust", "Kotlin", "Swift", "TypeScript",
        "React", "Angular", "Vue.js", "Ember.js",
        "Django", "Flask", "Node.js", "Express.js", "Spring Boot", "Ruby on Rails",
        "SQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
        "AWS", "Azure", "GCP",
        "Docker", "Kubernetes", "Jenkins", "Terraform",
        "Linux", "Unix", "Windows Server",
        "TensorFlow", "PyTorch", "Scikit-learn",
        "Cryptography", "Penetration Testing", "Firewall Management",
        "Adobe XD", "Sketch", "Figma",
        "GraphQL", "API REST", "WebRTC", "Blockchain", "Elasticsearch"
        ]
    

    tech_saviness = np.random.choice(['have a vague idea of tech', 'know a bit of tech', 'know a lot of tech', 'know nothing about tech'])
    rand_comb = random.sample(skills, random.randint(0, 3))
    
    messages = [{"role" : "system",
                "content" : f"""
                
                You are a mission offerer on a web dev/tech freelance platform. You {tech_saviness}. You want your mission to be done with either\
                combinations of these skills : {str(rand_comb)} or you might have no technological preference. Be concise and coherent.\
                Go straight to the point. \
                Don't write it in the form of a job offer but as you would like it to be done. Don't 
                        """}]
    

    response_generate = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=250,
    )

    text_response = response_generate.model_dump()["choices"][0]["message"]["content"]

    return text_response

def generate_feedback(mission, raw_response, feedback_date, rating, rating_limits=False, rating_auto=False, model="gpt-4-1106-preview", temperature=1.2):
    
    if rating_auto and rating_limits:
        rating = np.random.randint(rating_limits[0], rating_limits[1]+1)
    else:
        rating=rating

    messages = [
        {
        "role" : "system",
        "content" : f"You simulate a project owner that just submitted a mission on the platform,\
        you benefit from an ai assistant that helps you to extract technical details from that mission so you can frame your needs rapidly and accurately.\
        This time, the AI was not performant enough. You give it a rating of {rating} stars out of 5 and you decide to fill a survey to give a feedback. Here is your original posted mission : {mission} "
        },

        {
            "role" : "user",
            "content" : json.loads(raw_response['choices'][0]['message']['function_call']['arguments'])['detail']
        }
        ]

    function = {"name" : "feedback",
    "description" : "A function that takes in a mission processed by the AI and returns a list of feedback given by the user",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "user_rating" : {
                "type" : "integer",
                "description" : "The rating given by the user",

            },
            "user_comments" : {
                "type" : "string",
                "description" : "The comments given by the user",
                "minLength" : 30,
                "maxLength" : 500
            },
            "modification_details" : {
                "type" : "string",
                "description" : "The mission details given by the AI modified or rectified by the user it can be fully modified, partially or not at all if the user was satisfied",
            },


        },
        "required" : ["user_rating", "user_comments", "modification_details", "prompt_version"]

    }}
    response = openai.chat.completions.create(
        model = model,
        messages = messages,
        temperature = temperature,
        functions = [function],
        function_call = {"name" : "feedback"}
    )

    feedback_dict = json.loads(response.model_dump()['choices'][0]['message']['function_call']['arguments'])
    feedback_dict['id'] = uuid.uuid1()
    feedback_dict['created'] = feedback_date
    feedback_dict['prompt_version'] = np.random.choice(['v1', 'v2'])
    feedback_dict['mission_id'] = raw_response['id']
    
    return feedback_dict

def connect_to_db():
    db_host = os.getenv("DATABASE_HOST_B")
    db_user = os.getenv("DATABASE_USERNAME_B")
    db_password = os.getenv("DATABASE_PASSWORD_B")
    db_name = os.getenv("DATABASE")

    if not all([db_host, db_user, db_password, db_name]):
        raise Exception("Les informations de connexion à la base de données sont incomplètes.")

    connection = MySQLdb.connect(
        host=db_host,
        user=db_user,
        passwd=db_password,
        db=db_name,
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={"ca": "/etc/secrets/cert.pem"}
    )
    return connection

def fetch_data(query):
    with connect_to_db() as db:
        cur = db.cursor()
        cur.execute(query)
        columns = [col[0] for col in cur.description]
        data = pd.DataFrame(list(cur.fetchall()), columns=columns)
        cur.close()
    return data


def fetch_feedback(days, which_db): # DAG

    host = os.getenv('DATABASE_HOST_' + str(which_db))
    user = os.getenv('DATABASE_USERNAME_' + str(which_db))
    passwd = os.getenv('DATABASE_PASSWORD_' + str(which_db))
    db = os.getenv('DATABASE')

    # Établir la connexion à la base de données
        # Connexion à la base de données
    connection = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={"ca": "/etc/secrets/cert.pem"}
    )    
    cursor = connection.cursor()

    # Obtenir la date la plus récente des notes dans la base de données
    cursor.execute("SELECT MAX(created) FROM user_feedback")
    most_recent_date = cursor.fetchone()[0]
    if most_recent_date is None:
        return np.array([])  # Retourner un tableau vide s'il n'y a pas de notes

    # Calculer la date de début pour la période de 15 jours
    start_date = most_recent_date - timedelta(days=days)

    # Requête SQL pour récupérer les notes sur la période spécifiée
    query = """
    SELECT user_rating, user_comments FROM user_feedback
    WHERE created BETWEEN %s AND %s
    """
    cursor.execute(query, (start_date, most_recent_date))
    ratings = [item[0] for item in cursor.fetchall()]
    comments = [item[1] for item in cursor.fetchall()]
    # Fermeture du curseur et de la connexion à la base de données
    cursor.close()
    connection.close()

    return {'ratings': ratings, 'comments': comments, "start_date": start_date, "end_date": most_recent_date}

def store_processed_mission(mission_dict):
    connection = connect_to_db()
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO processed_mission (id, created, mission_name, mission_abstract, mission_detail, roles, budget, metadata_id) 
            VALUES (%s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s)
        """
        created = mission_dict["created"]
        budget = mission_dict.get("budget")
        if budget is not None:
            budget = json.dumps(budget)
        name = mission_dict.get("name")
        if name is not None:
            name = json.dumps(name)
        abstract = mission_dict.get("abstract")
        if abstract is not None:
            abstract = json.dumps(abstract)
        detail = mission_dict.get("detail")
        if detail is not None:
            detail = json.dumps(detail)
        roles = mission_dict.get("roles")
        if roles is not None:
            roles = json.dumps(roles)

        cursor.execute(insert_query, (
            mission_dict["id"],
            created,
            name,
            abstract,
            detail,
            roles,  # Utilise une liste vide si "roles" n'est pas présent
            budget,  # Utilise None si "budget" n'est pas présent
            mission_dict["metadata_id"]
        ))

    except Exception as e:
            # Cela capturera toutes les exceptions, y compris KeyError, MySQLdb.Error, etc.
            raise HTTPException(status_code=500, detail=f"Erreur rencontrée : {str(e)}")

    finally:
        if connection and connection.open:
            cursor.close()
            connection.close()

def store_raw_response(raw_response):
    connection = connect_to_db()

    try:
        cursor = connection.cursor()

        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO raw_response (
                id, created, choices, model, object, system_fingerprint, usage, cost
            ) VALUES (
                %s, FROM_UNIXTIME(%s), %s, %s, %s, %s, %s, %s
            )
            """
        cursor.execute(insert_query, (
            raw_response["id"], 
            raw_response["created"], 
            json.dumps(raw_response["choices"][0]), 
            raw_response["model"], 
            raw_response["object"], 
            raw_response["system_fingerprint"], 
            json.dumps(raw_response["usage"]),
            json.dumps(raw_response["cost"])
        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()

def store_feedback(feedback):
    connection = connect_to_db()

    try:
        cursor = connection.cursor()
        
        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO user_feedback (
                id, user_rating, user_comments, prompt_version, mission_id, created
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """
        cursor.execute(insert_query, (
            feedback.get("id"),
            feedback.get("user_rating"), 
            feedback.get("user_comments"),
            feedback.get("prompt_version"),
            feedback.get('mission_id'),
            feedback.get('created')

        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()

def get_wordcount(which_db):
    # Paramètres de connexion à la base de données
    host = os.getenv('DATABASE_HOST_' + str(which_db))
    user = os.getenv('DATABASE_USERNAME_' + str(which_db))
    passwd = os.getenv('DATABASE_PASSWORD_' + str(which_db))
    db = os.getenv('DATABASE')


    # Connexion à la base de données
    connection = MySQLdb.connect(
        host=host,
        user=user,
        passwd=passwd,
        db=db,
        autocommit=True,
        ssl_mode="VERIFY_IDENTITY",
        ssl={"ca": "/etc/secrets/cert.pem"}
    )
    cursor = connection.cursor()

    # Requête SQL pour récupérer les 50 derniers commentaires
    sql = "SELECT user_comments FROM user_feedback WHERE user_rating BETWEEN 1 AND 3 LIMIT 150"
    cursor.execute(sql)

    # Récupération des données
    comments = [item[0] for item in cursor.fetchall()]
    nltk.download('stopwords')

    # Liste des stop words
    stop_words = set(stopwords.words('english') + ['ai'])

    # Nettoyage et comptage des mots
    words = []
    for comment in comments:
        comment = re.sub(r'\W+', ' ', comment.lower())
        words.extend([word for word in comment.split() if word not in stop_words])

    word_freq = Counter(words)

    # Utilisation de most_common pour récupérer les 20 termes les plus fréquents
    top_words_freq = word_freq.most_common(40)

    # Conversion des données en format JSON
    wordcloud_data = [{'name': word, 'value': freq} for word, freq in top_words_freq]
    # Fermeture de la connexion à la base de données
    cursor.close()
    connection.close()

    return wordcloud_data

def get_stats(days):

    # Utilisation de la fonction pour récupérer les notes des deux bases de données
    feedback_a = fetch_feedback(days, which_db="A")
    feedback_b = fetch_feedback(days, which_db="B")

    ratings_a = feedback_a['ratings']
    ratings_b = feedback_b['ratings']

    start_date = feedback_a['start_date']
    end_date = feedback_a['end_date']
    # Effectuer le test de Mann-Whitney U
    u_stat, p_value = mannwhitneyu(ratings_a, ratings_b)
    alpha = 0.05

    dico = {#"wordcount": wordcount,
            'start_date': start_date,
            'end_date': end_date,
            'n_values_A': len(ratings_a),
            'n_values_B': len(ratings_b),
            'U_stat': u_stat,
            'p_value': p_value,
            "mean_A": np.mean(ratings_a), 
            "mean_B" : np.mean(ratings_b),
            "significance_threshold": alpha}

    # Interprétation
    if p_value > alpha:
        dico['significance'] = "Pas de différence significative"
    else:
        dico['significance'] = "Différence significative"

    return dico


def write_feedback(mission_id, user_comment, rating, prompt_version='unknown'):

    generated_id = {'id' : uuid.uuid1()}

    feedback = dict(generated_id)
    feedback['id'] = uuid.uuid1()
    feedback['user_rating'] = int(rating)
    feedback['user_comments'] = str(user_comment)
    feedback['mission_id'] = mission_id
    feedback['prompt_version'] = prompt_version
    feedback['created'] = datetime.datetime.today()
    connection = connect_to_db()

    try:
        cursor = connection.cursor()

        # Préparation et exécution de la requête SQL
        insert_query = """
            INSERT INTO user_feedback (
                id, user_rating, user_comments, mission_id, created, prompt_version
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """

        cursor.execute(insert_query, (
            feedback.get("id"),
            feedback.get("user_rating"),
            feedback.get("user_comments"),
            feedback.get('mission_id'),
            feedback.get('created'),
            feedback.get('prompt_version')
        ))

    except MySQLdb.Error as err:
        raise err

    finally:
        # Fermeture de la connexion à la base de données
        if connection and connection.open:
            cursor.close()
            connection.close()
            
    # Après insertion dans la base de données
    feedback_id = feedback.get("id")
    
    # Retourner l'ID de feedback ou l'objet de feedback
    return {'id': feedback_id}
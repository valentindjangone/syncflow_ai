import json
from fastapi import HTTPException
import openai
from dotenv import load_dotenv
import os
import MySQLdb
import uuid

load_dotenv()

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
                    "description" : "A synthetic description of the mission"
                },
                "detail" : {
                "type" : "string",
                "description" : "A detailed description of the mission"
                },
                "roles": {
                "type": "array",
                "description": "A list of the different required roles to accomplish the mission, roles must be related to tech/developpement/design.",
                "items": {
                    "type": "object",
                    "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "emoji related to the role + name of the role"
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

def get_db_connection():
    db_host = os.getenv("DATABASE_HOST")
    db_user = os.getenv("DATABASE_USERNAME")
    db_password = os.getenv("DATABASE_PASSWORD")
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
        ssl={"ca": "/etc/ssl/cert.pem"}
    )
    return connection

def store_processed_mission(mission_dict):
    connection = get_db_connection()
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
    connection = get_db_connection()

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

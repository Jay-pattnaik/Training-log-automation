import os
import logging
import random
import re
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import StreamingResponse
from io import BytesIO
# Constants
from constants import HOST, PORT, LOG_DIR, WORKERS, DEBUG, credentials
import shutil

import base64
# Constants
ALLOWED_ORIGIN = "*"
LOG_FILE_FORMAT = 'training_class_%d_%m_%Y.log'

# Create log directory if not exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, datetime.now().strftime(LOG_FILE_FORMAT))),
        logging.StreamHandler()],
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

# Initialize FastAPI app
app = FastAPI()




# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
sql_manager = MySQLDatabase(**credentials)

@app.post("/new_assistant")
async def new_assistant(data: dict):
    """
    Endpoint to create a new GPT-4 assistant.

    Parameters:
        - data (dict): A dictionary containing the following keys:
        - user_name (str): The name of the user.
        - user_id (str): The unique identifier for the user.
        - topic (str): The topic associated with the assistant.

    Returns:
    - dict: A dictionary containing either the newly created assistant's ID and status if successful,
            or an error message and status if there was an issue.
    """
    try:
        user_name = data.get("user_name")
        user_id = data.get("user_id")

        logging.info(f"payload received from /new_assistant: {data}")

        if not user_name or not user_id:
            raise HTTPException(status_code=400, detail="User name and User ID are required")

        assistant_id = assistant_manager.create_gpt_4_assistant(user_id, user_name)
        logging.info(f"Assistant created: {assistant_id}")

        if assistant_id:
            return {
                "success": True,
                "message": "assistant created",
                "data": {"assistant_id": assistant_id}
            }
        else:
            return {
                "success": False,
                "messages": "error while creating new assistant",
                "data":
                    {
                        'assistant_id': ''
                    }
            }

    except Exception as e:
        logging.critical(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/modify_assistant")
async def modify_assistant(data: dict):
    """
    Endpoint to modify GPT-4 assistant.

    Parameters:
        - data (dict): A dictionary containing the following keys:
        - instruction (str): The instruction for the assistant.
        - user_name (str): The name of the user.
        - user_id (str): The unique identifier for the user.
        - topic (str): The topic associated with the assistant.

    Returns:
    - dict: A dictionary containing either the newly created assistant's ID and status if successful,
            or an error message and status if there was an issue.
    """

    try:
        assistant_id = data.get("assistant_id")
        instruction = data.get("instruction")
        user_name = data.get("user_name")
        user_id = data.get("user_id")
        topic = data.get("topic")
        thread_id = data.get("thread_id")

        logging.info(f"payload received from /start_conversion: {data}")

        # Input validation
        if not assistant_id:
            raise HTTPException(status_code=400, detail="assistant id can't be empty!")

        if not instruction:
            raise HTTPException(status_code=400, detail="instruction can't be empty!")

        if not user_name:
            raise HTTPException(status_code=400, detail="user name can't be empty!")

        if not user_id:
            raise HTTPException(status_code=400, detail="user Id can't be empty!")

        if not topic:
            raise HTTPException(status_code=400, detail="topic can't be empty!")

        if thread_id is None:
            raise HTTPException(status_code=400, detail="thread_id can't be empty!")


        assistant_id, thread_id = assistant_manager.modify_assistant(assistant_id, instruction, topic, user_id, user_name, thread_id)

        logging.info(f"Assistant modified: {assistant_id}")

        print(assistant_id, thread_id)

        if assistant_id and thread_id:
            return {"success": True, "message": "assistant modified successfully", "data": {"assistant_id": assistant_id, "thread_id": thread_id}}
        elif assistant_id and (thread_id == ''):
            return {"success": True, "message": "thread already in use", "data": {"assistant_id": assistant_id, "thread_id": thread_id}}
        else:
            return {"success": False, "messages": "error while modifying assistant", "data": {"assistant_id": '', "thread_id": ''}}

    except Exception as e:
        logging.critical(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation")
async def conversation(data: dict):
    try:
        assistant_id = data.get("assistant_id")
        thread_id = data.get("thread_id")
        user_answer = data.get("user_answer","")

        logging.info(f"payload received from /remove_meeting_session: {data}")

        if not assistant_id:
            raise HTTPException(status_code=400, detail="assistant ID can't be empty!")

        if not thread_id:
            raise HTTPException(status_code=400, detail="thread ID can't be empty!")
        output = thread_manager.run_thread_gpt4(assistant_id=assistant_id, thread_id=thread_id, question=user_answer)

        logging.info(f"output from /remove_meeting_session: {output}")

        return output

    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/extract_qa")
async def extract_qa(data: dict):
    try:
        assistant_id = data.get("assistant_id")
        thread_id = data.get("thread_id")
        extraction_prompt = data.get("extraction_prompt","")

        logging.info(f"payload received from /extract_qa: {data}")

        if not assistant_id:
            raise HTTPException(status_code=400, detail="assistant ID can't be empty!")

        if not thread_id:
            raise HTTPException(status_code=400, detail="thread ID can't be empty!")

        if not extraction_prompt:
            raise HTTPException(status_code=400, detail="question answer extraction prompt can't be empty!")
        output = thread_manager.run_thread_gpt4(assistant_id=assistant_id, thread_id=thread_id, question=extraction_prompt)
        logging.info(f"output from /run_thread_gpt4: {output}")
        return output
    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/evaluate_conversation")
async def evaluate_conversation(data: dict):
    try:
        evalution_prompt = data.get("assistant_id")
        assistant_id = data.get("assistant_id")
        logging.info(f"payload received from: {data}")

        if not assistant_id:
            raise HTTPException(status_code=400, detail="assistant ID can't be empty!")


        output = assistant_manager.delete_gpt_4_assistant(assistant_id=assistant_id)
        logging.info(f"output from /delete_gpt_4_assistant: {output}")
        return output
    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/delete_assistant")
async def delete_assistant(data: dict):
    try:
        assistant_id = data.get("assistant_id")

        logging.info(f"payload received from: {data}")

        if not assistant_id:
            raise HTTPException(status_code=400, detail="assistant ID can't be empty!")


        output = assistant_manager.delete_gpt_4_assistant(assistant_id=assistant_id)
        logging.info(f"output from /delete_gpt_4_assistant: {output}")
        return output
    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete_thread")
async def delete_assistant(data: dict):
    try:
        thread_id = data.get("thread_id")

        logging.info(f"payload received from: {data}")

        if not thread_id:
            raise HTTPException(status_code=400, detail="Thread ID can't be empty!")

        output = thread_manager.delete_thread_id(thread_id=thread_id)
        logging.info(f"output from /delete_thread_id: {output}")
        return output
    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG, workers=WORKERS)
    except Exception as err:
        logging.error(f'Error running the FastAPI application: {err}')

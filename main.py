import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db_manager import MySQLDatabase
from fastapi.staticfiles import StaticFiles
import uvicorn
from constants import HOST, PORT, LOG_DIR, WORKERS, DEBUG, credentials
from utils import process_class_data_to_csv, convert_to_24_hour_format

# Constants
ALLOWED_ORIGIN = "*"
LOG_FILE_FORMAT = 'training_class_%d_%m_%Y.log'

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, datetime.now().strftime(LOG_FILE_FORMAT))),
        logging.StreamHandler()],
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sql_manager = MySQLDatabase(**credentials)

app.mount("/generated_csvs", StaticFiles(directory="generated_csvs"), name="generated_csvs")

@app.post("/register_new")
async def new_student(data:dict):
    try:
        roll_no= data.get("roll_no", "")
        student_name = data.get("student_name", "")
        contact_no = data.get("contact_no", "")
        logging.info(f"payload received from /register_new: rollno- {roll_no} student_name- {student_name} contact_info- {contact_no}")

        if not roll_no or not student_name or not contact_no:
            raise HTTPException(status_code=400, detail="roll_no, student_name and contact_no are required")

        register_status = sql_manager.insert_student_info(roll_no=roll_no,student_name=student_name,contact_no=contact_no)
        logging.info(f"sql status: {register_status}")

        if register_status["status"] == 1:
            return {
                "success": True,
                "message": "student registration completed",
                "data": {"roll_no": roll_no, "name":student_name}
            }
        else:
            return {
                "success": False,
                "messages": "error while student registration",
                "data":{"roll_no": roll_no, "name":student_name}
            }

    except Exception as e:
        logging.critical(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/record_class_info")
async def record_class_info(data: dict):
    try:
        roll_no = data.get("roll_no", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        date = data.get("date", "")
        topic = data.get("topic", "")
        logging.info(f"payload received from /record_class_info: roll_no={roll_no} start_time={start_time} end_time={end_time} date={date} topic={topic}")
        start_time= convert_to_24_hour_format(start_time)
        end_time= convert_to_24_hour_format(end_time)
        # Input validation
        if not roll_no:
            raise HTTPException(status_code=400, detail="roll no can't be empty!")

        if not start_time:
            raise HTTPException(status_code=400, detail="start time can't be empty!")

        if not end_time:
            raise HTTPException(status_code=400, detail="end time can't be empty!")

        if not date:
            raise HTTPException(status_code=400, detail="date Id can't be empty!")

        if not topic:
            raise HTTPException(status_code=400, detail="topic can't be empty!")



        new_class_status = sql_manager.insert_class_info(roll_no=roll_no, start_time=start_time, end_time=end_time,date=date, topic=topic)

        logging.info(f"class info insert: {new_class_status}")

        if new_class_status['status'] ==1:
            return {"success": True, "message": "data inserted successfully", "data": {"date": date, "timing": {
                start_time}-{end_time}}}
        else:
            return {"success": False, "messages": "error while inserting data", "data": {"date": date, "timing": {
                start_time}-{end_time}}}

    except Exception as e:
        logging.critical(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/featch_class_info")
async def conversation(data:dict):
    try:
        roll_no = data.get("roll_no", "")
        logging.info(f"payload received from /featch_class_info: {roll_no}")

        if not roll_no:
            raise HTTPException(status_code=400, detail="roll_no can't be empty!")


        output = sql_manager.fetch_class_data(roll_no=roll_no)
        logging.info(f"output from /featch_class_info: {output}")
        csv_file_path = f"generated_csvs/class_data_{roll_no}.csv"
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)
        status = process_class_data_to_csv(output["data"], csv_file_path)
        if status['status']:
            csv_url = f"http://localhost:{PORT}/{status['path']}"
            return {"status": 1, "csv_url": csv_url}
        else:
            return {"status": 0, "error": f"Failed to generate CSV {status['error']}"}

    except Exception as e:
        logging.critical('Error: {}'.format(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG, workers=WORKERS)
    except Exception as err:
        logging.error(f'Error running the FastAPI application: {err}')

import mysql.connector
import traceback
import logging
from mysql.connector import Error
class MySQLDatabase:
    def __init__(self,**credentials):
        self.db_credentials = credentials
        self.connection = None

    def insert_student_info(self, roll_no, student_name, contact_no):
        connection = mysql.connector.connect(**self.db_credentials)
        cursor = connection.cursor(buffered=True)
        try:
            student_register_query = """
            INSERT INTO student_info (roll_no, student_name, contact_info)
            VALUES (%s, %s, %s);
            """

            cursor.execute(student_register_query, (roll_no, student_name, contact_no))

            connection.commit()
            print("Student information inserted successfully.")

        except Error as e:
            logging.error("Error while inserting into student_info: %s", e)
            traceback.print_exc()

        finally:
            cursor.close()
            connection.close()

    def insert_class_info(self, roll_no, start_time, end_time, date, topic):
        connection = mysql.connector.connect(**self.db_credentials)
        cursor = connection.cursor(buffered=True)
        try:
            class_register_query = """
            INSERT INTO class_info (roll_no, start_time, end_time, class_date, topic)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(class_register_query, (roll_no, start_time, end_time, date, topic))

            connection.commit()
            print("Class information inserted successfully.")

        except Error as e:
            logging.error("Error while inserting into class_info: %s", e)
            traceback.print_exc()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def fetch_class_data(self, roll_no):
        # Establish a database connection
        connection = mysql.connector.connect(**self.db_credentials)
        cursor = connection.cursor(dictionary=True)
        try:
            # SQL query to fetch class information and student name
            fetch_query = """
            SELECT 
                s.student_name AS student_name,
                c.start_time,
                c.end_time,
                c.class_date,
                c.topic
            FROM 
                class_info c
            JOIN 
                student_info s
            ON 
                c.roll_no = s.roll_no
            WHERE 
                c.roll_no = %s;
            """

            # Execute the query with the roll_no parameter
            cursor.execute(fetch_query, (roll_no,))

            # Fetch all results
            results = cursor.fetchall()
            return results

        except Error as e:
            logging.error("Error while fetching class data: %s", e)
            traceback.print_exc()
            return None

        finally:
            # Ensure resources are closed
            if cursor:
                cursor.close()
            if connection:
                connection.close()




credentials = {

}

sql_manager = MySQLDatabase(**credentials)

print(sql_manager.fetch_class_data("101"))
from datetime import datetime
import pandas as pd
import pytz

ist_timezone = pytz.timezone('Asia/Kolkata')
def convert_to_24_hour_format(time_str):
    time_24_hour = datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M:%S")
    return time_24_hour

def convert_to_12_hour_format_ist(time_str):
    time_24_hour = datetime.strptime(time_str, "%H:%M:%S")
    localized_time = ist_timezone.localize(time_24_hour)
    time_12_hour = localized_time.strftime("%I:%M %p")
    return time_12_hour

def timedelta_to_12hr_format(timedelta_obj):
    base_time = datetime(1900, 1, 1) + timedelta_obj
    localized_time = ist_timezone.localize(base_time)
    return localized_time.strftime('%I:%M %p')

def process_class_data_to_csv(data, output_csv_path="class_data.csv"):
    """
    Processes class data into a CSV with an additional 'tution_duration' column.

    Args:
        data (list of dict): The data from the `output["data"]` dictionary.
        output_csv_path (str): The path where the CSV file will be saved.

    Returns:
        str: The path to the saved CSV file.
    """
    try:
        df = pd.DataFrame(data)

        df['start_time'] = pd.to_datetime(df['start_time'], format='%I:%M %p')
        df['end_time'] = pd.to_datetime(df['end_time'], format='%I:%M %p')

        df['tution_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

        df['start_time'] = df['start_time'].dt.strftime('%I:%M %p')
        df['end_time'] = df['end_time'].dt.strftime('%I:%M %p')

        df.to_csv(output_csv_path, index=False)

        return {"status":1,"path":output_csv_path}
    except Exception as e:
        return {"status":0,"error":str(e)}


# Example usage
# time_24_hour = "15:00:00"
# time_12_hour_ist = convert_to_12_hour_format_ist(time_24_hour)
# print("12-hour IST format:", time_12_hour_ist)


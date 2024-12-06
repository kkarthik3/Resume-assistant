from langchain_core.tools import tool
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta

ist_timezone = pytz.timezone("Asia/Kolkata")
current_time = datetime.now(ist_timezone)
formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S (%A)")

given_date = datetime(2024, 5, 1, tzinfo=ist_timezone)


@tool
def personal_details(expected_salary:bool,DOB:bool,address:bool,current_employer:bool,experience:bool,communication:bool,contact:bool) -> str:

    """
    This function returns a string containing the personal details of Karthikeyan, filtered by the input boolean parameters.

    Parameters:
    expected_salary (bool): If True, returns a message to contact via email for discussing expected salary.
    DOB (bool): If True, returns the date of birth of Karthikeyan.
    address (bool): If True, returns the native place and current working place of Karthikeyan.
    current_employer (bool): If True, returns the current employer of Karthikeyan.
    experience (bool): If True, returns the total number of years and months of experience of Karthikeyan.
    communication (bool): If True, returns the communication skills of Karthikeyan.
    contact (bool): If True, returns the contact details of Karthikeyan.

    Returns:
        str: A string containing the filtered personal details of Karthikeyan.
    """
    output = ""

    current_time = datetime.now(ist_timezone)

    difference = relativedelta(current_time, given_date)

    if expected_salary:
        output +=  "Please reach me out on email karthickinfo45@gmail.com for discussing about these details\n"
    if DOB:
        output += "My date of birth is 31st March 2001\n"
    if address:
        output += "My native is Chennai but im working in Kerala Kcohin\n"
    if current_employer:
        output += "My current employer is ISPG Technologies, Ernakulam, kerala\n"
    if experience:
        output += f"I have 5 months of Research experience and {difference.years} years {difference.months} months of industry experience"
    if communication:
        output += "I have moderate fluency in english and my native language is tamil\n"
    if contact:
        output += "Please reach me out on email karthickinfo45@gmail.com or socail platforms like linkedin https://www.linkedin.com/in/kkarthick-k/ \n"
    print(output)
    return output

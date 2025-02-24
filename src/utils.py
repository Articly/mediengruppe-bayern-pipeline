from datetime import datetime


def get_weekday() -> str:
    return datetime.today().strftime('%A').lower()

def update_transcript_for_correct_pronounciations(str1 : str) -> str:
    words: dict[str, str] = {"Vilshofen":"Filshofen"}

    for key, val in words:
        str1.replace(key, val)

    return str1

def get_date_with_german_month() -> str:
    month_mapping = {
        "January": "Januar",
        "February": "Februar",
        "March": "März",
        "April": "April",
        "May": "Mai",
        "June": "Juni",
        "July": "Juli",
        "August": "August",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Dezember"
    } 
    date = datetime.today().strftime('%d. %B %Y')
    # find and replace month
    for english_month, german_month in month_mapping.items():
        if english_month in date:
            date = date.replace(english_month, german_month)
            
    return date

from datetime import datetime


def get_weekday() -> str:
    return datetime.today().strftime('%A').lower()

def update_transcript_for_correct_pronounciations(str1 : str) -> str:
    words: dict[str, str] = {"Vilshofen":"Filshofen"}

    for key, val in words:
        str1.replace(key, val)

    return str1

import json


def load_metadata(filepath: str) -> dict:
    """Загрузка данных из файла

    Args:
        filepath (str): путь к файлу

    Returns:
        dict: database в формате dict
    """
    try:
        with open(filepath, 'r') as f:
            db_dict = json.load(f)
    except FileNotFoundError:
        db_dict = {}
    return db_dict


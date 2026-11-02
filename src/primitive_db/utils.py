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


def save_metadata(filepath: str, data: dict) -> None:
    """Загрузка данных в файл

    Args:
        filepath (str): путь к файлу
        data (dict): database
    """
    with open(filepath, 'w') as f:
        json.dump(data, f)

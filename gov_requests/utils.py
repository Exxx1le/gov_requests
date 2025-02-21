import requests
from docx import Document  # Для создания DOC-файла

# URL для запроса документов
API_URL = "http://publication.pravo.gov.ru/api/Documents"

def fetch_documents_by_date_and_authority(date, authority_id):
    """
    Функция для получения документов за указанную дату и для указанного государственного органа.

    :param date: Дата в формате DD.MM.YYYY
    :param authority_id: GUID государственного органа
    :return: Список найденных документов
    """
    params = {
        "periodType": "day",
        "date": date,
        "SignatoryAuthorityId": authority_id,
        "PageSize": 200,  # Количество документов на страницу
        "Index": 1,       # Номер страницы
        "SortedBy": 0,    # Сортировка по дате подписания
        "SortDestination": "asc"  # По возрастанию
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Проверяем статус ответа
        data = response.json()

        # Возвращаем список документов
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []

def save_to_doc(documents, output_filename="documents.docx"):
    """
    Сохраняет список документов в файл .docx с ссылками на каждый документ.

    :param documents: Список документов, полученный из API
    :param output_filename: Имя выходного файла
    """
    doc = Document()  # Создаем новый документ

    for doc_info in documents:
        eo_number = doc_info.get("eoNumber", "N/A")
        document_name = doc_info.get("complexName", "Название не указано")
        document_date = doc_info.get("documentDate", "Дата не указана")

        # Добавляем название документа
        doc.add_paragraph(f"{document_name} ({document_date})")

        # Добавляем ссылку на документ
        link = f"http://publication.pravo.gov.ru/document/{eo_number}"
        doc.add_paragraph(f"Ссылка: {link}")

        # Добавляем пустую строку между документами
        doc.add_paragraph("")

    # Сохраняем документ
    doc.save(output_filename)
    print(f"Документы успешно сохранены в файл: {output_filename}")
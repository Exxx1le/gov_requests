import requests
from datetime import timedelta
from docx import Document  # Для создания DOC-файла
import os
from pathlib import Path
import docx

# URL для запроса документов
API_URL = "http://publication.pravo.gov.ru/api/Documents"

def fetch_documents_by_date(date, authority_id):
    """
    Функция для получения документов за указанную дату и для указанного государственного органа.

    :param date: Дата в формате DD.MM.YYYY
    :param authority_id: GUID государственного органа
    :return: Список найденных документов
    """
    params = {
        "periodType": "day",
        "date": date,
        "SignatoryAuthorityId": authority_id
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Фильтруем результаты для Правительства РФ
        if authority_id == "8005d8c9-4b6d-48d3-861a-2a37e69fccb3":
            return [
                doc for doc in data.get("items", [])
                if doc.get("documentTypeId") == "fd5a8766-f6fd-4ac2-8fd9-66f414d314ac"
            ]
        
        # Для остальных органов возвращаем все документы
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса для даты {date}: {e}")
        return []

def add_hyperlink(paragraph, text, url):
    """
    Добавляет кликабельную гиперссылку в параграф.
    
    :param paragraph: Параграф документа
    :param text: Отображаемый текст
    :param url: URL для перехода
    """
    # Получаем связь с word документом
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    
    # Создаем гиперссылку
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id)
    
    # Создаем элемент run
    new_run = docx.oxml.shared.OxmlElement('w:r')
    rPr = docx.oxml.shared.OxmlElement('w:rPr')
    
    # Добавляем стиль для гиперссылки
    rStyle = docx.oxml.shared.OxmlElement('w:rStyle')
    rStyle.set(docx.oxml.shared.qn('w:val'), 'Hyperlink')
    rPr.append(rStyle)
    
    # Добавляем текст
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    
    paragraph._p.append(hyperlink)
    return hyperlink

def save_to_doc(documents_by_authority, output_filename="documents.docx"):
    """
    Сохраняет список документов в файл .docx, группируя их по органам власти
    """
    home_dir = str(Path.home())
    output_path = os.path.join(home_dir, output_filename)
    
    doc = Document()

    for authority_name, documents in documents_by_authority.items():
        # Добавляем название органа власти как заголовок
        heading = doc.add_heading(authority_name, level=1)
        
        for doc_info in documents:
            eo_number = doc_info.get("eoNumber", "N/A")
            document_name = doc_info.get("complexName", "Название не указано")
            document_date = doc_info.get("documentDate", "Дата не указана")

            # Добавляем название документа
            doc.add_paragraph(f"{document_name} ({document_date})")

            # Создаем параграф для ссылки
            p = doc.add_paragraph()
            link = f"http://publication.pravo.gov.ru/document/{eo_number}"
            add_hyperlink(p, f"Ссылка на документ", link)

            # Добавляем пустую строку между документами
            doc.add_paragraph("")
        
        # Добавляем разделитель между органами власти
        doc.add_page_break()

    doc.save(output_path)
    print(f"Документы успешно сохранены в файл: {output_path}")

def generate_date_range(start_date, end_date):
    """
    Генерирует список дат между начальной и конечной датами (включительно).

    :param start_date: Начальная дата
    :param end_date: Конечная дата
    :return: Список дат в формате DD.MM.YYYY
    """
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%d.%m.%Y"))
        current_date += timedelta(days=1)
    return dates

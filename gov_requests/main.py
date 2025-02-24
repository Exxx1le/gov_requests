from collections import defaultdict
from datetime import timedelta
from utils import fetch_documents_by_date, generate_date_range, save_to_doc
from constants import AUTHORITY_ID


def main(start_date, end_date):
    """
    Основная функция для получения и обработки документов.
    
    :param start_date: datetime.date объект с начальной датой
    :param end_date: datetime.date объект с конечной датой
    """
    current_date = start_date
    all_documents_by_authority = {}

    while current_date <= end_date:
        formatted_date = current_date.strftime("%d.%m.%Y")
        
        for authority_id in AUTHORITY_ID:
            documents = fetch_documents_by_date(formatted_date, authority_id)
            if documents:
                if authority_id not in all_documents_by_authority:
                    all_documents_by_authority[authority_id] = []
                all_documents_by_authority[authority_id].extend(documents)
            
        current_date += timedelta(days=1)

    save_to_doc(all_documents_by_authority, "output_documents.docx")

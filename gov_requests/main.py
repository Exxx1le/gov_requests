from datetime import datetime
from utils import fetch_documents_by_date, generate_date_range, save_to_doc
from constants import AUTHORITY_ID


def main():
    # Пример использования
    start_date_str = input("Введите начальную дату (YYYY-MM-DD): ")
    end_date_str = input("Введите конечную дату (YYYY-MM-DD): ")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Неверный формат даты. Используйте формат YYYY-MM-DD.")
        return

    if start_date > end_date:
        print("Начальная дата не может быть позже конечной даты.")
        return

    # Генерируем список дат
    date_range = generate_date_range(start_date, end_date)

    # Собираем все документы за указанный период по каждому органу власти
    all_documents_by_authority = {}  # Словарь для хранения документов по органам
    for authority_name, guid in AUTHORITY_ID.items():
        print(f"\nОбработка документов для: {authority_name}")
        
        authority_documents = []  # Список для документов текущего органа
        for date in date_range:
            print(f"Запрос документов за {date}...")
            documents = fetch_documents_by_date(date, guid)
            if documents:
                authority_documents.extend(documents)
            
        if authority_documents:
            all_documents_by_authority[authority_name] = authority_documents
        print(f"Обработка {authority_name} завершена")

    # Итоговая статистика и сохранение
    total_docs = sum(len(docs) for docs in all_documents_by_authority.values())
    if total_docs > 0:
        print(f"\nОбщее количество найденных документов: {total_docs}")
        save_to_doc(all_documents_by_authority, "output_documents.docx")
    else:
        print("\nДокументы не найдены.")

if __name__ == "__main__":
    main()
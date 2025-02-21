from datetime import datetime
from utils import fetch_documents_by_date_and_authority, save_to_doc


def main():
    # Пример использования
    date_str = input("Введите дату (DD.MM.YYYY): ")

    try:
        date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        print("Неверный формат даты. Используйте формат DD.MM.YYYY.")
        return

    # GUID государственного органа (замените на актуальный)
    authority_id = "8005d8c9-4b6d-48d3-861a-2a37e69fccb3"  # Правительство РФ

    # Получаем документы
    documents = fetch_documents_by_date_and_authority(date_str, authority_id)

    if documents:
        print(f"Найдено документов: {len(documents)}")
        # Сохраняем документы в файл
        save_to_doc(documents, "output_documents.docx")
    else:
        print("Документы не найдены.")

if __name__ == "__main__":
    main()
from datetime import datetime
from utils import fetch_documents_by_date, generate_date_range, save_to_doc

# GUID государственного органа (замените на актуальный)
authority_id = {"Правительство РФ":"8005d8c9-4b6d-48d3-861a-2a37e69fccb3",
                "Президент Российской Федерации":"225698f1-cfbc-4e42-9caa-32f9f7403211",
                "Министерство цифрового развития, связи и массовых коммуникаций Российской Федерации":"1ac1ee36-2621-4c4f-917f-9bffc35d4671",
                "Федеральная служба по надзору в сфере связи, информационных технологий и массовых коммуникаций":"bc7a65a3-80ef-4c88-8214-3ec5b29f9997"
                }

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
    all_documents = []
    for authority_name, guid in authority_id.items():
        print(f"\nОбработка документов для: {authority_name}")
        
        for date in date_range:
            print(f"Запрос документов за {date}...")
            # Передаем только GUID вместо словаря с названием органа
            documents = fetch_documents_by_date(date, guid)
            if documents:
                all_documents.extend(documents)
            
        print(f"Обработка {authority_name} завершена")

    # Итоговая статистика и сохранение
    if all_documents:
        print(f"\nОбщее количество найденных документов: {len(all_documents)}")
        save_to_doc(all_documents, "output_documents.docx")
    else:
        print("\nДокументы не найдены.")

if __name__ == "__main__":
    main()
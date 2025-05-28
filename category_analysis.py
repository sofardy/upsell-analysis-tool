import pandas as pd
from collections import defaultdict
import csv

def get_product_category(product_name):
    """Определяет категорию товара по его названию"""
    if 'Кольє' in product_name:
        return 'Колье'
    elif 'Сережки' in product_name:
        return 'Серьги'
    elif 'Браслет' in product_name:
        return 'Браслет'
    elif 'Каблучка' in product_name:
        return 'Кольцо'
    elif 'Кафф' in product_name:
        return 'Кафф'
    elif 'Анклет' in product_name:
        return 'Анклет'
    elif 'Чокер' in product_name:
        return 'Чокер'
    else:
        return 'Другое'

def analyze_category_upsells():
    # Читаем CSV файл
    df = pd.read_csv('products.csv')
    
    # Группируем по номеру заказа
    orders = df.groupby('№ заказа')
    
    # Словарь для хранения статистики по категориям
    category_stats = defaultdict(lambda: defaultdict(int))
    
    # Словарь для подсчета общего количества проданных товаров по категориям
    main_category_counts = defaultdict(int)
    
    print("Анализирую заказы по категориям...")
    
    # Сначала подсчитываем общее количество проданных товаров по категориям
    for order_id, order_data in orders:
        main_products = order_data[order_data['Допродажа'].isna() | (order_data['Допродажа'] == '')]
        
        for _, main_product in main_products.iterrows():
            main_product_name = main_product['Товары']
            
            # Пропускаем коробки и упаковки
            if 'Коробка' in main_product_name or 'Пакет' in main_product_name:
                continue
                
            main_category = get_product_category(main_product_name)
            main_category_counts[main_category] += 1
    
    # Теперь анализируем допродажи
    for order_id, order_data in orders:
        # Разделяем товары на основные и допродажи
        main_products = order_data[order_data['Допродажа'].isna() | (order_data['Допродажа'] == '')]
        upsell_products = order_data[order_data['Допродажа'] == 'Допродажа']
        
        # Если в заказе есть допродажи
        if not upsell_products.empty:
            for _, main_product in main_products.iterrows():
                main_product_name = main_product['Товары']
                
                # Пропускаем коробки и упаковки
                if 'Коробка' in main_product_name or 'Пакет' in main_product_name:
                    continue
                
                main_category = get_product_category(main_product_name)
                
                # Подсчитываем допродажи по категориям
                for _, upsell_product in upsell_products.iterrows():
                    upsell_name = upsell_product['Товары']
                    
                    # Пропускаем коробки и пакеты в допродажах
                    if 'Коробка' in upsell_name or 'Пакет' in upsell_name:
                        continue
                        
                    upsell_category = get_product_category(upsell_name)
                    category_stats[main_category][upsell_category] += 1
    
    # Создаем результирующий CSV
    with open('category_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Получаем все уникальные категории
        all_categories = set()
        for main_stats in category_stats.values():
            all_categories.update(main_stats.keys())
        all_categories = sorted(list(all_categories))
        
        # Записываем заголовки
        headers = ['Основная категория', 'Количество продаж'] + [f'{cat} (кол-во)' for cat in all_categories] + [f'{cat} (%)' for cat in all_categories]
        writer.writerow(headers)
        
        # Записываем данные по каждой основной категории
        for main_category, upsell_stats in sorted(category_stats.items()):
            row = [main_category, main_category_counts[main_category]]
            
            # Добавляем количество допродаж
            for category in all_categories:
                row.append(upsell_stats[category])
            
            # Добавляем проценты
            total_main_sales = main_category_counts[main_category]
            for category in all_categories:
                if total_main_sales > 0:
                    percentage = round((upsell_stats[category] / total_main_sales) * 100, 1)
                else:
                    percentage = 0
                row.append(f"{percentage}%")
            
            writer.writerow(row)
            
            # Выводим в консоль
            print(f"\nОсновная категория: {main_category} (продано: {total_main_sales})")
            for category, count in sorted(upsell_stats.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    percentage = round((count / total_main_sales) * 100, 1) if total_main_sales > 0 else 0
                    print(f"  - {category}: {count} допродаж ({percentage}%)")
    
    print(f"\nОбщая статистика по основным категориям:")
    for category, count in sorted(main_category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count} товаров продано")
    
    print(f"\nРезультаты сохранены в файл 'category_analysis.csv'")

if __name__ == "__main__":
    analyze_category_upsells()

import pandas as pd
from collections import defaultdict
import csv

def analyze_upsells():
    # Читаем CSV файл
    df = pd.read_csv('products.csv')
    
    # Группируем по номеру заказа
    orders = df.groupby('№ заказа')
    
    # Словарь для подсчета допродаж к каждому товару
    upsell_stats = defaultdict(int)
    
    # Словарь для сбора детальной информации
    detailed_stats = defaultdict(list)
    
    orders_with_upsells = 0
    total_orders = 0
    
    print("Анализирую заказы...")
    
    for order_id, order_data in orders:
        total_orders += 1
        
        # Разделяем товары на основные (без допродажи) и допродажи
        main_products = order_data[order_data['Допродажа'].isna() | (order_data['Допродажа'] == '')]
        upsell_products = order_data[order_data['Допродажа'] == 'Допродажа']
        
        # Если в заказе есть допродажи
        if not upsell_products.empty:
            orders_with_upsells += 1
            
            # Для каждого основного товара увеличиваем счетчик допродаж
            for _, main_product in main_products.iterrows():
                main_product_name = main_product['Товары']
                
                # Пропускаем коробки и упаковки
                if 'Коробка' in main_product_name or 'Пакет' in main_product_name:
                    continue
                
                upsell_stats[main_product_name] += 1
                
                # Сохраняем детальную информацию
                upsell_items = [item['Товары'] for _, item in upsell_products.iterrows()]
                detailed_stats[main_product_name].extend(upsell_items)
                
                print(f"Заказ {order_id}: к '{main_product_name}' добавили {len(upsell_products)} допродаж")
    
    print(f"\nВсего заказов: {total_orders}")
    print(f"Заказов с допродажами: {orders_with_upsells}")
    
    # Сортируем по количеству допродаж
    sorted_stats = sorted(upsell_stats.items(), key=lambda x: x[1], reverse=True)
    
    # Создаем результирующий CSV
    with open('upsell_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Основной товар', 'Количество допродаж', 'Примеры допродаж'])
        
        for product, count in sorted_stats:
            # Берем уникальные примеры допродаж для этого товара
            examples = list(set(detailed_stats[product]))[:5]  # Первые 5 уникальных примеров
            examples_str = '; '.join(examples)
            
            writer.writerow([product, count, examples_str])
    
    print(f"\nТоп-10 товаров с наибольшим количеством допродаж:")
    for i, (product, count) in enumerate(sorted_stats[:10], 1):
        print(f"{i}. {product}: {count} допродаж")
    
    print(f"\nРезультаты сохранены в файл 'upsell_analysis.csv'")

if __name__ == "__main__":
    analyze_upsells()
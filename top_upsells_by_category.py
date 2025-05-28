import csv
import sys
from collections import defaultdict

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

def analyze_top_upsells_by_category(top_n=10):
    """
    Анализирует топ допродаваемых товаров по категориям
    
    Args:
        top_n (int): Количество топ товаров для показа в каждой категории (по умолчанию 10)
    """
    # Читаем CSV файл
    orders = {}
    with open('products.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            order_id = row['№ заказа']
            if order_id not in orders:
                orders[order_id] = []
            orders[order_id].append(row)
    
    # Словари для статистики
    category_upsells = defaultdict(lambda: defaultdict(int))  # category -> {product: count}
    total_category_upsells = defaultdict(int)  # category -> total_count
    total_orders_with_upsells = 0
    
    print("Анализирую топ допродаваемых товаров по категориям...")
    print(f"Загружено {len(orders)} заказов")
    
    # Анализируем каждый заказ
    for order_id, order_data in orders.items():
        # Разделяем товары на основные и допродажи
        main_products = []
        upsells = []
        
        for item in order_data:
            doprodazha = item.get('Допродажа', '')
            if doprodazha == 'Допродажа':
                upsells.append(item)
            else:
                main_products.append(item)
        
        # Если есть допродажи в заказе
        if upsells:
            has_main_products = False
            
            # Проверяем, есть ли основные товары (исключая упаковку)
            for main_product in main_products:
                main_product_name = main_product['Товары']
                if not ('Коробка' in main_product_name or 'Пакет' in main_product_name):
                    has_main_products = True
                    break
            
            # Если есть основные товары, считаем допродажи
            if has_main_products:
                total_orders_with_upsells += 1
                
                for upsell_product in upsells:
                    upsell_name = upsell_product['Товары']
                    
                    # Пропускаем упаковку в допродажах
                    if 'Коробка' in upsell_name or 'Пакет' in upsell_name:
                        continue
                    
                    upsell_category = get_product_category(upsell_name)
                    category_upsells[upsell_category][upsell_name] += 1
                    total_category_upsells[upsell_category] += 1
    
    # Создаем результирующий CSV
    with open('top_upsells_by_category.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Записываем заголовки
        headers = ['Категория', 'Ранг', 'Товар', 'Количество допродаж', 'Доля в категории (%)', 'Доля от всех допродаж (%)']
        writer.writerow(headers)
        
        # Подсчитываем общее количество допродаж
        total_all_upsells = sum(total_category_upsells.values())
        
        # Сортируем категории по общему количеству допродаж
        sorted_categories = sorted(total_category_upsells.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nОбщая статистика:")
        print(f"Заказов с допродажами: {total_orders_with_upsells}")
        print(f"Всего допродаж: {total_all_upsells}")
        
        # Для каждой категории выводим топ товаров
        for category, total_count in sorted_categories:
            print(f"\n📦 Категория: {category} (всего допродаж: {total_count})")
            
            # Сортируем товары в категории по количеству допродаж
            sorted_products = sorted(category_upsells[category].items(), key=lambda x: x[1], reverse=True)
            
            # Выводим топ N товаров
            for rank, (product_name, count) in enumerate(sorted_products[:top_n], 1):
                category_percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0
                total_percentage = round((count / total_all_upsells) * 100, 1) if total_all_upsells > 0 else 0
                
                # Записываем в CSV
                writer.writerow([category, rank, product_name, count, f"{category_percentage}%", f"{total_percentage}%"])
                
                # Выводим в консоль (только топ-5 для читаемости)
                if rank <= 5:
                    print(f"  {rank}. {product_name}: {count} допродаж ({category_percentage}% в категории)")
            
            # Если товаров больше 5, показываем это
            if len(sorted_products) > 5:
                print(f"  ... и ещё {len(sorted_products) - 5} товаров")
    
    # Выводим общую статистику по категориям
    print(f"\n📊 Рейтинг категорий по количеству допродаж:")
    for rank, (category, count) in enumerate(sorted_categories, 1):
        percentage = round((count / total_all_upsells) * 100, 1) if total_all_upsells > 0 else 0
        unique_products = len(category_upsells[category])
        print(f"  {rank}. {category}: {count} допродаж ({percentage}%, {unique_products} уникальных товаров)")
    
    print(f"\nРезультаты сохранены в файл 'top_upsells_by_category.csv'")

if __name__ == "__main__":
    # Обработка аргументов командной строки
    top_n = 10
    
    if len(sys.argv) > 1:
        try:
            top_n = int(sys.argv[1])
            if top_n < 1:
                print("Ошибка: количество товаров должно быть больше 0")
                sys.exit(1)
        except ValueError:
            print("Ошибка: аргумент должен быть числом (количество топ товаров в каждой категории)")
            sys.exit(1)
    
    print(f"Анализируются топ-{top_n} товаров в каждой категории")
    analyze_top_upsells_by_category(top_n)

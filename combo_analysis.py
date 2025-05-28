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

def analyze_combo_upsells(min_combo_size=2, max_combo_size=None):
    """
    Анализирует комбинации категорий товаров
    
    Args:
        min_combo_size (int): Минимальный размер комбинации (по умолчанию 2)
        max_combo_size (int): Максимальный размер комбинации (по умолчанию без ограничений)
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
    
    # Словарь для хранения статистики по комбинациям категорий
    combo_stats = defaultdict(lambda: defaultdict(int))
    
    # Словарь для подсчета общего количества комбинаций
    combo_counts = defaultdict(int)
    
    print("Анализирую заказы с комбинациями категорий...")
    print(f"Загружено {len(orders)} заказов")
    
    # Сначала подсчитываем все комбинации основных товаров
    for order_id, order_data in orders.items():
        main_products = []
        upsells = []
        
        for item in order_data:
            doprodazha = item.get('Допродажа', '')
            if doprodazha == 'Допродажа':
                upsells.append(item)
            else:
                main_products.append(item)
        
        # Получаем категории основных товаров в заказе
        main_categories = []
        for main_product in main_products:
            main_product_name = main_product['Товары']
            
            # Пропускаем коробки и упаковки
            if 'Коробка' in main_product_name or 'Пакет' in main_product_name:
                continue
                
            category = get_product_category(main_product_name)
            main_categories.append(category)
        
        # Создаем комбинации заданного размера
        unique_categories = list(set(main_categories))
        if len(unique_categories) >= min_combo_size:
            # Генерируем комбинации разных размеров
            from itertools import combinations
            
            # Определяем максимальный размер комбинации
            actual_max_size = max_combo_size if max_combo_size else len(unique_categories)
            actual_max_size = min(actual_max_size, len(unique_categories))
            
            for combo_size in range(min_combo_size, actual_max_size + 1):
                for combo_tuple in combinations(unique_categories, combo_size):
                    combo = tuple(sorted(combo_tuple))
                    combo_counts[combo] += 1
                    
                    # Если есть допродажи, подсчитываем их
                    if upsells:
                        for upsell_product in upsells:
                            upsell_name = upsell_product['Товары']
                            
                            # Пропускаем коробки и пакеты в допродажах
                            if 'Коробка' in upsell_name or 'Пакет' in upsell_name:
                                continue
                                
                            upsell_category = get_product_category(upsell_name)
                            combo_stats[combo][upsell_category] += 1
    
    # Создаем результирующий CSV
    with open('combo_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Получаем все уникальные категории допродаж
        all_upsell_categories = set()
        for combo_data in combo_stats.values():
            all_upsell_categories.update(combo_data.keys())
        all_upsell_categories = sorted(list(all_upsell_categories))
        
        # Записываем заголовки
        headers = ['Комбинация категорий', 'Количество заказов'] + [f'{cat} (кол-во)' for cat in all_upsell_categories] + [f'{cat} (%)' for cat in all_upsell_categories]
        writer.writerow(headers)
        
        # Записываем данные по каждой комбинации
        for combo, upsell_stats in sorted(combo_stats.items(), key=lambda x: combo_counts[x[0]], reverse=True):
            combo_str = " + ".join(combo)  # Используем join для комбинаций любого размера
            combo_count = combo_counts[combo]
            
            row = [combo_str, combo_count]
            
            # Добавляем количество допродаж
            for category in all_upsell_categories:
                row.append(upsell_stats[category])
            
            # Добавляем проценты
            for category in all_upsell_categories:
                if combo_count > 0:
                    percentage = round((upsell_stats[category] / combo_count) * 100, 1)
                else:
                    percentage = 0
                row.append(f"{percentage}%")
            
            writer.writerow(row)
            
    
    print(f"\nНайдено {len(combo_counts)} уникальных комбинаций категорий")
    print(f"Из них {len(combo_stats)} комбинаций имеют допродажи")
    
    # Статистика по размерам комбинаций
    combo_sizes = defaultdict(int)
    for combo in combo_counts.keys():
        combo_sizes[len(combo)] += 1
    
    print(f"\nРаспределение по размерам комбинаций:")
    for size in sorted(combo_sizes.keys()):
        print(f"  - {size} категории: {combo_sizes[size]} комбинаций")
    
    # Выводим топ-10 комбинаций с допродажами
    print(f"\nТоп комбинации с допродажами:")
    combo_items = list(combo_stats.items())
    combo_items.sort(key=lambda x: combo_counts[x[0]], reverse=True)
    
    for i, (combo, upsell_stats) in enumerate(combo_items[:10]):
        combo_str = " + ".join(combo)  # Универсальный join для любого размера комбинации
        combo_count = combo_counts[combo]
        print(f"\n{i+1}. {combo_str} (заказов: {combo_count})")
        
        for category, count in sorted(upsell_stats.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = round((count / combo_count) * 100, 1) if combo_count > 0 else 0
                print(f"   - {category}: {count} допродаж ({percentage}%)")
    
    print(f"\nОбщая статистика по комбинациям (топ-10):")
    top_combos = sorted(combo_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for combo, count in top_combos:
        combo_str = " + ".join(combo)  # Универсальный join
        print(f"  - {combo_str}: {count} заказов")
    
    print(f"\nРезультаты сохранены в файл 'combo_analysis.csv'")

if __name__ == "__main__":
    # Обработка аргументов командной строки
    min_size = 2
    max_size = None
    
    if len(sys.argv) > 1:
        try:
            min_size = int(sys.argv[1])
        except ValueError:
            print("Ошибка: первый аргумент должен быть числом (минимальный размер комбинации)")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            max_size = int(sys.argv[2])
        except ValueError:
            print("Ошибка: второй аргумент должен быть числом (максимальный размер комбинации)")
            sys.exit(1)
    
    # Проверяем корректность параметров
    if min_size < 2:
        print("Ошибка: минимальный размер комбинации должен быть не менее 2")
        sys.exit(1)
    
    if max_size and max_size < min_size:
        print("Ошибка: максимальный размер не может быть меньше минимального")
        sys.exit(1)
    
    # Выводим информацию о параметрах
    if max_size:
        print(f"Анализируются комбинации от {min_size} до {max_size} категорий")
    else:
        print(f"Анализируются комбинации от {min_size} категорий и выше")
    
    analyze_combo_upsells(min_size, max_size)

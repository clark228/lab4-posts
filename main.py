import os
import csv
from typing import List, Iterator, Any


# =====================================================
# Базовый класс для демонстрации наследования
# =====================================================
class BaseEntity:
    """Базовый класс для всех сущностей (демонстрация наследования)"""

    @staticmethod
    def get_csv_fieldnames():
        """Статический метод — должен быть переопределён в дочернем классе"""
        raise NotImplementedError

    @staticmethod
    def validate_data(data):
        """Статический метод для валидации данных"""
        return True


# =====================================================
# Основной класс Post (Пост)
# =====================================================
class Post(BaseEntity):
    """Класс, представляющий пост"""

    # Статическое поле для хранения всех созданных экземпляров
    _instances = []

    def __init__(self, post_id: int, author: str, text: str, likes: int):
        self._id = post_id
        self._author = author
        self._text = text
        self._likes = likes
        Post._instances.append(self)

    # ========== Свойства с контролем через __setattr__ ==========
    def __setattr__(self, name, value):
        """
        Перегрузка __setattr__ — запись значений только через этот метод
        """
        if name == '_id' and hasattr(self, '_id'):
            raise AttributeError("ID поста нельзя изменить")
        if name == '_likes' and value < 0:
            raise ValueError("Количество лайков не может быть отрицательным")
        super().__setattr__(name, value)

    # Геттеры для свойств (опционально, для удобства)
    @property
    def id(self):
        return self._id

    @property
    def author(self):
        return self._author

    @property
    def text(self):
        return self._text

    @property
    def likes(self):
        return self._likes

    # ========== Перегрузка repr ==========
    def __repr__(self) -> str:
        """Перегрузка repr — пункт 2"""
        text_preview = self._text[:50] + "..." if len(self._text) > 50 else self._text
        return f"Post(id={self._id}, author='{self._author}', likes={self._likes}, text='{text_preview}')"

    def __str__(self) -> str:
        text_preview = self._text[:50] + "..." if len(self._text) > 50 else self._text
        return f"#{self._id} | {self._author} | лайков {self._likes} | {text_preview}"

    # ========== Статические методы ==========
    @staticmethod
    def get_csv_fieldnames():
        """Статический метод — возвращает имена полей для CSV"""
        return ['№', 'ник автора', 'текст поста', 'количество лайков']

    @staticmethod
    def from_csv_row(row):
        """Статический метод — создаёт объект Post из строки CSV"""
        return Post(
            post_id=int(row['№']),
            author=row['ник автора'],
            text=row['текст поста'],
            likes=int(row['количество лайков'])
        )

    @staticmethod
    def validate_data(data):
        """Статический метод для валидации данных перед сохранением"""
        if data.get('likes', 0) < 0:
            return False
        if not data.get('author', '').strip():
            return False
        return True

    # ========== Генератор ==========
    @classmethod
    def generate_posts(cls, count: int):
        """
        Генератор постов — демонстрация генераторов (пункт 7)
        Генерирует тестовые посты без создания файлов
        """
        authors = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
        texts = [
            "Сегодня отличный день!",
            "Программирование — это весело",
            "Лабораторная работа готова!",
            "Python — лучший язык",
            "Ура, выходные!"
        ]
        for i in range(count):
            author = authors[i % len(authors)]
            text = texts[i % len(texts)] + f" (пост №{i + 1})"
            likes = (i * 10) % 100
            yield Post(post_id=i + 1, author=author, text=text, likes=likes)

    # ========== Итератор для коллекции постов ==========
    @classmethod
    def get_posts_iterator(cls):
        """Возвращает итератор по всем созданным постам"""
        return iter(cls._instances)


# =====================================================
# Класс-коллекция для управления постами (реализует __getitem__)
# =====================================================
class PostCollection:
    """
    Коллекция постов с поддержкой доступа по индексу (__getitem__)
    """

    def __init__(self, posts: List[Post] = None):
        self._posts = posts if posts else []

    def add(self, post: Post):
        self._posts.append(post)

    def __getitem__(self, index):
        """
        Доступ к элементам коллекции по индексу — пункт 5
        """
        if isinstance(index, slice):
            return PostCollection(self._posts[index])
        if not isinstance(index, int):
            raise TypeError("Индекс должен быть целым числом")
        if index < 0 or index >= len(self._posts):
            raise IndexError("Индекс вне диапазона")
        return self._posts[index]

    def __len__(self):
        return len(self._posts)

    def __iter__(self):
        return iter(self._posts)

    def sort_by_author(self):
        """Сортировка по строковому полю"""
        self._posts = sorted(self._posts, key=lambda p: p.author)
        return self

    def sort_by_likes(self):
        """Сортировка по числовому полю"""
        self._posts = sorted(self._posts, key=lambda p: p.likes)
        return self

    def filter_by_likes(self, threshold: int) -> List[Post]:
        """Фильтрация по лайкам"""
        return [p for p in self._posts if p.likes > threshold]

    def to_dict_list(self):
        """Преобразование в список словарей для сохранения в CSV"""
        return [
            {'№': p.id, 'ник автора': p.author, 'текст поста': p.text, 'количество лайков': p.likes}
            for p in self._posts
        ]


# =====================================================
# Класс для работы с файлами
# =====================================================
class PostFileManager:
    """Класс для загрузки и сохранения постов в CSV"""

    @staticmethod
    def count_files_in_directory(path: str = ".") -> int:
        """Статический метод — подсчёт файлов в директории"""
        if not os.path.exists(path):
            print(f"Директория {path} не найдена")
            return 0
        count = 0
        for _, _, files in os.walk(path):
            count += len(files)
        return count

    @classmethod
    def load_from_csv(cls, filename: str) -> PostCollection:
        """Загрузка постов из CSV файла"""
        posts = []
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                post = Post.from_csv_row(row)
                posts.append(post)
        return PostCollection(posts)

    @classmethod
    def save_to_csv(cls, filename: str, collection: PostCollection):
        """Сохранение коллекции постов в CSV"""
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=Post.get_csv_fieldnames())
            writer.writeheader()
            writer.writerows(collection.to_dict_list())


# =====================================================
# Демонстрация работы всех возможностей
# =====================================================

def main():
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №4 — КЛАССЫ (ВАРИАНТ 11 — ПОСТЫ)")
    print("=" * 60)

    # ----- 1. Подсчёт файлов в директории (статические методы) -----
    print("\n1. ПОДСЧЁТ ФАЙЛОВ В ДИРЕКТОРИИ:")
    dir_path = input("Введите путь к папке (Enter для текущей): ").strip()
    if not dir_path:
        dir_path = "."
    file_count = PostFileManager.count_files_in_directory(dir_path)
    print(f"   Количество файлов в '{dir_path}': {file_count}")

    # ----- Загрузка данных из CSV -----
    csv_file = "data_posts.csv"

    # Если файл не существует — создаём тестовые данные через генератор
    if not os.path.exists(csv_file):
        print(f"\n   Файл {csv_file} не найден. Создаём тестовые данные...")
        gen = Post.generate_posts(10)  # Генератор — пункт 7
        test_collection = PostCollection(list(gen))
        PostFileManager.save_to_csv(csv_file, test_collection)
        print(f"   Создан файл {csv_file} с 10 тестовыми постами")

    # Загружаем коллекцию
    collection = PostFileManager.load_from_csv(csv_file)
    print(f"\n   Загружено постов: {len(collection)}")

    # ----- Вывод исходных данных -----
    print("\n0. ИСХОДНЫЕ ДАННЫЕ (первые 5 постов):")
    for i, post in enumerate(collection[:5]):
        print(f"   {i + 1}. {post}")

    # ----- 2.1 Сортировка по строковому полю (ник автора) -----
    print("\n2.1 СОРТИРОВКА ПО СТРОКОВОМУ ПОЛЮ (НИК АВТОРА):")
    sorted_by_author = PostCollection(collection[:])  # копия через __getitem__ с slice
    sorted_by_author.sort_by_author()
    for i, post in enumerate(sorted_by_author[:5]):  # выводим первые 5
        print(f"   {i + 1}. {post.author} — лайков {post.likes} — {post.text[:30]}...")

    # ----- 2.2 Сортировка по числовому полю (лайки) -----
    print("\n2.2 СОРТИРОВКА ПО ЧИСЛОВОМУ ПОЛЮ (КОЛИЧЕСТВО ЛАЙКОВ):")
    sorted_by_likes = PostCollection(collection[:])
    sorted_by_likes.sort_by_likes()
    for i, post in enumerate(sorted_by_likes[:5]):
        print(f"   {i + 1}. лайков {post.likes} — {post.author}")

    # ----- 2.3 Фильтрация по критерию (лайки > N) -----
    print("\n2.3 ФИЛЬТРАЦИЯ ПО КРИТЕРИЮ (ЛАЙКИ > N):")
    try:
        threshold = int(input("   Введите порог лайков: "))
        filtered = collection.filter_by_likes(threshold)
        print(f"   Посты с лайками > {threshold}: {len(filtered)} шт.")
        for post in filtered[:5]:
            print(f"   - {post}")
    except ValueError:
        print("   Неверный ввод")

    # ----- 3. Сохранение новых данных -----
    print("\n3. ДОБАВЛЕНИЕ НОВОГО ПОСТА И СОХРАНЕНИЕ:")
    answer = input("   Хотите добавить новый пост? (да/нет): ").lower()
    if answer == "да":
        new_id = max([p.id for p in collection]) + 1 if len(collection) > 0 else 1
        author = input("   Ник автора: ")
        text = input("   Текст поста: ")
        try:
            likes = int(input("   Количество лайков: "))
            new_post = Post(new_id, author, text, likes)
            collection.add(new_post)
            PostFileManager.save_to_csv(csv_file, collection)
            print(f"    Пост добавлен и сохранён в {csv_file}")
        except ValueError as e:
            print(f"    Ошибка: {e}")

    # ----- Демонстрация работы __getitem__ -----
    print("\n4. ДЕМОНСТРАЦИЯ ДОСТУПА ПО ИНДЕКСУ (__getitem__):")
    print(f"   Первый пост: {collection[0]}")
    if len(collection) > 1:
        print(f"   Последний пост: {collection[-1]}")
    if len(collection) >= 5:
        print(f"   Срез [2:5]: {len(collection[2:5])} постов")

    # ----- Демонстрация итератора -----
    print("\n5. ДЕМОНСТРАЦИЯ ИТЕРАТОРА (из класса Post):")
    it = Post.get_posts_iterator()
    print("   Первые 3 поста из глобального итератора:")
    for i in range(min(3, len(Post._instances))):
        try:
            print(f"   - {next(it)}")
        except StopIteration:
            break

    # ----- Демонстрация repr -----
    print("\n6. ДЕМОНСТРАЦИЯ __repr__:")
    example_post = Post(999, "Demo", "Пример текста поста для демонстрации repr", 42)
    print(f"   repr(post): {repr(example_post)}")

    # ----- Демонстрация статического метода валидации -----
    print("\n7. ДЕМОНСТРАЦИЯ СТАТИЧЕСКОГО МЕТОДА validate_data:")
    valid_data = {'likes': 100, 'author': 'John'}
    invalid_data = {'likes': -5, 'author': ''}
    print(f"   Валидные данные: {Post.validate_data(valid_data)}")
    print(f"   Невалидные данные: {Post.validate_data(invalid_data)}")

    # ----- Демонстрация генератора -----
    print("\n8. ДЕМОНСТРАЦИЯ ГЕНЕРАТОРА (generate_posts):")
    gen = Post.generate_posts(5)
    print("   Сгенерированные посты:")
    for post in gen:
        print(f"   - {post}")

    # ----- Демонстрация __setattr__ -----
    print("\n9. ДЕМОНСТРАЦИЯ __setattr__ (защита от изменения ID):")
    test_post = Post(100, "Tester", "Тестовый пост", 10)
    print(f"   До попытки изменения: id={test_post.id}")
    try:
        test_post._id = 999  # Это вызовет исключение
    except AttributeError as e:
        print(f"    Попытка изменить ID: {e}")

    print("\n" + "=" * 60)
    print("РАБОТА ЗАВЕРШЕНА")


if __name__ == "__main__":
    main()
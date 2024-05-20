import requests
from bs4 import BeautifulSoup
import sqlite3

# folder = 'data'
folder = '/data'
# folder = ''


def time(x):
    if x == 1: time = '8:30 - 10:00'
    if x == 2: time = '10:10 - 11:40'
    if x == 3: time = '12:20 - 13:50'
    if x == 4: time = '14:00 - 15:30'
    if x == 5: time = '15:40 - 17:10'
    if x == 6: time = '17:20 - 18:50'
    if x == 7: time = '19:00 - 20:30'
    return time

def clear_table(table_name):
    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {table_name.replace("-", "_")}')
    conn.commit()
    conn.close()

def create_table(table_name):
    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE {table_name.replace("-", "_")} (
            week TEXT,
            day TEXT,
            num_lesson INTEGER,
            lesson TEXT,
            teacher TEXT,
            type_lesson TEXT,
            aud TEXT,
            group_ INTEGER,
            time_lesson TEXT);
        ''')
    # Закрытие соединения с базой данных
    conn.close()

def write_timetable(week_name, day_name, num_lesson, table_name, groups, separation):
    for l in range(len(groups)):
        lesson_name = groups[l].find(class_='title').text
        teacher = groups[l].find(class_='teacher').text
        type_lesson = groups[l].find(class_='clearfix').text
        aud = groups[l].find(class_='aud').text

        teacher = teacher.lstrip('- ').split()[0]
        type_lesson = type_lesson.lstrip('- ').split()[0]
        print(day_name.text)
        print(f'Предмет: {lesson_name}')
        print(f'Преподаватель: {teacher}')
        print(f'Занятие: {type_lesson}')
        print(f'Аудитория: {aud}')
        if separation != False: 
            print(f"Группа: {separation}")
        print('')

        time_lesson = time(num_lesson)


        conn = sqlite3.connect(f'{folder}/database.db')
        c = conn.cursor()
        c.execute(f"INSERT INTO {table_name.replace('-', '_')} (week, day, num_lesson, lesson, teacher, type_lesson, aud, group_, time_lesson) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (week_name.text, day_name.text, num_lesson, lesson_name, teacher, type_lesson, aud, separation, time_lesson))
        conn.commit()
        conn.close()



def new_timetable(group):
    URL = f"https://timetable.magtu.ru/{group}"

    # Отправить GET-запрос на страницу с расписанием
    try:
        response = requests.get(URL)
    except Exception as e:
        print(f'Возникла ошибка при подключении: {e}')

    if response.status_code == 200:
        conn = sqlite3.connect(f'{folder}/database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{group.replace('-', '_')}'")
        result = cursor.fetchone()
        
        if result is not None:
            print(f"Таблица {group} существует")
            clear_table(group)
            print("Таблица очищена")
        else:
            print(f"Таблица {group} не существует")
            create_table(group)
        cursor.close()
        conn.close()

        # Создать объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, "html.parser")
    
        weeks = soup.find_all('div', class_ = 'week')
    
        for i in range(len(weeks)):
            week_name = weeks[i].find('div', class_='week-name')
            print(f'Неделя: {week_name.text}')
            days = weeks[i].find_all(class_='day')
            for j in range(len(days)):
                day_name = days[j].find(class_='day-name')
                print(day_name.text)
                lessons = days[j].find_all(class_='less-wrap')
                empty_lesson = days[j].find_all(class_='empty')
                number_lesson = len(empty_lesson)
                print(f'empty_lesson {empty_lesson}')
                for k in range(len(lessons)):
                    num_lesson = k +1+number_lesson
                    if lessons[k].find_all(class_='group-0'):
                        groups = lessons[k].find_all(class_=f'group-0')
                        write_timetable(week_name, day_name, num_lesson, group, groups, False)
                    else:
                        for m in range(1, 5):
                            try:
                                groups = lessons[k].find_all(class_=f'group-{m}')           
                                write_timetable(week_name, day_name, num_lesson,group, groups, m)
    
                            except Exception as e:
                                print(f'Ошибка: {e}')
        successfully = True
    
    else:
        print(f"Ошибка при получении расписания: {response.status_code}")
        successfully = False
    return successfully
    pass

# new_timetable('ИДАб-20')
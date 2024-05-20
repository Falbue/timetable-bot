import requests
from bs4 import BeautifulSoup


def anek():
    URL = f"https://www.anekdot.ru/last/anekdot/"

    # Отправить GET-запрос на страницу
    try:
        response = requests.get(URL)
    except Exception as e:
        print(f'Возникла ошибка при подключении: {e}')

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        rates = soup.find('div', class_ = 'topicbox', id = "1")
        anek_text = rates.find('div', class_ = 'text')
        x = f"Анекдот дня:{anek_text.text}"
        try:    
            x = x.replace('-', '\n-')
        except:
            print("Не нужно было экранизировть")
    else:
        print(f"Ошибка при получении расписания: {response.status_code}")
    return x
    pass
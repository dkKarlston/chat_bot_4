from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, logger
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime
import random
import requests
import webbrowser
from urllib.parse import quote


FACTS = {
    "спорт": [
        "Бадминтон – является самым быстрым ракеточным видом спорта: скорость полета волана может достигать в среднем 270 км/час.",
        "В стандартном мячике для гольфа всего 336 выемок.",
        "В пелотоне Формулы-1 нет болида под номером 13, после 12-го сразу идёт 1",
        "Фернандо Алонсо, гонщик «Формулы-1», сел за руль карта в три года.",
        "Нильс Бор, знаменитый физик, был вратарём сборной Дании.",
    ],
    "история": [
        "Великая китайская стена не видна с Луны невооруженным глазом.",
        "Первая фотография была сделана в 1826 году.",
        "Рим был основан в 753 году до нашей эры.",
        "Арабские цифры изобрелись не арабами, а математиками из Индии.",
        "Когда-то морфин использовался для уменьшения кашля.",
    ],
    "космос": [
        "Температура на поверхности Венеры достигает 465°C, что горячее, чем на Меркурии, хотя Венера дальше от Солнца.",
        "Самая высокая гора в Солнечной системе - гора Олимп на Марсе. Ее высота достигает 21 километр.",
        "Нейтронные звезды могут вращаться со скоростью до 600 оборотов в секунду.",
        "В космосе нельзя заплакать. В условиях микрогравитации слезы не падают вниз, как на Земле, а остаются на глазах в виде маленьких капель.",
        "В космосе нет звука. Звук не может распространяться в вакууме, так как ему нужны молекулы воздуха или другого вещества для передачи волн.",
    ],
}


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:


        city = tracker.get_slot("city")
        if not city:
            dispatcher.utter_message(text="Не удалось определить город. Пожалуйста, уточните.")
            return []


        api_key = "c4aec831b9f8a6d4a4acc553848b76ff"

        try:

            city_encoded = quote(city)
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric&lang=ru"


            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Проверяем HTTP-ошибки
            data = response.json()


            if data.get("cod") != 200:
                raise Exception(f"API error: {data.get('message', 'Unknown error')}")


            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            dispatcher.utter_message(text=f"В {city} сейчас {weather_desc}, {temp}°C")

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="Сервис погоды временно недоступен. Попробуйте позже.")
            logger.error(f"Weather API error: {e}")

        except Exception as e:
            dispatcher.utter_message(text="Произошла ошибка при получении погоды.")
            logger.error(f"Action error: {e}")

        return []

        api_key = "c4aec831b9f8a6d4a4acc553848b76ff"

        try:
            city_encoded = quote(city)
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_encoded}&appid={api_key}&units=metric&lang=ru"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            pressure = data["main"]["pressure"]
            sunrise_timestamp = data["sys"]["sunrise"]
            sunset_timestamp = data["sys"]["sunset"]

            sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp).strftime("%H:%M:%S")
            sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")

            weather_responses = [
                (f"В городе {city} сейчас {weather_desc}, температура {temp}°C, "
                 f"атмосферное давление {pressure} гПа.\n"
                 f"Время восхода: {sunrise_time}, время заката: {sunset_time}"),
                (f"Погода в {city}: {weather_desc}, {temp}°C, давление {pressure} гПа. "
                 f"Восход в {sunrise_time}, закат в {sunset_time}."),
                (f"Сейчас в {city} {weather_desc}, температура воздуха {temp} градусов Цельсия, "
                 f"давление {pressure} гектопаскалей. Солнце встало в {sunrise_time}, а сядет в {sunset_time}.")
            ]

            dispatcher.utter_message(text=random.choice(weather_responses))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                dispatcher.utter_message(text="Город не найден. Пожалуйста, уточните название города.")
            else:
                dispatcher.utter_message(text="Произошла ошибка при получении данных о погоде.")
        except Exception as e:
            dispatcher.utter_message(text=f"Произошла ошибка: {e}")

        return [SlotSet("city", None)]




class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        try:

            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%d.%m.%Y")

            message = f"Сейчас {current_time}, сегодня {current_date}"
            dispatcher.utter_message(text=message)


            return []

        except Exception as e:
            dispatcher.utter_message(text="Не удалось определить время.")
            logger.error(f"Error in action_get_time: {e}")
            return []  # Всегда возвращаем список, даже при ошибке

class ActionTellFact(Action):
    def name(self) -> Text:
        return "action_tell_fact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        category = tracker.get_slot("category")
        if not category or category not in FACTS:
            dispatcher.utter_message(text="Пожалуйста, выберите категорию: спорт, история или космос.")
            return [SlotSet("category", None)]

        fact = random.choice(FACTS[category])
        dispatcher.utter_message(text=fact)
        return [SlotSet("category", None)]


class ActionSearchWeb(Action):
    def name(self) -> Text:
        return "action_search_web"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = tracker.get_slot("query")
        if not query:
            dispatcher.utter_message(text="Что вы хотите найти?")
            return []

        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open_new_tab(url)
            dispatcher.utter_message(text=f"Ищу '{query}' в Google...")
        except Exception as e:
            dispatcher.utter_message(text="Не удалось выполнить поиск")

        return []


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        expression = tracker.get_slot("expression")
        if not expression:
            dispatcher.utter_message(text="Пожалуйста, введите выражение для вычисления.")
            return []

        try:
            expression = expression.replace('x', '*')
            result = eval(expression)
            dispatcher.utter_message(text=f"Результат: {result}")
        except (SyntaxError, TypeError, NameError, ZeroDivisionError):
            dispatcher.utter_message(text="Не могу вычислить это выражение.")

        return [SlotSet("expression", None)]


class ActionAnalyzeMood(Action):
    def name(self) -> Text:
        return "action_analyze_mood"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get("text", "").lower()

        positive_words = ["хорошо", "отлично", "прекрасно", "радост", "счастлив", "ура", "люблю", "классно",
                          "замечательно"]
        negative_words = ["плохо", "ужасно", "грустно", "несчаст", "тоскливо", "разочарован", "устал", "бесит"]

        positive_count = sum(word in user_message for word in positive_words)
        negative_count = sum(word in user_message for word in negative_words)

        if positive_count > negative_count:
            mood = "positive"
        elif negative_count > positive_count:
            mood = "negative"
        else:
            mood = "neutral"

        responses = {
            "positive": [
                "Ты звучишь очень позитивно! 😄 Чем могу порадовать тебя ещё?",
                "Похоже, у вас отличное настроение!",
                "Я чувствую вашу радость! Так держать!"
            ],
            "negative": [
                "Ты, похоже, не в настроении... 😔 Хочешь поговорить об этом?",
                "Кажется, вам сейчас нелегко...",
                "Ваше настроение кажется подавленным. Если нужно поговорить - я здесь."
            ],
            "neutral": [
                "Улавливаю нейтральный настрой. Спрашивай, если что-нибудь нужно!",
                "Ваше настроение кажется ровным. Все в порядке?",
                "Похоже, у вас обычный день. Надеюсь, он станет еще лучше!"
            ]
        }

        dispatcher.utter_message(text=random.choice(responses[mood]))
        return []
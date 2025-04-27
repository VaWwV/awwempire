from selenium.webdriver.common.by import By

class CommandProcessor:
    def __init__(self, browser_manager, voice_recognizer, youtube_controller):
        self.browser_manager = browser_manager
        self.voice_recognizer = voice_recognizer
        self.youtube_controller = youtube_controller
        self.is_input_mode = False
        self.current_input_field = None
        
    def show_help(self):
        """Показывает список всех доступных команд"""
        print("\nСписок доступных голосовых команд:")
        print("Управление браузером:")
        print("- 'макарчик запускай' - запуск браузера")
        print("- 'макарчик закрывай' - закрытие браузера")
        print("- 'обнови страницу' - обновление текущей страницы")
        
        print("\nРабота с YouTube:")
        print("- 'открой youtube' - открытие YouTube")
        print("- 'найди видео НАЗВАНИЕ' - поиск видео на YouTube")
        print("- 'включи видео НОМЕР' - выбор видео из рекомендаций по номеру (1-10)")
        print("- 'включи видео НАЗВАНИЕ' - выбор видео из рекомендаций по названию")
        print("- 'включи видео поиск НОМЕР' - выбор видео из результатов поиска по номеру")
        print("- 'включи видео поиск НАЗВАНИЕ' - выбор видео из результатов поиска по названию")
        
        print("\nНавигация по странице:")
        print("- 'листай вверх' - прокрутка страницы вверх")
        print("- 'листай вниз' - прокрутка страницы вниз")
        print("- 'листай начало' - прокрутка в начало страницы")
        print("- 'листай конец' - прокрутка в конец страницы")
        
        print("\nРабота с полями ввода:")
        print("- 'ввод' - включение режима ввода текста в активное поле")
        print("- 'ввод в поле имя НАЗВАНИЕ' - включение режима ввода в поле по имени")
        print("- 'ввод в поле id НАЗВАНИЕ' - включение режима ввода в поле по id")
        print("- 'ввод в поле класс НАЗВАНИЕ' - включение режима ввода в поле по классу")
        print("- 'стоп ввод' - выключение режима ввода текста")
        
        print("\nУправление программой:")
        print("- 'помощь' - показать этот список команд")
        print("- 'микрофон' - выключение голосового управления")
        print("- 'стоп' - выход из программы")
        print("- F2 - включение/выключение голосового управления вручную")
        
    def find_input_field(self, field_type, value):
        """Находит поле ввода на странице"""
        driver = self.browser_manager.get_driver()
        try:
            if field_type == "name":
                return driver.find_element(By.NAME, value)
            elif field_type == "id":
                return driver.find_element(By.ID, value)
            elif field_type == "class":
                return driver.find_element(By.CLASS_NAME, value)
            elif field_type == "xpath":
                return driver.find_element(By.XPATH, value)
        except Exception as e:
            print(f"Ошибка при поиске поля: {e}")
            return None
            
    def input_text_to_field(self, text, field=None):
        """Вводит текст в указанное поле или активное поле"""
        driver = self.browser_manager.get_driver()
        try:
            if field:
                input_field = field
            else:
                input_field = driver.switch_to.active_element
                
            input_field.clear()
            input_field.send_keys(text)
            print(f"Введен текст: {text}")
        except Exception as e:
            print(f"Ошибка при вводе текста: {e}")
            
    def process_command(self, command):
        """Обрабатывает полученную команду"""
        if self.is_input_mode:
            if command.lower() == "стоп ввод":
                self.is_input_mode = False
                self.current_input_field = None
                print("Режим ввода выключен")
            else:
                self.input_text_to_field(command, self.current_input_field)
            return
            
        if "стоп" in command:
            self.browser_manager.close_browser()
            self.voice_recognizer.stop()
            print("Выход из программы.")
        elif "помощь" in command:
            self.show_help()
        elif "микрофон" in command:
            self.voice_recognizer.toggle_voice()
            print("Голосовое управление ВЫКЛЮЧЕНО. Нажмите F2 для включения.")
        elif "макарчик запускай" in command:
            self.browser_manager.setup_browser()
        elif "макарчик закрывай" in command:
            self.browser_manager.close_browser()
        elif "открой youtube" in command:
            self.youtube_controller.open_youtube()
        elif "обнови страницу" in command:
            self.youtube_controller.refresh_page()
        elif command.startswith("листай"):
            direction = command.split()[-1]
            self.youtube_controller.scroll_page(direction)
        elif command.startswith("найди видео"):
            search_query = command[11:].strip()
            if search_query:
                self.youtube_controller.search_youtube(search_query)
            else:
                print("Скажите, что искать на YouTube")
        elif command.startswith("включи видео") or command.startswith("открой видео"):
            search_text = command[13:].strip()
            
            if search_text.isdigit() or any(num in search_text for num in ['первое', 'второе', 'третье', 'четвертое', 'пятое']):
                if search_text.isdigit():
                    number = int(search_text)
                else:
                    number = self.youtube_controller.convert_word_to_number(search_text)
                
                if "поиск" in command:
                    self.youtube_controller.select_search_video(number=number)
                else:
                    self.youtube_controller.select_recommended_video(number=number)
            else:
                if "поиск" in command:
                    self.youtube_controller.select_search_video(title=search_text)
                else:
                    self.youtube_controller.select_recommended_video(title=search_text)
        elif command.startswith("ввод в поле"):
            parts = command.split()
            if len(parts) >= 4:
                field_type = parts[3]
                field_value = " ".join(parts[4:])
                field = self.find_input_field(field_type, field_value)
                if field:
                    self.current_input_field = field
                    self.is_input_mode = True
                    print(f"Режим ввода включен для поля {field_value}. Говорите текст. Скажите 'стоп ввод' для выхода.")
                else:
                    print(f"Поле {field_value} не найдено")
        elif command == "ввод":
            self.is_input_mode = True
            self.current_input_field = None
            print("Режим ввода включен. Говорите текст. Скажите 'стоп ввод' для выхода из режима ввода.")
        else:
            print(f"Неизвестная команда: {command}")
            print("Скажите 'помощь' для просмотра списка доступных команд") 
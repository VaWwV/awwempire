print("Загрузка command_processor.py")
import logging
from app.youtube_controller import YouTubeController

class CommandProcessor:
    def __init__(self, browser_manager, voice_recognizer, youtube_controller):
        self.browser_manager = browser_manager
        self.voice_recognizer = voice_recognizer
        self.youtube_controller = youtube_controller
        self.logger = logging.getLogger(__name__)

    def process_command(self, command):
        """Обрабатывает полученную команду"""
        self.logger.info(f"Processing command: {command}")
        
        if "макарчик запускай" in command:
            print("Запуск браузера...")
            if self.browser_manager.setup_browser():
                print("Браузер успешно запущен")
            else:
                print("Ошибка при запуске браузера")
            
        elif "открой youtube" in command:
            print("Открываю YouTube...")
            if self.browser_manager.open_url("https://www.youtube.com"):
                print("YouTube открыт")
            else:
                print("Ошибка при открытии YouTube")
            
        elif "макарчик закрывай" in command:
            print("Закрываю браузер...")
            self.browser_manager.close_browser()
        
        # ... остальные команды ...

        try:
            command = command.lower().strip()
            self.logger.info(f"Processing command: {command}")

            # Базовые команды
            if "стоп" in command:
                self.voice_recognizer.stop()
                return True
            elif "помощь" in command:
                self.show_help()
                return True
            elif "микрофон" in command:
                self.voice_recognizer.toggle_voice()
                return True

            # Команды браузера
            if "макарчик запускай" in command:
                return self.browser_manager.open_browser()
            elif "макарчик закрывай" in command:
                return self.browser_manager.close_browser()

            if "youtube" in command:
                if "открой" in command or "open" in command:
                    return self.youtube_controller.open_youtube()
                elif "найди" in command or "search" in command:
                    query = command.split("найди")[-1].strip() if "найди" in command else command.split("search")[-1].strip()
                    return self.youtube_controller.search_youtube(query)
                elif "выбери" in command or "select" in command:
                    try:
                        number = int(''.join(filter(str.isdigit, command)))
                        return self.youtube_controller.select_video(number)
                    except ValueError:
                        self.logger.error("No valid number found in command")
                        return False
                elif "следующее" in command or "next" in command:
                    return self.youtube_controller.next_video()
                elif "предыдущее" in command or "previous" in command:
                    return self.youtube_controller.previous_video()

            self.logger.warning(f"Unknown command: {command}")
            return False

        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return False 
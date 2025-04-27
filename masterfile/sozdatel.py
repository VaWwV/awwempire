import os

def create_project_structure(base_path):
    # Определяем структуру проекта
    structure = {
        "app": {
            "__pycache__": {},
            "browser_control": {},
            "command_processing": {},
            "voice_recognition": {},
            "__init__.py": None,
            "browser_manager.py": None,
            "command_processor.py": None,
            "routes.py": None,
            "youtube_manager.py": None,
            "web": {
                "static": {
                    "sounds": {
                        "notification.mp3": None
                    },
                    "css": {},
                    "js": {}
                },
                "frontend": {
                    "app.py": None,
                    "dockerfile": None
                }
            },
            "backend": {
                "dockerfile": None,
                "package.json": None,
                "server.js": None
            }
        },
        "templates": {
            "index.html": None
        },
        "tests": {
            "browser_control": {
                "test_browser_manager.py": None
            },
            "command_processing": {
                "test_command_processor.py": None
            },
            "voice_recognition": {
                "test_voice_recognition.py": None
            }
        },
        "run.py": None,
        "requirements.txt": None,
        "docker-compose.yml": None
    }

    # Функция для рекурсивного создания папок и файлов
    def create_structure(path, structure):
        for name, content in structure.items():
            new_path = os.path.join(path, name)
            if content is None:
                # Создаем файл
                with open(new_path, 'w') as f:
                    pass  # Создаем пустой файл
            else:
                # Создаем папку и рекурсивно создаем ее содержимое
                os.makedirs(new_path, exist_ok=True)
                create_structure(new_path, content)

    # Создаем базовую папку проекта
    os.makedirs(base_path, exist_ok=True)
    create_structure(base_path, structure)

# Укажите путь, где вы хотите создать проект
base_path = "project"
create_project_structure(base_path)

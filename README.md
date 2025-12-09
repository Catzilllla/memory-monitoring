## 🚀 **Готовый пакет для `pip install python-memwatch`**

**Упаковываем для PyPI или приватного репозитория:**

## **1. Финальный `pyproject.toml`:**


## **2. `README.md`:**

```markdown
# Python Memory Watch

Web-монитор памяти Python процесса с визуализацией арен/пул/блоков.
fv,,.vggghh,,,h. bfsz.v
## Установка
```
pip install python-memwatch
```

## Использование

**1. CLI сервер:**
```
python-memwatch
# http://localhost:5000
```

**2. В программе:**
```
from python_memwatch import record_memory, start_background_sampler

start_background_sampler()  # авто-сбор

heavy_work()  # ваш код
record_memory("heavy")
```
```

## **3. Соберите и установите:**

```bash
# 1. Создайте venv (обязательно!)
python -m venv venv
source venv/bin/activate

# 2. Соберите wheel
pip install build
python -m build

# 3. Установите локально
pip install dist/python_memwatch-0.1.1-py3-none-any.whl
```

## **4. Глобальная установка:**

```bash
# Для всех проектов
pip install --user dist/python_memwatch-0.1.1-py3-none-any.whl
```

## **✅ Результат:**

```bash
# В любом проекте, без editable!
pip install python-memwatch
python-memwatch  # сервер
```

```python
# В любом коде
from python_memwatch import start_background_sampler
start_background_sampler()
```

**`.whl` файл работает везде** — venv, user, system. Никаких editable проблем![1][2]

[1](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
[2](https://realpython.com/python-pyproject-toml/)
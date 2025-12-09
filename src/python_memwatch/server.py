from flask import Flask, jsonify, render_template
import psutil
import tracemalloc
import threading
import time
import sys
import importlib.util

app = Flask(__name__, template_folder="templates")
process = psutil.Process()

# Глобальное состояние памяти (симуляция)
memory_state = {
    "arenas": []
}

# ... (остальной код server.py) ...

# === ФУНКЦИИ СОВМЕСТИМОСТИ ДЛЯ ИМПОРТА ===

def record_memory(label="point"):
    """
    Заглушка для обратной совместимости.
    В новой версии мы используем tracemalloc автоматически.
    """
    pass

def start_background_sampler(interval=1.0):
    """
    Заглушка: мониторинг теперь запускается автоматически
    при старте сервера.
    """
    pass


# Сохраняем начальное потребление при старте
BASE_MEMORY = 0

def start_monitor():
    global BASE_MEMORY
    tracemalloc.start()
    # Запоминаем "пустой" вес процесса
    time.sleep(0.5) 
    BASE_MEMORY, _ = tracemalloc.get_traced_memory()
    
    def run_server():
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
        
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    print("🚀 Memory Visualizer: http://localhost:5000")

def simulate_pymalloc_layout():
    try:
        current, _ = tracemalloc.get_traced_memory()
    except:
        current = 0
    
    # Считаем только ПРИРОСТ памяти (ваши данные)
    # Если прирост < 0 (сборка мусора), ставим 0
    user_data_size = max(0, current - BASE_MEMORY)
    
    # Если данных совсем мало (< 4КБ), покажем хотя бы 1 пул для наглядности,
    # если они вообще есть (> 0).
    if user_data_size > 0 and user_data_size < 4096:
         user_data_size = 4096

    ARENA_SIZE = 256 * 1024
    POOL_SIZE = 4 * 1024
    
    # Сколько арен нужно под пользовательские данные
    num_arenas = (user_data_size // ARENA_SIZE) + 1
    
    arenas = []
    base_address = 0x7f0000000000
    
    remaining_bytes = user_data_size
    
    for i in range(num_arenas):
        # Если данных нет, не рисуем пустую арену (кроме случая старта)
        if remaining_bytes <= 0 and i > 0: break
            
        arena_addr = base_address + (i * ARENA_SIZE)
        
        # Заполняем пулами
        bytes_in_arena = min(remaining_bytes, ARENA_SIZE)
        num_pools = max(0, bytes_in_arena // POOL_SIZE)
        
        # Если байты есть, но меньше пула - рисуем 1 пул
        if bytes_in_arena > 0 and num_pools == 0:
            num_pools = 1
            
        pools = []
        # Ограничиваем отрисовку 16 пулами (чтобы влезло в Canvas)
        display_pools = min(num_pools, 16)
        
        for j in range(display_pools):
            pool_addr = arena_addr + (j * POOL_SIZE)
            
            # В пуле блоки по 64 байта
            BLOCK_SIZE = 64
            
            # Логика заполнения блоков внутри пула
            # Последний пул может быть неполным
            if j == num_pools - 1:
                # Остаток байт в последнем пуле
                bytes_in_pool = bytes_in_arena % POOL_SIZE
                if bytes_in_pool == 0: bytes_in_pool = POOL_SIZE
            else:
                bytes_in_pool = POOL_SIZE
            
            num_blocks = bytes_in_pool // BLOCK_SIZE
            display_blocks = min(num_blocks, 8) # Рисуем до 8 блоков
            
            blocks = []
            for k in range(display_blocks):
                blocks.append({
                    "addr": pool_addr + (k * BLOCK_SIZE),
                    "size": BLOCK_SIZE
                })
                
            pools.append({
                "addr": pool_addr,
                "blocks": blocks,
                "total_blocks": num_blocks
            })
            
        arenas.append({
            "addr": arena_addr,
            "size": ARENA_SIZE,
            "pools": pools
        })
        
        remaining_bytes -= bytes_in_arena
        
    return {
        "arenas": arenas, 
        "total_rss": process.memory_info().rss,
        "user_data": user_data_size # Добавим для отладки
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/layout")
def layout():
    """Возвращает структуру памяти для отрисовки"""
    return jsonify(simulate_pymalloc_layout())

def start_monitor():
    """Запуск сервера в фоне"""
    tracemalloc.start()
    
    def run_server():
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
        
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    print("🚀 Memory Visualizer: http://localhost:5000")

def run_script(script_path):
    """Запускает пользовательский скрипт"""
    start_monitor()
    
    # Ждем запуска сервера
    time.sleep(1)
    
    print(f"Running {script_path}...")
    
    # Загружаем и исполняем файл как модуль
    spec = importlib.util.spec_from_file_location("__main__", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["__main__"] = module
    spec.loader.exec_module(module)

def main():
    if len(sys.argv) < 2:
        print("Usage: python-memwatch <script.py>")
        # Демо-режим если нет аргументов
        start_monitor()
        while True:
            # Имитация работы
            data = [b"a" * 100 for _ in range(10000)]
            time.sleep(2)
            del data
            time.sleep(1)
    else:
        run_script(sys.argv[1])

if __name__ == "__main__":
    main()

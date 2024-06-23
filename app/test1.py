import threading
import time

def thread_task():
    while True:
        time.sleep(1)

threads = []
max_threads = 1000000  # Número máximo de hilos a probar

for i in range(max_threads):
    try:
        thread = threading.Thread(target=thread_task)
        thread.start()
        threads.append(thread)
        print(f"Hilo {i+1} iniciado.")
    except Exception as e:
        print(f"No se pudo iniciar el hilo {i+1}: {e}")
        break

print(f"Se iniciaron {len(threads)} hilos.")

# Terminar los hilos (solo para propósitos de limpieza)
for thread in threads:
    thread.join()
    
print(f"Se finalizo {len(threads)} hilos.")
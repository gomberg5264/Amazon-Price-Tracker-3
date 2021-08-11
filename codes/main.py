from src import app
from src.jobs import loop
from threading import Thread

if __name__ == '__main__':
    Thread(target=loop, daemon=True).start()
    app_thread = Thread(target=app.run)
    app_thread.start()
    app_thread.join()
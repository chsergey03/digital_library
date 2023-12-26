from modules.routers import app
from modules.dump import dump_and_upload

from time import sleep
from threading import Thread


def dump_and_upload_files_on_schedule():
    while True:
        dump_and_upload()
        sleep(60)


if __name__ == "__main__":
    th = Thread(target=dump_and_upload_files_on_schedule)
    th.start()

    app.run()

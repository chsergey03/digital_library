import os
import subprocess
import datetime

import yadisk


def dump_and_upload():
    cwd_path = os.getcwd()

    os.environ["PGPASSWORD"] = "password"
    os.chdir(r'C:/Program Files/PostgreSQL/16/bin')

    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    filename = "dump_" + date_str + ".dump"
    filepath = "D:/" + filename

    command = ('pg_dump -h {0} -U {1} -p 5432 -d{2} --file={3} --format=p'
               .format("localhost", "postgres", "digital_library", filepath))

    p = subprocess.Popen(command, shell=True)
    p.wait()

    os.chdir(cwd_path)

    y = yadisk.YaDisk(token=open("data/yadisk_token.txt", "r").readline())
    y.upload(filepath, "/digital_library_backups/" + filename)

from tkinter import *
from tkinter import ttk
import getpass
import socket
import argparse
import os

username  = getpass.getuser()
hostname = socket.gethostname()


def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки")
    parser.add_argument("--vfs", default=None, help="Путь к физическому расположению VFS")
    parser.add_argument("--script", default=None, help="Путь к стартовому скрипту")
    return parser.parse_args()

args = parse_args()


root = Tk()
root.title(f"{hostname} - {username}")
root.geometry("500x500")

text_var = StringVar()

entry = (ttk.Entry(textvariable=text_var))
entry.pack(side = "bottom", fill = 'both', padx=8, pady= 8) #коммандная строка - поле ввода


def getPole(event):
    text = text_var.get()
    text_var.set("")
    if command(text) == "exit":
        root.destroy()



entry.bind("<Return>",getPole)

output = Text(root)
output.pack(side='top', fill='both', expand=True)


def println(text):
    output.insert('end', text + "\n")
    output.see('end')


def debug_params():
    println("[DEBUG] Параметры запуска эмулятора:")
    println(f"[DEBUG]   --vfs    = {args.vfs}")
    println(f"[DEBUG]   --script = {args.script}")
    println("-" * 40)


def command(key):
    key = key.strip()
    println(f'<{username}> $ {key}')
    if not key:
        return "error"

    name = key.split()[0]
    if name == "ls":
        println(f"ls: {StringSplitLS(key)}")
        return "ok"
    elif name == ("cd"):
        println(f"cd: {StringSplitCD(key)}")
        return "ok"
    elif name == "exit":
        return "exit"
    else:
        println(f"Неизвестная команда {key}")
        return "error"


def run_script(path):
    if not os.path.isfile(path):
        println(f"[ОШИБКА] Стартовый скрипт не найден: {path}")
        return
    k = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            k = k + 1
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            status = command(line)
            if status == "exit":
                println("Программа завершена")
                return
            elif status == "error":
                println(f"[ОШИБКА]: строка {k}, команда пропущена")



def StringSplitLS(stroka):
    parts = stroka.split(maxsplit=2)
    first = parts[1] if len(parts) > 1 else ""
    second = parts[2] if len(parts) > 2 else "None"
    return f"flags: [{first}], path: {second}"


def StringSplitCD(stroka):
    parts = stroka.split(maxsplit=2)
    first = parts[1] if len(parts) > 1 else ""
    if first == "":
        return "остаемся там же"
    else:
        return f"перемещен в {first}"


debug_params()
if args.script:
    run_script(args.script)
root.mainloop()
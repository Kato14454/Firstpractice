from tkinter import *
from tkinter import ttk
import getpass
import socket
import argparse
import os
import json

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


vfs_root = None


def count_nodes(folder):
    files = 0
    dirs = 0
    for name, node in folder.items():
        if isinstance(node, dict):
            dirs += 1
            f, d = count_nodes(node)
            files += f
            dirs += d
        else:
            files += 1
    return files, dirs


def load_vfs(path):
    global vfs_root
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        println(f"[ОШИБКА] Файл VFS не найден: {path}")
        return False
    except json.decoder.JSONDecodeError as e:
        println(f"[ОШИБКА] VFS не является корректным JSON: {e}")
        return False
    except OSError as e:
        println(f"[ОШИБКА] Не удалось прочитать VFS: {e}")
        return False
    if not isinstance(data, dict):
        println("[ОШИБКА] Корень VFS должен быть папкой, то есть { ... }")
        return False

    vfs_root = data
    files,dirs = count_nodes(data)
    println(f"[INFO] VFS загружена: {path}")
    println(f"[INFO] Файлов: {files}, папок: {dirs}")
    return True


def debug_params():
    println("[DEBUG] Параметры запуска эмулятора:")
    println(f"[DEBUG]   --vfs    = {args.vfs}")
    println(f"[DEBUG]   --script = {args.script}")
    println("-" * 40)


def command(key):
    key = key.strip()
    println(f'<{username}> $ {key}')
    if not key:
        return "ok"

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

if args.vfs is not None:
    load_vfs(args.vfs)

if args.script:
    run_script(args.script)

root.mainloop()
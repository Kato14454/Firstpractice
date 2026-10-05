from sys import path
from tkinter import *
from tkinter import ttk
import getpass
import socket
import argparse
import os
import json
import time

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


cwd = []


def cwd_str():
    return "/" + "/".join(cwd)


def resolve(path):
    parts = [] if path.startswith("/") else list(cwd)
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)
    return parts


def get_node(parts):
    node = vfs_root
    for name in parts:
        if not isinstance(node, dict) or name not in node:
            return None
        node = node[name]
    return node


def cmd_cd(cmd_args):
    global cwd
    if vfs_root is None:
        println("cd: VFS не загружена (укажите --vfs)")
        return "error"
    if len(cmd_args) > 1:
        println("cd: слишком много аргументов")
        return "error"

    target = cmd_args[0] if cmd_args else "/"
    parts = resolve(target)
    node = get_node(parts)

    if node is None:
        println(f"cd: {target}: нет такого файла или каталога")
        return "error"
    if not isinstance(node, dict):
        println(f"cd: {target}: не является каталогом")
        return "error"

    cwd = parts
    if len(cwd) > 1:
        println(f"Переход в <{cwd_str()}> произведен успешно")
    else:
        println(f"Переход в /home произведен успешно")
    return "ok"


def cmd_ls(cmd_args):
    if vfs_root is None:
        println("ls: VFS не загружена (укажите --vfs)")
        return "error"

    long_format = False
    paths = []
    for a in cmd_args:
        if a.startswith("-"):
            if a != "-l":
                println(f"ls: неизвестный флаг '{a}'")
                return "error"
            long_format = True
        else:
            paths.append(a)
    if len(paths) > 1:
        println("ls: слишком много аргументов")
        return "error"

    target = paths[0] if paths else "."
    node = get_node(resolve(target))
    if node is None:
        println(f"ls: {target}: нет такого файла или каталога")
        return "error"

    if isinstance(node, dict):
        items = sorted(node.items())
    else:
        items = [(target.split("/")[-1], node)]

    names = []
    for name, child in items:
        if isinstance(child, dict):
            if long_format:
                println(f"d  {name}/")
            else:
                names.append(name + "/")
        else:
            if long_format:
                println(f"-  {name}  {len(child)}")
            else:
                names.append(name)
    if names:
        println("  ".join(names))
    return "ok"


def print_tree(folder,k=0):
    stroka = "    "
    for name,child in folder.items():
        println(f"{k*stroka}{name}:")
        if isinstance(child, dict):
            print_tree(child,k+1)


def cmd_tree(cmd_args):
    if vfs_root is None:
        println("tree: VFS не загружена (укажите --vfs)")
        return "error"
    if len(cmd_args) > 1:
        println("tree: слишком много аргументов")
        return "error"

    target = cmd_args[0] if cmd_args else "."
    node = get_node(resolve(target))
    if node is None:
        println(f"tree: {target}: нет такого файла или каталога")
        return "error"
    if not isinstance(node, dict):
        println(f"tree: {target}: не является каталогом")
        return "error"

    print_tree(node)
    return "ok"


start_time =  time.strftime("%Y-%m-%d %H:%M")

def cmd_who(cmd_args):
    if cmd_args:
        println(f"who: лишние аргументы")
        return "error"
    println(f"{username} tty1 {start_time}")
    return "ok"


def debug_params():
    println("[DEBUG] Параметры запуска эмулятора:")
    println(f"[DEBUG]   --vfs    = {args.vfs}")
    println(f"[DEBUG]   --script = {args.script}")
    println("-" * 40)


def command(key):
    key = key.strip()
    println(f'<{username}"@{hostname}: {cwd_str()}> $ {key}')
    if not key:
        return "ok"

    words = key.split()
    name = words[0]
    cmd_args = words[1:]

    if name == "ls":
        return cmd_ls(cmd_args)
    elif name == ("cd"):
        return cmd_cd(cmd_args)
    elif name =="tree":
        return cmd_tree(cmd_args)
    elif name == "who":
        return cmd_who(cmd_args)
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


debug_params()

if args.vfs is not None:
    load_vfs(args.vfs)

if args.script:
    run_script(args.script)

root.mainloop()
from tkinter import *
from tkinter import ttk
import getpass
import socket

username  = getpass.getuser()
hostname = socket.gethostname()

root = Tk()  # создаем корневой объект - окно
root.title(f"{hostname} - {username}")  # устанавливаем заголовок окна
root.geometry("500x500")  # устанавливаем размеры окна

text_var = StringVar()

entry = (ttk.Entry(textvariable=text_var))
entry.pack(side = "bottom", fill = 'both', padx=8, pady= 8) #коммандная строка - поле ввода


def getPole(event):
    text = text_var.get()
    command(text)
    text_var.set("")


entry.bind("<Return>",getPole)

output = Text(root)
output.pack(side='top', fill='both', expand=True)

def command(key):
    if key[:2] == "ls":
        output.insert('end', f"<{username}> $ {key}\n")
        output.insert('end', f"ls: {StringSplitLS(key)}\n")
    elif key[:2] == ("cd"):
        output.insert('end', f"<{username}> $ {key}\n")
        output.insert('end', f"ls: {StringSplitCD(key)}\n")
    elif key == "exit":
        root.destroy()
    else:
        output.insert('end', f"<{username}> $ {key}\n")
        output.insert('end', "Неверная команда")


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


root.mainloop()


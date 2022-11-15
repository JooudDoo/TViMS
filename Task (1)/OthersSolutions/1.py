from collections import Counter
import os
import math

def clear_txt(txt):
    txt = txt.lower()
    txt = txt.replace("\n", "")
    txt = txt.replace("\t", "")
    for i in "-,./';]=[1234567890!@#$%^&*()_+{}|:\"<>?`~":
        txt = txt.replace(i, "")
    return txt

sp = 0
nesp = 0

counterWordSpam = Counter()
counterWordHam = Counter()

with open("learn.csv", 'r') as file:
    text = file.readlines()
    for line in text:
        mark, text = line.split(',')[:2]
        text = clear_txt(text)
        if mark == 'spam':
            counterWordSpam.update(set(text.split(" ")))
            sp += 1
        elif mark == 'ham':
            counterWordHam.update(set(text.split(" ")))
            nesp += 1

summ = sp + nesp
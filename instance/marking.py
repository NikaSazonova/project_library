import sys
import pymorphy2
import csv
import string
import os
r

vowels = {'а', 'о', 'и', 'е', 'у', 'ю', 'ё', 'я', 'ы', 'э'}
names = ['Слово', 'Часть речи', 'n - 1', 'n + 1', 'Род', 'Число', 'Падеж', 'Склонение']


def marking(file_name, path, path2):
    morph = pymorphy2.MorphAnalyzer()
    f_open = open(path, 'r', encoding="utf-8")
    name_res = f"marked_{file_name}"
    text = list()
    f = open(path2, 'w', newline='', encoding="cp1251")
    writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(names)
    exclude = set(string.punctuation)
    exclude.add('–')
    exclude.add('«')
    exclude.add('»')
    exclude.add('*')
    for line in f_open:
        line = ''.join(ch for ch in line if ch not in exclude)
        for word in line.split():
            text.append(word)
    for i in range(len(text)):
        res = list()
        p = morph.parse(text[i])[0]
        POS = str(p.tag.POS)
        if len(text) == 1:
            n_word = '-'
            p_word = '-'
        elif i == len(text) - 1:
            p_word = text[i - 1]
            n_word = '-'
        elif i == 0:
            n_word = text[i + 1]
            p_word = '-'
        else:
            n_word = text[i + 1]
            p_word = text[i - 1]
        gender = str(p.tag.gender)
        number = str(p.tag.number)
        case = str(p.tag.case)
        if gender == 'None':
            gender = '-'
        if number == 'None':
            number = '-'
        if case == 'None':
            case = '-'
        if POS == 'NOUN':
            if gender == 'masc' and morph.parse(text[i])[0].normal_form[-1] == 'а':
                inflection = 'Первое'
            elif gender == 'masc' and morph.parse(text[i])[0].normal_form[-1] == 'я':
                inflection = 'Первое'
            elif gender == 'femn' and morph.parse(text[i])[0].normal_form[-1] == 'а':
                inflection = 'Первое'
            elif gender == 'femn' and morph.parse(text[i])[0].normal_form[-1] == 'я':
                inflection = 'Первое'
            elif gender == 'masc' and morph.parse(text[i])[0].normal_form[-1] not in vowels:
                inflection = 'Второе'
            elif gender == 'neut' and morph.parse(text[i])[0].normal_form[-1] == 'о':
                inflection = 'Второе'
            elif gender == 'neut' and morph.parse(text[i])[0].normal_form[-1] == 'е':
                inflection = 'Второе'
            elif gender == 'femn' and morph.parse(text[i])[0].normal_form[-1] == 'ь':
                inflection = 'Третье'
            else:
                inflection = '-'
        else:
            inflection = '-'
        res.append(text[i])
        res.append(POS)
        res.append(p_word)
        res.append(n_word)
        res.append(gender)
        res.append(number)
        res.append(case)
        res.append(inflection)
        writer.writerow(res)
    f.close()
    f_open.close()
    return True

# marking('ottsy_i_dieti_-_ivan_sierghieievich_turghieniev.txt')

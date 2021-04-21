import sys
import pymorphy2
import csv
import string
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog, QInputDialog

vowels = {'а', 'о', 'и', 'е', 'у', 'ю', 'ё', 'я', 'ы', 'э'}
names = ['Слово', 'Часть речи', 'n - 1', 'n + 1', 'Род', 'Число', 'Падеж', 'Склонение']


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('proj_razm.ui', self)
        self.setFixedSize(600, 300)
        self.setWindowTitle('Разметчик корпусов')
        # изменение некоторых элементов дизайна
        self.setStyleSheet("background-color:  #eceff1;")
        font = QtGui.QFont()
        font.setFamily("Times")
        font.setPointSize(11)
        self.pushButton.setStyleSheet('background-color: #A3E1DA; color: #000066')
        self.pushButton.setFont(font)
        self.textEdit_2.setFont(font)
        self.textEdit_2.setAlignment(QtCore.Qt.AlignCenter)
        font_2 = QtGui.QFont()
        font_2.setFamily("Times")
        font_2.setPointSize(10)
        self.radioButton.setFont(font_2)
        self.radioButton.setStyleSheet("color: #000066")
        self.radioButton_2.setFont(font_2)
        self.radioButton_2.setStyleSheet("color: #000066")
        self.label.setFont(font)
        self.label.setStyleSheet("color: #000066")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setFont(font)
        self.label_2.adjustSize()
        self.label_2.setStyleSheet("color: #000066")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setFont(font)
        self.label_3.adjustSize()
        self.label_3.setStyleSheet("color: #000066")
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        # привязка радиокнопок к событию
        self.radioButton.toggled.connect(self.onClicked)
        self.radioButton_2.toggled.connect(self.onClicked)
        # установка значения, минимума и максимума для виджета прогресса
        self.progressBar.setValue(0)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

    def onClicked(self):
        if self.radioButton.isChecked():
            # проверяется, какой формат файла выбран и открывается соответствующий диалог
            self.f_name = QFileDialog.getOpenFileName(self, 'Выбрать файл', '',
                                                      'Текстовый файл (*.txt);;Все файлы (*)')[0]
            self.pushButton.clicked.connect(self.razmetka_1)
        elif self.radioButton_2.isChecked():
            text, ok_pressed = QInputDialog.getText(self, "Ввод текста", "Вставьте исходный текст")
            if ok_pressed:
                self.f_open = text
            self.pushButton.clicked.connect(self.razmetka_2)

    def razmetka_1(self):
        morph = pymorphy2.MorphAnalyzer()
        try:
            f_open = open(self.f_name, 'r', encoding="utf8")
        except IOError as e:
            self.label.setText('Неверное имя файла. Попробуйте ещё раз:')
            return
        self.label.setText('Успешно!')
        name_res = self.textEdit_2.toPlainText()
        text = list()
        f = open(f'{name_res}.csv', 'w', newline='', encoding="cp1251")
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(names)
        exclude = set(string.punctuation)
        exclude.add('–')
        exclude.add('«')
        exclude.add('»')
        # очищение от знаков препинания
        for line in f_open:
            line = ''.join(ch for ch in line if ch not in exclude)
            for word in line.split():
                text.append(word)
        for i in range(len(text)):
            # далее идет разметка каждого слова и запись в конечный файл
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
            self.progressBar.setValue(self.progressBar.value() + 100 // len(text))
        # доводим виджет прогресса до максимума, если необходимо
        self.progressBar.setValue(100)
        f.close()
        f_open.close()

    def razmetka_2(self):
        text = list()
        morph = pymorphy2.MorphAnalyzer()
        self.label.setText('Успешно!')
        name_res = self.textEdit_2.toPlainText()
        f = open(f'{name_res}.csv', 'w', newline='', encoding="cp1251")
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(names)
        exclude = set(string.punctuation)
        exclude.add('–')
        exclude.add('«')
        exclude.add('»')
        # очищение от знаков препинания
        self.f_open = ''.join(ch for ch in self.f_open if ch not in exclude)
        for word in self.f_open.split():
            text.append(word)
        for i in range(len(text)):
            # далее идет разметка каждого слова и запись в исходный файл
            res = list()
            p = morph.parse(text[i])[0]
            POS = str(p.tag.POS)
            if POS == 'None':
                POS = '-'
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
            self.progressBar.setValue(self.progressBar.value() + 100 // len(text))
        # доводим виджет прогресса до максимума, если необходимо
        self.progressBar.setValue(100)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())

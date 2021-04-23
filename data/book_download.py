import yadisk

disk = yadisk.YaDisk(token='AQAAAABUIJphAAcUIlSKz5SMo0q9gbAxBIW03Uc')

a = list(disk.listdir("/book"))


def folder():
    disk.mkdir('/book')


def book_load(file, name):
    disk.upload(f'{file}', f'/book/{name}')


def book_download(name):
    disk.download(f'/book/{name}', f'{name}')

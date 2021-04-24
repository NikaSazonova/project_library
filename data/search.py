import sqlite3


def search(request):
    query(books).filter(books.title.like(f'%{request}%'))

import sqlite3


def search(request):
    connec = sqlite3.connect("project_library/bd/library.db")
    curs = connec.cursor()
    sor_t = curs.execute("""SELECT * FROM books
                WHERE title LIKE '?'""", (f'%{request}%',)).fetchall()
    connec.close()
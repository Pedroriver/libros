import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
DB = 'libros.db'

ESTADOS = ['📖 Por leer', '📘 Leyendo', '✅ Leído']


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT '📖 Por leer',
                resena TEXT DEFAULT '',
                creado TEXT NOT NULL
            )
        ''')


def get_libros():
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        filas = con.execute(
            'SELECT * FROM libros ORDER BY id DESC'
        ).fetchall()
    return [dict(f) for f in filas]


def get_libro(libro_id):
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        fila = con.execute(
            'SELECT * FROM libros WHERE id = ?', (libro_id,)
        ).fetchone()
    return dict(fila) if fila else None


@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        resena = request.form.get('resena', '').strip()
        if titulo and autor:
            with sqlite3.connect(DB) as con:
                con.execute(
                    'INSERT INTO libros (titulo, autor, resena, creado) VALUES (?, ?, ?, ?)',
                    (titulo, autor, resena, datetime.now().strftime("%d/%m/%Y"))
                )
        return redirect(url_for('inicio'))

    libros = get_libros()
    return render_template(
        'inicio.html',
        nombre="Pedro",
        fecha=datetime.now().strftime("%d/%m/%Y"),
        libros=libros,
        num_libros=len(libros),
        estados=ESTADOS,
    )


@app.route('/editar-resena/<int:libro_id>', methods=['GET', 'POST'])
def editar_resena(libro_id):
    libro = get_libro(libro_id)
    if not libro:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        resena = request.form.get('resena', '').strip()
        with sqlite3.connect(DB) as con:
            con.execute(
                'UPDATE libros SET resena = ? WHERE id = ?',
                (resena, libro_id)
            )
        return redirect(url_for('inicio'))

    return render_template('editar_resena.html', libro=libro)


@app.route('/borrar/<int:libro_id>', methods=['POST'])
def borrar_libro(libro_id):
    with sqlite3.connect(DB) as con:
        con.execute('DELETE FROM libros WHERE id = ?', (libro_id,))
    return redirect(url_for('inicio'))


@app.route('/estado/<int:libro_id>', methods=['POST'])
def cambiar_estado(libro_id):
    nuevo_estado = request.form.get('estado', '').strip()
    if nuevo_estado in ESTADOS:
        with sqlite3.connect(DB) as con:
            con.execute(
                'UPDATE libros SET estado = ? WHERE id = ?',
                (nuevo_estado, libro_id)
            )
    return redirect(url_for('inicio'))


@app.route('/sobre-mi')
def sobre_mi():
    return render_template('sobre_mi.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuración de la base de datos ---
# Render nos dará la URL de PostgreSQL en una variable de entorno.
database_url = os.environ.get('DATABASE_URL')

# SQLAlchemy a veces requiere que la URL empiece por 'postgresql://' en lugar de 'postgres://'
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Si estamos en local (sin variable de entorno), usa SQLite como respaldo
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///libros.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Modelo de datos ---
class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), default='📖 Por leer')
    resena = db.Column(db.Text, default='')
    creado = db.Column(db.String(20), nullable=False)

ESTADOS = ['📖 Por leer', '📘 Leyendo', '✅ Leído']

# --- Crear las tablas automáticamente al iniciar (necesario para Render) ---
with app.app_context():
    db.create_all()

# --- Rutas ---
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        autor = request.form.get('autor', '').strip()
        resena = request.form.get('resena', '').strip()
        
        if titulo and autor:
            nuevo_libro = Libro(
                titulo=titulo,
                autor=autor,
                resena=resena,
                creado=datetime.now().strftime("%d/%m/%Y")
            )
            db.session.add(nuevo_libro)
            db.session.commit()
        return redirect(url_for('inicio'))

    libros = Libro.query.order_by(Libro.id.desc()).all()
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
    libro = Libro.query.get_or_404(libro_id)
    if request.method == 'POST':
        libro.resena = request.form.get('resena', '').strip()
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template('editar_resena.html', libro=libro)

@app.route('/borrar/<int:libro_id>', methods=['POST'])
def borrar_libro(libro_id):
    libro = Libro.query.get_or_404(libro_id)
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for('inicio'))

@app.route('/estado/<int:libro_id>', methods=['POST'])
def cambiar_estado(libro_id):
    libro = Libro.query.get_or_404(libro_id)
    nuevo_estado = request.form.get('estado', '').strip()
    if nuevo_estado in ESTADOS:
        libro.estado = nuevo_estado
        db.session.commit()
    return redirect(url_for('inicio'))

@app.route('/sobre-mi')
def sobre_mi():
    return render_template('sobre_mi.html')

if __name__ == '__main__':
    app.run(debug=True)

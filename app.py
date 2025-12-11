import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'chave_secreta_zero22'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
DATABASE = 'database.db'

# Extensões permitidas
EXT_IMG = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
EXT_AUDIO = {'mp3', 'wav', 'ogg', 'zip', 'rar'}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        # Tabelas: Usuários, Configs, Álbuns, Mídias
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS albums (id INTEGER PRIMARY KEY, title TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        db.execute('''CREATE TABLE IF NOT EXISTS media (
                        id INTEGER PRIMARY KEY, 
                        filename TEXT, 
                        type TEXT, 
                        album_id INTEGER, 
                        FOREIGN KEY(album_id) REFERENCES albums(id))''')
        
        # Admin padrão
        user = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not user:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))
        
        # Config padrão
        try:
            db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('site_title', 'Equipe Zero22'))
            db.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('history_text', 'A história da equipe começa nas ruas...'))
        except: pass
        db.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS PÚBLICAS ---

@app.route('/')
def index():
    db = get_db()
    titulo = db.execute('SELECT value FROM settings WHERE key = ?', ('site_title',)).fetchone()['value']
    # Pega os 3 últimos álbuns para destaque
    albuns = db.execute('SELECT * FROM albums ORDER BY created_at DESC LIMIT 3').fetchall()
    return render_template('home.html', titulo=titulo, albuns=albuns)

@app.route('/historia')
def historia():
    db = get_db()
    texto = db.execute('SELECT value FROM settings WHERE key = ?', ('history_text',)).fetchone()['value']
    return render_template('historia.html', texto=texto)

@app.route('/fotos')
def fotos():
    db = get_db()
    albuns = db.execute('SELECT * FROM albums ORDER BY created_at DESC').fetchall()
    return render_template('fotos.html', albuns=albuns)

@app.route('/album/<int:album_id>')
def ver_album(album_id):
    db = get_db()
    album = db.execute('SELECT * FROM albums WHERE id = ?', (album_id,)).fetchone()
    fotos = db.execute('SELECT * FROM media WHERE album_id = ? AND type = "img"', (album_id,)).fetchall()
    return render_template('ver_album.html', album=album, fotos=fotos)

@app.route('/musicas')
def musicas():
    db = get_db()
    arquivos = db.execute('SELECT * FROM media WHERE type = "audio" OR type = "zip"').fetchall()
    return render_template('musicas.html', arquivos=arquivos)

# --- SISTEMA ADMIN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (request.form['username'],)).fetchone()
        if user and user['password'] == request.form['password']:
            session['user_id'] = user['id']
            return redirect(url_for('admin'))
        flash('Login inválido')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    db = get_db()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # 1. CRIAR ÁLBUM
        if action == 'create_album':
            nome = request.form['album_name']
            db.execute('INSERT INTO albums (title) VALUES (?)', (nome,))
            db.commit()
            flash(f'Álbum "{nome}" criado!')

        # 2. UPLOAD DE MÍDIA (MÚLTIPLOS ARQUIVOS)
        elif action == 'upload':
            files = request.files.getlist('files') # Pega lista de arquivos
            album_id = request.form.get('album_id') # Pode ser None se for música
            
            for file in files:
                if file.filename == '': continue
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                ftype = 'unknown'
                if ext in EXT_IMG: ftype = 'img'
                elif ext in EXT_AUDIO: ftype = 'zip' if ext in ['zip','rar'] else 'audio'
                
                # Salva no disco
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Salva no Banco
                db.execute('INSERT INTO media (filename, type, album_id) VALUES (?, ?, ?)', 
                           (filename, ftype, album_id if album_id else None))
            db.commit()
            flash(f'{len(files)} arquivos enviados!')

        # 3. ATUALIZAR TEXTOS
        elif action == 'update_settings':
            db.execute('UPDATE settings SET value = ? WHERE key = ?', (request.form['history_text'], 'history_text'))
            db.commit()
            flash('História atualizada!')

    # Carregar dados para o painel
    albuns = db.execute('SELECT * FROM albums').fetchall()
    todas_midias = db.execute('SELECT * FROM media ORDER BY id DESC LIMIT 50').fetchall()
    historia = db.execute('SELECT value FROM settings WHERE key = ?', ('history_text',)).fetchone()['value']
    
    return render_template('admin.html', albuns=albuns, midias=todas_midias, historia=historia)

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_media(id):
    db = get_db()
    # Pega nome do arquivo para deletar do disco
    media = db.execute('SELECT filename FROM media WHERE id = ?', (id,)).fetchone()
    if media:
        path = os.path.join(app.config['UPLOAD_FOLDER'], media['filename'])
        if os.path.exists(path): os.remove(path) # Deleta do HD
        db.execute('DELETE FROM media WHERE id = ?', (id,)) # Deleta do Banco
        db.commit()
        flash('Arquivo deletado.')
    return redirect(url_for('admin'))

# ... (código anterior) ...

@app.route('/admin/delete_album/<int:album_id>', methods=['POST'])
@login_required
def delete_album(album_id):
    db = get_db()
    
    # 1. Busca todas as mídias (fotos) deste álbum
    midias = db.execute('SELECT * FROM media WHERE album_id = ?', (album_id,)).fetchall()
    
    # 2. Apaga os arquivos físicos da pasta 'uploads'
    for media in midias:
        path = os.path.join(app.config['UPLOAD_FOLDER'], media['filename'])
        if os.path.exists(path):
            os.remove(path)
            
    # 3. Apaga os registros das mídias no banco de dados
    db.execute('DELETE FROM media WHERE album_id = ?', (album_id,))
    
    # 4. Finalmente, apaga o álbum
    db.execute('DELETE FROM albums WHERE id = ?', (album_id,))
    db.commit()
    
    flash('Álbum e todas as suas fotos foram apagados!')
    return redirect(url_for('admin'))

# ... (if __name__ == '__main__': ...)

if __name__ == '__main__':
    os.makedirs('static/uploads', exist_ok=True)
    init_db()
    app.run(debug=True)
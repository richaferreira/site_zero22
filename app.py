import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'chave_secreta_zero22_v2_segura'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = None  # Upload ilimitado
DATABASE = 'database.db'

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
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
        db.execute('CREATE TABLE IF NOT EXISTS albums (id INTEGER PRIMARY KEY, title TEXT, cover_photo TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        db.execute("""CREATE TABLE IF NOT EXISTS media (
                        id INTEGER PRIMARY KEY,
                        filename TEXT,
                        type TEXT,
                        album_id INTEGER,
                        FOREIGN KEY(album_id) REFERENCES albums(id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS eventos (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        date TEXT,
                        location TEXT,
                        image TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

        try:
            db.execute('ALTER TABLE albums ADD COLUMN cover_photo TEXT')
        except Exception:
            pass

        try:
            db.execute('ALTER TABLE eventos ADD COLUMN image TEXT')
        except Exception:
            pass

        try:
            db.execute('ALTER TABLE media ADD COLUMN cover_image TEXT')
        except Exception:
            pass

        user = db.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
        if not user:
            hashed = generate_password_hash('admin')
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', hashed))
        elif not user['password'].startswith('pbkdf2:') and not user['password'].startswith('scrypt:'):
            hashed = generate_password_hash(user['password'])
            db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, user['id']))

        try:
            db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('site_title', 'Equipe Zero22'))
            db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('history_text', 'A historia da equipe comeca nas ruas...'))
            db.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ('instagram_url', 'https://www.instagram.com/equipezero22'))
        except Exception:
            pass
        db.commit()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_album_cover(album_id):
    db = get_db()
    album = db.execute("SELECT cover_photo FROM albums WHERE id = ?", (album_id,)).fetchone()
    if album and album['cover_photo']:
        return album['cover_photo']
    foto = db.execute("SELECT filename FROM media WHERE album_id = ? AND type = 'img' LIMIT 1", (album_id,)).fetchone()
    if foto:
        return foto['filename']
    return None


@app.route('/')
def index():
    db = get_db()
    titulo = db.execute("SELECT value FROM settings WHERE key = ?", ('site_title',)).fetchone()['value']
    albuns = db.execute('SELECT * FROM albums ORDER BY created_at DESC LIMIT 6').fetchall()
    albuns_com_capa = []
    for album in albuns:
        capa = get_album_cover(album['id'])
        albuns_com_capa.append({'id': album['id'], 'title': album['title'], 'created_at': album['created_at'], 'cover': capa})
    return render_template('home.html', titulo=titulo, albuns=albuns_com_capa)


@app.route('/historia')
def historia():
    db = get_db()
    texto = db.execute("SELECT value FROM settings WHERE key = ?", ('history_text',)).fetchone()['value']
    return render_template('historia.html', texto=texto)


@app.route('/fotos')
def fotos():
    db = get_db()
    albuns = db.execute('SELECT * FROM albums ORDER BY created_at DESC').fetchall()
    albuns_com_capa = []
    for album in albuns:
        capa = get_album_cover(album['id'])
        num_fotos = db.execute("SELECT COUNT(*) as total FROM media WHERE album_id = ? AND type = 'img'", (album['id'],)).fetchone()['total']
        albuns_com_capa.append({'id': album['id'], 'title': album['title'], 'created_at': album['created_at'], 'cover': capa, 'num_fotos': num_fotos})
    return render_template('fotos.html', albuns=albuns_com_capa)


@app.route('/album/<int:album_id>')
def ver_album(album_id):
    db = get_db()
    album = db.execute('SELECT * FROM albums WHERE id = ?', (album_id,)).fetchone()
    if not album:
        return render_template('404.html'), 404
    fotos = db.execute("SELECT * FROM media WHERE album_id = ? AND type = 'img'", (album_id,)).fetchall()
    return render_template('ver_album.html', album=album, fotos=fotos)


@app.route('/musicas')
def musicas():
    db = get_db()
    arquivos = db.execute("SELECT * FROM media WHERE type = 'audio' OR type = 'zip' ORDER BY id DESC").fetchall()
    return render_template('musicas.html', arquivos=arquivos)


@app.route('/eventos')
def eventos():
    db = get_db()
    eventos_list = db.execute('SELECT * FROM eventos ORDER BY date DESC').fetchall()
    return render_template('eventos.html', eventos=eventos_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (request.form['username'],)).fetchone()
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = user['id']
            return redirect(url_for('admin'))
        flash('Login invalido')
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

        if action == 'create_album':
            nome = request.form['album_name']
            cover_filename = ''
            if 'album_cover' in request.files:
                cover_file = request.files['album_cover']
                if cover_file.filename:
                    cf_name = secure_filename(cover_file.filename)
                    cext = cf_name.rsplit('.', 1)[1].lower() if '.' in cf_name else ''
                    if cext in EXT_IMG:
                        cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cf_name))
                        cover_filename = cf_name
            db.execute('INSERT INTO albums (title, cover_photo) VALUES (?, ?)', (nome, cover_filename))
            db.commit()
            album_id_new = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            if 'album_photos' in request.files:
                photos = request.files.getlist('album_photos')
                count = 0
                for photo in photos:
                    if photo.filename == '':
                        continue
                    pname = secure_filename(photo.filename)
                    pext = pname.rsplit('.', 1)[1].lower() if '.' in pname else ''
                    if pext in EXT_IMG:
                        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], pname))
                        db.execute('INSERT INTO media (filename, type, album_id) VALUES (?, ?, ?)',
                                   (pname, 'img', album_id_new))
                        count += 1
                db.commit()
                if count > 0:
                    flash(f'Album "{nome}" criado com {count} foto(s)!')
                else:
                    flash(f'Album "{nome}" criado!')
            else:
                flash(f'Album "{nome}" criado!')

        elif action == 'upload':
            files = request.files.getlist('files')
            album_id = request.form.get('album_id')
            cover_image_name = ''
            if 'cover_image' in request.files:
                cover_file = request.files['cover_image']
                if cover_file.filename:
                    cover_filename = secure_filename(cover_file.filename)
                    cext = cover_filename.rsplit('.', 1)[1].lower() if '.' in cover_filename else ''
                    if cext in EXT_IMG:
                        cover_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_filename))
                        cover_image_name = cover_filename
            count = 0
            for file in files:
                if file.filename == '':
                    continue
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                ftype = 'unknown'
                if ext in EXT_IMG:
                    ftype = 'img'
                elif ext in EXT_AUDIO:
                    ftype = 'zip' if ext in ['zip', 'rar'] else 'audio'
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute('INSERT INTO media (filename, type, album_id, cover_image) VALUES (?, ?, ?, ?)',
                           (filename, ftype, album_id if album_id else None, cover_image_name if ftype in ['audio', 'zip'] else ''))
                count += 1
            db.commit()
            flash(f'{count} arquivo(s) enviado(s) com sucesso!')

        elif action == 'update_settings':
            db.execute("UPDATE settings SET value = ? WHERE key = ?", (request.form['history_text'], 'history_text'))
            if 'instagram_url' in request.form:
                db.execute("UPDATE settings SET value = ? WHERE key = ?", (request.form['instagram_url'], 'instagram_url'))
            db.commit()
            flash('Configuracoes atualizadas!')

        elif action == 'create_evento':
            title = request.form['evento_title']
            description = request.form.get('evento_description', '')
            date = request.form.get('evento_date', '')
            location = request.form.get('evento_location', '')
            evento_image = ''
            if 'evento_image' in request.files:
                img_file = request.files['evento_image']
                if img_file.filename:
                    img_filename = secure_filename(img_file.filename)
                    ext = img_filename.rsplit('.', 1)[1].lower() if '.' in img_filename else ''
                    if ext in EXT_IMG:
                        img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
                        evento_image = img_filename
            db.execute('INSERT INTO eventos (title, description, date, location, image) VALUES (?, ?, ?, ?, ?)',
                       (title, description, date, location, evento_image))
            db.commit()
            flash(f'Evento "{title}" criado!')

        elif action == 'change_password':
            new_pass = request.form.get('new_password', '')
            if len(new_pass) >= 4:
                hashed = generate_password_hash(new_pass)
                db.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, session['user_id']))
                db.commit()
                flash('Senha alterada com sucesso!')
            else:
                flash('A senha deve ter pelo menos 4 caracteres.')

    albuns = db.execute('SELECT * FROM albums ORDER BY created_at DESC').fetchall()
    todas_midias = db.execute('SELECT * FROM media ORDER BY id DESC LIMIT 50').fetchall()
    historia_text = db.execute("SELECT value FROM settings WHERE key = ?", ('history_text',)).fetchone()['value']
    instagram = db.execute("SELECT value FROM settings WHERE key = ?", ('instagram_url',)).fetchone()
    instagram_url = instagram['value'] if instagram else ''
    eventos_list = db.execute('SELECT * FROM eventos ORDER BY date DESC').fetchall()
    num_fotos = db.execute("SELECT COUNT(*) as total FROM media WHERE type = 'img'").fetchone()['total']
    num_audios = db.execute("SELECT COUNT(*) as total FROM media WHERE type = 'audio' OR type = 'zip'").fetchone()['total']

    return render_template('admin.html', albuns=albuns, midias=todas_midias, historia=historia_text,
                           instagram_url=instagram_url, eventos=eventos_list,
                           num_fotos=num_fotos, num_audios=num_audios, num_albuns=len(albuns))


@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_media(id):
    db = get_db()
    media = db.execute('SELECT filename FROM media WHERE id = ?', (id,)).fetchone()
    if media:
        path = os.path.join(app.config['UPLOAD_FOLDER'], media['filename'])
        if os.path.exists(path):
            os.remove(path)
        db.execute('DELETE FROM media WHERE id = ?', (id,))
        db.commit()
        flash('Arquivo deletado.')
    return redirect(url_for('admin'))


@app.route('/admin/delete_album/<int:album_id>', methods=['POST'])
@login_required
def delete_album(album_id):
    db = get_db()
    midias = db.execute('SELECT * FROM media WHERE album_id = ?', (album_id,)).fetchall()
    for media in midias:
        path = os.path.join(app.config['UPLOAD_FOLDER'], media['filename'])
        if os.path.exists(path):
            os.remove(path)
    db.execute('DELETE FROM media WHERE album_id = ?', (album_id,))
    db.execute('DELETE FROM albums WHERE id = ?', (album_id,))
    db.commit()
    flash('Album e todas as suas fotos foram apagados!')
    return redirect(url_for('admin'))


@app.route('/admin/delete_evento/<int:evento_id>', methods=['POST'])
@login_required
def delete_evento(evento_id):
    db = get_db()
    db.execute('DELETE FROM eventos WHERE id = ?', (evento_id,))
    db.commit()
    flash('Evento removido!')
    return redirect(url_for('admin'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def file_too_large(e):
    flash('Arquivo muito grande! Maximo permitido: 50MB.')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    os.makedirs('static/uploads', exist_ok=True)
    init_db()
    app.run(debug=True)

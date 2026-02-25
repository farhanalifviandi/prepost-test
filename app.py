from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'prepost-secret-2024-sma')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///prepost.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Models ───────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    kelas = db.Column(db.String(20))
    no_absen = db.Column(db.String(10))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.relationship('TestResult', backref='user', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(10), nullable=False)  # 'pre' or 'post'
    soal = db.Column(db.Text, nullable=False)
    pilihan_a = db.Column(db.String(300), nullable=False)
    pilihan_b = db.Column(db.String(300), nullable=False)
    pilihan_c = db.Column(db.String(300), nullable=False)
    pilihan_d = db.Column(db.String(300), nullable=False)
    jawaban_benar = db.Column(db.String(1), nullable=False)  # 'a', 'b', 'c', 'd'
    nomor = db.Column(db.Integer)

class Materi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    tipe = db.Column(db.String(10), nullable=False)  # 'video', 'teks', 'audio'
    konten = db.Column(db.Text, nullable=False)
    deskripsi = db.Column(db.Text)
    urutan = db.Column(db.Integer, default=1)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_type = db.Column(db.String(10), nullable=False)
    nilai = db.Column(db.Float, nullable=False)
    jumlah_benar = db.Column(db.Integer)
    total_soal = db.Column(db.Integer)
    jawaban = db.Column(db.Text)  # JSON
    waktu = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Helper ───────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Akses ditolak.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def seed_data():
    if Question.query.count() == 0:
        pre_questions = [
            ("Perubahan fisika adalah perubahan yang...", "Mengubah komposisi zat", "Tidak menghasilkan zat baru", "Menghasilkan zat baru", "Mengubah sifat kimia", "b"),
            ("Air mendidih pada suhu berapa pada tekanan normal?", "90°C", "95°C", "100°C", "110°C", "c"),
            ("Zat yang dapat menghantarkan listrik disebut...", "Isolator", "Konduktor", "Semikonduktor", "Dielektrik", "b"),
            ("Fotosintesis menghasilkan...", "CO2 dan H2O", "O2 dan glukosa", "CO2 dan glukosa", "H2O dan O2", "b"),
            ("Hukum Newton I menyatakan bahwa...", "F = ma", "Benda diam akan tetap diam jika tidak ada gaya", "Aksi = Reaksi", "Gaya sebanding massa", "b"),
        ]
        post_questions = [
            ("Reaksi kimia yang melepaskan panas disebut reaksi...", "Endoterm", "Eksoterm", "Redoks", "Netralisasi", "b"),
            ("Berapa elektron valensi atom Oksigen (O)?", "2", "4", "6", "8", "c"),
            ("Proses pemisahan campuran berdasarkan titik didih berbeda disebut...", "Filtrasi", "Kristalisasi", "Destilasi", "Sublimasi", "c"),
            ("DNA tersusun dari monomer yang disebut...", "Asam amino", "Nukleotida", "Glukosa", "Lipid", "b"),
            ("Sel volta mengubah energi... menjadi energi...", "Listrik → Kimia", "Kimia → Listrik", "Mekanik → Listrik", "Panas → Listrik", "b"),
        ]
        for i, (soal, a, b, c, d, jwb) in enumerate(pre_questions, 1):
            db.session.add(Question(test_type='pre', soal=soal, pilihan_a=a, pilihan_b=b, pilihan_c=c, pilihan_d=d, jawaban_benar=jwb, nomor=i))
        for i, (soal, a, b, c, d, jwb) in enumerate(post_questions, 1):
            db.session.add(Question(test_type='post', soal=soal, pilihan_a=a, pilihan_b=b, pilihan_c=c, pilihan_d=d, jawaban_benar=jwb, nomor=i))

    if Materi.query.count() == 0:
        db.session.add(Materi(judul="Pengantar Kimia SMA", tipe="video", konten="https://www.youtube.com/embed/uVFCOfSuPTo", deskripsi="Video pengantar dasar-dasar ilmu kimia untuk siswa SMA.", urutan=1))
        db.session.add(Materi(judul="Struktur Atom dan Tabel Periodik", tipe="teks", konten="""
<h3>Struktur Atom</h3>
<p>Atom terdiri dari <strong>proton</strong>, <strong>neutron</strong>, dan <strong>elektron</strong>. Proton bermuatan positif (+), neutron tidak bermuatan (netral), dan elektron bermuatan negatif (-).</p>
<h4>Nomor Atom dan Nomor Massa</h4>
<ul>
<li><strong>Nomor Atom (Z)</strong> = jumlah proton dalam inti atom</li>
<li><strong>Nomor Massa (A)</strong> = jumlah proton + neutron</li>
</ul>
<h4>Konfigurasi Elektron</h4>
<p>Elektron menempati kulit-kulit atom berdasarkan aturan tertentu. Kulit K maksimal 2 elektron, kulit L maksimal 8 elektron, kulit M maksimal 18 elektron.</p>
<h3>Tabel Periodik</h3>
<p>Tabel periodik disusun berdasarkan kenaikan nomor atom. Unsur dalam satu golongan memiliki elektron valensi yang sama, sedangkan unsur dalam satu periode memiliki jumlah kulit yang sama.</p>
<blockquote><em>"Sifat-sifat unsur merupakan fungsi periodik dari nomor atomnya." — Dmitri Mendeleev</em></blockquote>
        """, deskripsi="Materi lengkap tentang struktur atom dan tabel periodik unsur.", urutan=2))
        db.session.add(Materi(judul="Podcast: Kimia dalam Kehidupan Sehari-hari", tipe="audio", konten="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", deskripsi="Dengarkan bagaimana kimia berperan dalam kehidupan kita sehari-hari.", urutan=3))

    if not User.query.filter_by(is_admin=True).first():
        db.session.add(User(nama="Administrator", username="admin", password=generate_password_hash("admin123"), is_admin=True))

    db.session.commit()

# ─── Routes: Auth ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['nama'] = user.nama
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        flash('Username atau password salah!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        username = request.form['username']
        password = request.form['password']
        kelas = request.form['kelas']
        no_absen = request.form['no_absen']
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!', 'danger')
            return render_template('register.html')
        user = User(nama=nama, username=username, password=generate_password_hash(password), kelas=kelas, no_absen=no_absen)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Routes: Siswa ────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    pre_result = TestResult.query.filter_by(user_id=user.id, test_type='pre').first()
    post_result = TestResult.query.filter_by(user_id=user.id, test_type='post').first()
    return render_template('dashboard.html', user=user, pre_result=pre_result, post_result=post_result)

@app.route('/pretest', methods=['GET', 'POST'])
@login_required
def pretest():
    user_id = session['user_id']
    existing = TestResult.query.filter_by(user_id=user_id, test_type='pre').first()
    if existing:
        return redirect(url_for('result', test_type='pre'))

    if request.method == 'POST':
        questions = Question.query.filter_by(test_type='pre').order_by(Question.nomor).all()
        jawaban_user = {}
        benar = 0
        for q in questions:
            jawaban = request.form.get(f'q_{q.id}', '')
            jawaban_user[str(q.id)] = jawaban
            if jawaban == q.jawaban_benar:
                benar += 1
        total = len(questions)
        nilai = (benar / total * 100) if total > 0 else 0
        result = TestResult(user_id=user_id, test_type='pre', nilai=nilai, jumlah_benar=benar, total_soal=total, jawaban=json.dumps(jawaban_user))
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('result', test_type='pre'))

    questions = Question.query.filter_by(test_type='pre').order_by(Question.nomor).all()
    return render_template('test.html', questions=questions, test_type='pre', title='Pre-Test')

@app.route('/result/<test_type>')
@login_required
def result(test_type):
    user_id = session['user_id']
    result = TestResult.query.filter_by(user_id=user_id, test_type=test_type).first()
    if not result:
        return redirect(url_for('dashboard'))
    questions = Question.query.filter_by(test_type=test_type).order_by(Question.nomor).all()
    jawaban_user = json.loads(result.jawaban) if result.jawaban else {}
    return render_template('result.html', result=result, questions=questions, jawaban_user=jawaban_user, test_type=test_type)

@app.route('/materi')
@login_required
def materi():
    user_id = session['user_id']
    pre_result = TestResult.query.filter_by(user_id=user_id, test_type='pre').first()
    if not pre_result:
        flash('Selesaikan pre-test terlebih dahulu!', 'warning')
        return redirect(url_for('pretest'))
    materials = Materi.query.order_by(Materi.urutan).all()
    return render_template('materi.html', materials=materials)

@app.route('/posttest', methods=['GET', 'POST'])
@login_required
def posttest():
    user_id = session['user_id']
    pre_result = TestResult.query.filter_by(user_id=user_id, test_type='pre').first()
    if not pre_result:
        flash('Selesaikan pre-test terlebih dahulu!', 'warning')
        return redirect(url_for('pretest'))

    existing = TestResult.query.filter_by(user_id=user_id, test_type='post').first()
    if existing:
        return redirect(url_for('result', test_type='post'))

    if request.method == 'POST':
        questions = Question.query.filter_by(test_type='post').order_by(Question.nomor).all()
        jawaban_user = {}
        benar = 0
        for q in questions:
            jawaban = request.form.get(f'q_{q.id}', '')
            jawaban_user[str(q.id)] = jawaban
            if jawaban == q.jawaban_benar:
                benar += 1
        total = len(questions)
        nilai = (benar / total * 100) if total > 0 else 0
        result = TestResult(user_id=user_id, test_type='post', nilai=nilai, jumlah_benar=benar, total_soal=total, jawaban=json.dumps(jawaban_user))
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('result', test_type='post'))

    questions = Question.query.filter_by(test_type='post').order_by(Question.nomor).all()
    return render_template('test.html', questions=questions, test_type='post', title='Post-Test')

# ─── Routes: Admin ────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_siswa = User.query.filter_by(is_admin=False).count()
    total_pre = TestResult.query.filter_by(test_type='pre').count()
    total_post = TestResult.query.filter_by(test_type='post').count()
    avg_pre = db.session.query(db.func.avg(TestResult.nilai)).filter_by(test_type='pre').scalar() or 0
    avg_post = db.session.query(db.func.avg(TestResult.nilai)).filter_by(test_type='post').scalar() or 0
    return render_template('admin/dashboard.html', total_siswa=total_siswa, total_pre=total_pre, total_post=total_post, avg_pre=round(avg_pre, 1), avg_post=round(avg_post, 1))

@app.route('/admin/siswa')
@admin_required
def admin_siswa():
    students = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    results = {}
    for s in students:
        pre = TestResult.query.filter_by(user_id=s.id, test_type='pre').first()
        post = TestResult.query.filter_by(user_id=s.id, test_type='post').first()
        results[s.id] = {'pre': pre, 'post': post}
    return render_template('admin/siswa.html', students=students, results=results)

@app.route('/admin/hasil')
@admin_required
def admin_hasil():
    data = db.session.query(User, TestResult).join(TestResult, User.id == TestResult.user_id).filter(User.is_admin == False).order_by(User.nama, TestResult.test_type).all()
    
    paired = {}
    for user, result in data:
        if user.id not in paired:
            paired[user.id] = {'user': user, 'pre': None, 'post': None}
        paired[user.id][result.test_type] = result
    return render_template('admin/hasil.html', paired=paired)

@app.route('/admin/soal', methods=['GET', 'POST'])
@admin_required
def admin_soal():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'tambah':
            q = Question(
                test_type=request.form['test_type'],
                soal=request.form['soal'],
                pilihan_a=request.form['pilihan_a'],
                pilihan_b=request.form['pilihan_b'],
                pilihan_c=request.form['pilihan_c'],
                pilihan_d=request.form['pilihan_d'],
                jawaban_benar=request.form['jawaban_benar'],
                nomor=Question.query.filter_by(test_type=request.form['test_type']).count() + 1
            )
            db.session.add(q)
            db.session.commit()
            flash('Soal berhasil ditambahkan!', 'success')
        elif action == 'hapus':
            q = Question.query.get(request.form['id'])
            if q:
                db.session.delete(q)
                db.session.commit()
                flash('Soal dihapus!', 'success')
    pre_q = Question.query.filter_by(test_type='pre').order_by(Question.nomor).all()
    post_q = Question.query.filter_by(test_type='post').order_by(Question.nomor).all()
    return render_template('admin/soal.html', pre_q=pre_q, post_q=post_q)

@app.route('/admin/materi', methods=['GET', 'POST'])
@admin_required
def admin_materi():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'tambah':
            m = Materi(judul=request.form['judul'], tipe=request.form['tipe'], konten=request.form['konten'], deskripsi=request.form['deskripsi'], urutan=Materi.query.count() + 1)
            db.session.add(m)
            db.session.commit()
            flash('Materi berhasil ditambahkan!', 'success')
        elif action == 'hapus':
            m = Materi.query.get(request.form['id'])
            if m:
                db.session.delete(m)
                db.session.commit()
                flash('Materi dihapus!', 'success')
    materials = Materi.query.order_by(Materi.urutan).all()
    return render_template('admin/materi.html', materials=materials)

@app.route('/admin/reset_siswa/<int:user_id>', methods=['POST'])
@admin_required
def reset_siswa(user_id):
    TestResult.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    flash('Data test siswa berhasil direset!', 'success')
    return redirect(url_for('admin_siswa'))

@app.route('/admin/hapus_siswa/<int:user_id>', methods=['POST'])
@admin_required
def hapus_siswa(user_id):
    user = User.query.get(user_id)
    if user and not user.is_admin:
        TestResult.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('Siswa berhasil dihapus!', 'success')
    return redirect(url_for('admin_siswa'))

@app.route('/admin/export')
@admin_required
def admin_export():
    from io import StringIO
    import csv
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nama', 'Username', 'Kelas', 'No. Absen', 'Nilai Pre-Test', 'Nilai Post-Test', 'Selisih', 'Peningkatan'])
    students = User.query.filter_by(is_admin=False).all()
    for s in students:
        pre = TestResult.query.filter_by(user_id=s.id, test_type='pre').first()
        post = TestResult.query.filter_by(user_id=s.id, test_type='post').first()
        pre_val = round(pre.nilai, 1) if pre else '-'
        post_val = round(post.nilai, 1) if post else '-'
        selisih = round(post.nilai - pre.nilai, 1) if pre and post else '-'
        peningkatan = 'Ya' if pre and post and post.nilai > pre.nilai else ('Tidak' if pre and post else '-')
        writer.writerow([s.nama, s.username, s.kelas or '-', s.no_absen or '-', pre_val, post_val, selisih, peningkatan])
    from flask import Response
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=hasil_prepost_test.csv'})

# ─── Init ─────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)
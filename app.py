# Imports
import os

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

# Inicializa o Flask
app = Flask(__name__)
app.secret_key = ''  # Troque por uma chave segura

@app.route('/')
def home():
    return redirect(url_for('login'))

# Função para conectar ao banco
def get_conexao():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
		connection_timeout=5
    )

# Rota: Login (GET e POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
	print("📌 Entrou na rota /login")
	if request.method == 'POST':
		cpf_raw = request.form['cpf'].strip()
		cpf_numbers = ''.join(filter(str.isdigit, cpf_raw))
		if len(cpf_numbers) == 11:
			cpf = cpf_numbers[:9] + '-' + cpf_numbers[9:]
		else:
			cpf = cpf_raw
			
		conexao = get_conexao()
		print("✅ Conectou ao banco com sucesso")
		cursor = conexao.cursor(dictionary=True)

		try:
			cursor.execute("SELECT * FROM professor WHERE CPF = %s", (cpf,))
			professor = cursor.fetchone()
			print("🎯 Resultado da consulta:", professor)
		except mysql.connector.Error as err:
			cursor.close()
			conexao.close()
			return render_template('login.html', erro=f"Erro no banco: {err}")

		cursor.close()
		conexao.close()

		if professor:
			session['cpf'] = professor['cpf']
			return redirect(url_for('dashboard'))
		else:
			return render_template('login.html', erro="CPF não encontrado")

	return render_template('login.html')

# Rota: Dashboard (dados do professor + turmas)
@app.route('/dashboard')
def dashboard():
	if 'cpf' not in session:
		return redirect(url_for('login'))

	cpf = session['cpf']
	conexao = get_conexao()
	cursor = conexao.cursor(dictionary=True)

	cursor.execute("SELECT * FROM professor WHERE CPF = %s", (cpf,))
	professor = cursor.fetchone()

	cursor.execute("SELECT * FROM turma WHERE cpf_prof = %s", (cpf,))
	turmas = cursor.fetchall()

	cursor.close()
	conexao.close()

	return render_template('dashboard.html', professor=professor, turmas=turmas)

# Rota: Visualizar turmas
@app.route('/turmas')
def turmas():
	if 'cpf' not in session:
		return redirect(url_for('login'))

	cpf = session['cpf']
	conexao = get_conexao()
	cursor = conexao.cursor(dictionary=True)

	cursor.execute("SELECT * FROM turma WHERE cpf_prof = %s", (cpf,))
	turmas = cursor.fetchall()

	cursor.close()
	conexao.close()

	return render_template('turmas.html', turmas=turmas)

# Rota: Ver e editar notas dos alunos da turma
@app.route('/turmas/<serie_ano>/alunos', methods=['GET', 'POST'])
def alunos(serie_ano):
	if 'cpf' not in session:
		return redirect(url_for('login'))

	conexao = get_conexao()
	cursor = conexao.cursor(dictionary=True)

	if request.method == 'POST':
		for aluno_id, nota in request.form.items():
			cursor.execute("UPDATE alunos SET nota = %s WHERE id = %s", (nota, aluno_id))
		conexao.commit()

	cursor.execute("SELECT * FROM alunos WHERE ano_serie = %s", (serie_ano,))
	alunos = cursor.fetchall()

	cursor.close()
	conexao.close()

	return render_template('editar_notas.html', alunos=alunos, serie_ano=serie_ano)

# Rota: Logout
@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

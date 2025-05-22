#Teste simples de conexão

import mysql.connector

try:
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',         # coloque aqui seu usuário
        password='Galler1220!@#',         # coloque aqui sua senha (ou deixe vazio se não tiver)
        database= 'escola2025'           #coloque o nome do banco de dados que você criou
    )

    if conexao.is_connected():
        print("✅ Conexão realizada com sucesso!")

    conexao.close()

except mysql.connector.Error as erro:
    print("❌ Erro ao conectar:", erro)
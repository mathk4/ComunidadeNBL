from flask import render_template, redirect, url_for, flash, request, abort
from ComunidadeNBL import app, database, bcrypt
from ComunidadeNBL.forms import Form_Login, Form_CriarConta, Form_EditarPerfil, Form_CriarPost
from ComunidadeNBL.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@app.route("/")
def home():

    posts = Post.query.order_by(Post.id.desc())
    return render_template("home.html", posts=posts)

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/usuarios")
@login_required
def usuarios():
    return render_template("usuarios.html", lista_usuarios=Usuario.query.all())

@app.route("/login", methods=['GET', 'POST'])
def login_CriarConta():
    form_login = Form_Login()
    form_criarconta = Form_CriarConta()

    if form_login.validate_on_submit() and 'botao_enviar_login' in request.form:

        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for("home"))
        else:
            flash('E-mail ou senha inválidos. Tente novamente.', 'alert-danger')
            return redirect(url_for("login_CriarConta"))

    
    if form_criarconta.validate_on_submit() and 'botao_enviar_criarconta' in request.form:
        senha_criptografada = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(nome_usuario= form_criarconta.nome_usuario.data, email= form_criarconta.email.data, senha= senha_criptografada)
        database.session.add(usuario)
        database.session.commit()
        
        flash(f'Conta criada com sucesso no e-mail {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for("home"))
    
    return render_template('login_e_CriarConta.html', form_login= form_login, form_criarconta=form_criarconta)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash('Você saiu com sucesso.', 'alert-success')
    return redirect(url_for("home"))

@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for('static', filename='foto_perfil/{}'.format(current_user.foto_perfil))
    return render_template("perfil.html", foto_perfil=foto_perfil)

@app.route("/post/criar", methods=['GET', 'POST'])
@login_required
def criar_post():
    form = Form_CriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.conteudo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso!', 'alert-success')
        return redirect(url_for("home"))
    return render_template("criar_post.html", form=form)


def salvar_foto_perfil(foto):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(foto.filename)
    novo_nome = nome + codigo + extensao #extensao é jpg, png, etc.
    caminho = os.path.join(app.root_path, 'static', 'foto_perfil', novo_nome)

    tamanho = (200, 200) #tamanho máximo da foto do perfil
    foto_redusida = Image.open(foto)
    foto_redusida.thumbnail(tamanho)

    foto_redusida.save(caminho)
    return novo_nome

def salvar_ranks_usuario(form_editarperfil):
    lista_ranks = []
    for campo in form_editarperfil:
        if "rank_" in campo.name:
            if campo.data:
                lista_ranks.append(campo.label.text)
    return ";".join(lista_ranks)

@app.route("/perfil/editar", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form_editarperfil = Form_EditarPerfil()

    if form_editarperfil.validate_on_submit():
        current_user.nome_usuario = form_editarperfil.nome_usuario.data
        current_user.email = form_editarperfil.email.data

        if form_editarperfil.foto_perfil.data:
            nome_foto = salvar_foto_perfil(form_editarperfil.foto_perfil.data)
            current_user.foto_perfil = nome_foto
        
        current_user.ranks = salvar_ranks_usuario(form_editarperfil)

        database.session.commit()
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for("perfil"))
    elif request.method == 'GET':
        form_editarperfil.nome_usuario.data = current_user.nome_usuario
        form_editarperfil.email.data = current_user.email

    foto_perfil = url_for('static', filename='foto_perfil/{}'.format(current_user.foto_perfil))
    return render_template("editar_perfil.html", foto_perfil=foto_perfil, form_editarperfil=form_editarperfil)

@app.route("/post/<post_id>", methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)

    if current_user ==  post.autor:
        form = Form_CriarPost()
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.conteudo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.conteudo.data
            database.session.commit()
    else:
        form = None

    return render_template("post.html", post=post, form=form)

@app.route("/post/<post_id>/excluir", methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluído com sucesso.', 'alert-danger')
        return redirect(url_for("home"))
    else:
        abort(403)


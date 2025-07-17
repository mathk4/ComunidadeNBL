from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import data_required, length, email, equal_to, ValidationError
from ComunidadeNBL.models import Usuario
from flask_login import current_user

class Form_CriarConta(FlaskForm):
    nome_usuario = StringField("Nome de usuário", validators=[data_required()])
    email = StringField("E-Mail", validators=[data_required(), email()])
    senha = PasswordField("Senha", validators=[data_required(), length(min= 8)])
    senha_confirmacao = PasswordField("Confirmar senha", validators=[data_required(), equal_to("senha")])
    botao_enviar_criarconta = SubmitField("Criar Conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado. Por favor, escolha outro e-mail.")


class Form_Login(FlaskForm):
    email = StringField("E-Mail", validators=[data_required(), email()])
    senha = PasswordField("Senha", validators=[data_required()])
    lembrar_dados = BooleanField("Lembrar dados de Acesso") 
    botao_enviar_login = SubmitField("Fazer Login")

class Form_EditarPerfil(FlaskForm):
    nome_usuario = StringField("Nome de usuário", validators=[data_required()])
    email = StringField("E-Mail", validators=[data_required(), email()])
    foto_perfil = FileField("Atualizar foto de perfil", validators=[FileAllowed(['jpg', 'png', 'jpeg'], "Somente imagens são permitidas.")])

    rank_bronze = BooleanField("Rank Bronze")
    rank_prata = BooleanField("Rank Prata")
    rank_ouro = BooleanField("Rank Ouro")
    rank_diamante = BooleanField("Rank Diamante")
    rank_mitico = BooleanField("Rank Mítico")
    rank_lendario = BooleanField("Rank Lendário")
    rank_mestre = BooleanField("Rank Mestre")
    rank_pro = BooleanField("Rank Pro")

    botao_enviar_editarperfil = SubmitField("Salvar Alterações")
    
    def validate_email(self, email):
        if email.data != current_user.email:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError("E-mail já cadastrado. Por favor, escolha outro e-mail.")
            
class Form_CriarPost(FlaskForm):
    titulo = StringField("Título", validators=[data_required(), length(min=2, max=100)])
    conteudo = TextAreaField("Escreva seu post aqui", validators=[data_required()])
    botao_enviar_criarpost = SubmitField("Criar Post")
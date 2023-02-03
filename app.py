#  Alunos:
#  Renzo Prats Silva Souza  -  11921ECP004
#  Guilherme Gabriel Ferreira Souza - 11921ECP001

from flask import Flask, Response, request, session
from flask_sqlalchemy import SQLAlchemy
import json
import os
from datetime import datetime, timedelta

#Configurando a aplicação flask e o banco de dados
app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{os.path.abspath("")}/companhia_area.db'
app.secret_key = 'A123JANAJWNE923'

db = SQLAlchemy(app)

#Criando o Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
 
#Criando o objeto Aeroporto
class Aeroporto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), unique=True)
    localizacao = db.Column(db.String(200))
    
    #metodo que converte os campos do objeto em json
    def to_json(self):
        return {"id": self.id, "nome": self.nome, "localizacao": self.localizacao}

#Criando o objeto Voo
class Voo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origem = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)
    destino = db.Column(db.Integer, db.ForeignKey('aeroporto.id'), nullable=False)
    tarifa = db.Column(db.Float)
    horario_saida = db.Column(db.String(16))
    horario_chegada = db.Column(db.String(16))
    quantidade = db.Column(db.Integer)
    
    #metodo que converte os campos do objeto em json
    def to_json(self):
        return {
            "id": self.id, 
            "origem": self.origem, 
            "destino": self.destino,
            "tarifa": self.tarifa,
            "horario_saida": self.horario_saida,
            "horario_chegada": self.horario_chegada,
            "quantidade":self.quantidade
        }

#Criando o objeto Compras
class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voo = db.Column(db.Integer, db.ForeignKey('voo.id'), nullable=False)
    #substituir depois de implementar o usuario
    comprador = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    numero_voucher = db.Column(db.String(20))
    quantidade = db.Column(db.Integer)
    
    #metodo que converte os campos do objeto em json
    def to_json(self):
        return {
            "id": self.id, 
            "numero_voucher": self.numero_voucher
        }

# db.drop_all()
# db.create_all()

#funcao que gera o response
def generate_response(status, content_name, content, mensagem=False):
    body = {}
    body[content_name] = content
     
    if mensagem:
        body["mensagem"] = mensagem
        
    return Response(json.dumps(body), status=status, mimetype="application/json")

#ROUTES

@app.route("/login", methods=["POST"])
def login():
    try:
        body = request.get_json()
        username = body["username"]
        password = body["password"]

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return generate_response(200, "usuario", {}, "Login efetuado com sucesso!")
        else:
            return generate_response(400, "usuario", {}, "Usuário e/ou senha estão incorretos!")
    
    except:
        return generate_response(400, "usuario", {}, "Erro ao efetuar login")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return generate_response(200, "usuario", {}, "Logout efetuado com sucesso!")

@app.route("/cadastrar", methods=["POST"])
def cadastrar():
    body = request.get_json()
    
    try:
        usuario = User(username=body["username"], password=body["password"])
        db.session.add(usuario)
        db.session.commit()
        session["username"] = usuario.username
        
        return generate_response(201, "usuario", {}, "Usuário criado com sucesso")
    
    except:
        return generate_response(400, "usuario", {}, "Erro ao criar usuário")

#Routes do Aeroporto
#route /aeroportos retorna todos aeroportos
@app.route("/aeroportos", methods=["GET"])
def select_aeroportos():
    try:
        aeroportos_objects = Aeroporto.query.all()
        aeroportos_json = [aeroporto.to_json() for aeroporto in aeroportos_objects]
        

        return generate_response(200, "aeroportos", aeroportos_json, "OK")
    
    except:
        return generate_response(400, "aeroportos", {}, "Erro ao filtrar os aeroportos")

#route /aeroportos/<id> retorna os aeroportos pela origem
@app.route("/aeroportos/<origem>", methods=["GET"])
def select_aeroportos_origem(origem):
    aeroportos_objects = Aeroporto.query.filter_by(localizacao=origem)
    
    try:
        aeroportos_json = [aeroporto.to_json() for aeroporto in aeroportos_objects]
        
        
        return generate_response(200, "aeroportos", aeroportos_json, "OK")
    
    except:
        return generate_response(400, "aeroportos", {}, "Erro ao filtrar os aeroporto pela origem")

#route /aeroporto cria um aeroporto pelo metodo HTTP POST
@app.route("/aeroporto", methods=["POST"])
def create_aeroporto():
    body = request.get_json()
    
    try:
        if session['username']:
            aeroporto = Aeroporto(nome=body["nome"], localizacao=body["localizacao"])
            db.session.add(aeroporto)
            db.session.commit()
            
            
            return generate_response(201, "aeroporto", aeroporto.to_json(), "Aeroporto criado com sucesso")

        else:
            return generate_response(400, "aeroporto", {}, "Erro ao criar aeroporto")
    
    except:
        return generate_response(400, "aeroporto", {}, "Erro ao criar aeroporto")

#route /aeroporto/<id> atualiza um aeroporto pelo metodo HTTP PUT
@app.route("/aeroporto/<id>", methods=["PUT"])
def update_aeroporto(id):
    aeroporto_object = Aeroporto.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if session['username']:  
            if('nome' in body):
                aeroporto_object.nome = body['nome']
            if('localizacao' in body):
                aeroporto_object.localizacao = body['localizacao']
            
            db.session.add(aeroporto_object)
            db.session.commit()
            
            
            return generate_response(200, "aeroporto", aeroporto_object.to_json(), "Aeroporto atualizado com sucesso")
        else:
            return generate_response(400, "aeroporto", {}, "Erro ao atualizar aeroporto")
    
    except:
        return generate_response(400, "aeroporto", {}, "Erro ao atualizar aeroporto")

#route /aeroporto/<id> deleta um aeroporto pelo metodo HTTP DELETE
@app.route("/aeroporto/<id>", methods=["DELETE"])
def delete_aeroporto(id):
    aeroporto_object = Aeroporto.query.filter_by(id=id).first()
    
    try:
        if session['username']:
            db.session.delete(aeroporto_object)
            db.session.commit()
            
            
            return generate_response(200, "aeroporto", aeroporto_object.to_json(), "Aeroporto deletado com sucesso")
        else:
            return generate_response(400, "aeroporto", {}, "Erro ao deletar aeroporto")
    
    except:
        return generate_response(400, "aeroporto", {}, "Erro ao deletar aeroporto")

#Routes do Voo
#route /voos retorna todos voos
@app.route("/voos", methods=["GET"])
def select_voos():
    try:
        voo_objects = Voo.query.all()
        voo_json = [voo.to_json() for voo in voo_objects]
        

        return generate_response(200, "voos", voo_json, "OK")
    
    except:
        return generate_response(400, "voos", {}, "Erro ao filtrar os voos")

#route /voo/<id> retorna o voo pelo id
@app.route("/voo/<id>", methods=["GET"])
def select_voo(id):
    voo_object = Voo.query.filter_by(id=id).first()
    
    try:
        voo_object = voo_object.to_json()        
        return generate_response(200, "voo", voo_object, "OK")
    
    except:
        return generate_response(400, "voo", {}, "Erro ao filtrar o voo pelo id")

#route /voos retorna os voos pela data
@app.route("/voos/<data>", methods=["GET"])
def select_voos_data(data):
    try:        
        voo_objects = Voo.query.all()
        voo_objects = [v for v in voo_objects if v.horario_saida.replace('/','').replace(':','').replace(' ','')[0:8] == data]
        voo_json = [voo.to_json() for voo in voo_objects]
        

        return generate_response(200, "voos", voo_json, "OK")
    
    except:
        return generate_response(400, "voos", {}, "Erro ao filtrar os voos pela data")
    
#route /voos retorna os voos mais baratos pela quantidade de pessoas
@app.route("/pesquisar_voos/<quantidade>", methods=["GET"])
def pesquisar_voos(quantidade):
    try:
        if session['username']:
            voo_objects = Voo.query.order_by(Voo.tarifa).all()
            voo_objects = [voo for voo in voo_objects if voo.quantidade >= int(quantidade)]
            voo_json = [voo.to_json() for voo in voo_objects]
            voo_json = voo_json[0]
            

            return generate_response(200, "voos", voo_json, "OK")
        else:
            return generate_response(400, "voos", {}, "Erro ao pesquisar os voos")
    
    except:
        return generate_response(400, "voos", {}, "Erro ao pesquisar os voos")
    
#route /voo cria um voo pelo metodo HTTP POST
@app.route("/voo", methods=["POST"])
def create_voo():
    body = request.get_json()
    
    try:
        if session['username']:
            voo = Voo(origem=int(body["origem"]), destino=int(body["destino"]), tarifa=float(body["tarifa"]), horario_saida=body["horario_saida"],
                        horario_chegada=body["horario_chegada"], quantidade=int(body["quantidade"])  
                    )
            db.session.add(voo)
            db.session.commit()
            
            
            return generate_response(201, "voo", voo.to_json(), "Voo criado com sucesso")
        else:
            return generate_response(400, "voo", {}, "Erro ao criar voo")
    
    except:
        return generate_response(400, "voo", {}, "Erro ao criar voo")

#route /voo/<id> atualiza um voo pelo metodo HTTP PUT
@app.route("/voo/<id>", methods=["PUT"])
def update_voo(id):
    voo_object = Voo.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if session['username']:
            if('origem' in body):
                voo_object.origem = int(body['origem'])
            if('destino' in body):
                voo_object.destino = int(body['destino'])
            if('tarifa' in body):
                voo_object.tarifa = float(body['tarifa'])
            if('horario_saida' in body):
                voo_object.horario_saida = body['horario_saida']
            if('horario_chegada' in body):
                voo_object.horario_chegada = body['horario_chegada']
            if('quantidade' in body):
                voo_object.quantidade = int(body['quantidade'])
            
            db.session.add(voo_object)
            db.session.commit()
            
            
            return generate_response(200, "voo", voo_object.to_json(), "Voo atualizado com sucesso")
        else:
            return generate_response(400, "voo", {}, "Erro ao atualizar voo")
    
    except:
        return generate_response(400, "voo", {}, "Erro ao atualizar voo")

#route /aeroporto/<id> deleta um aeroporto pelo metodo HTTP DELETE
@app.route("/voo/<id>", methods=["DELETE"])
def delete_voo(id):
    voo_object = Voo.query.filter_by(id=id).first()
    
    try:
        if session['username']:
            db.session.delete(voo_object)
            db.session.commit()
            
            
            return generate_response(200, "voo", voo_object.to_json(), "Voo deletado com sucesso")
        else:
            return generate_response(400, "voo", {}, "Erro ao deletar voo")
    except:
        return generate_response(400, "voo", {}, "Erro ao deletar voo")    

#Routes da compra
@app.route("/compras", methods=["GET"])
def select_compras():
    try:
        compras_objects = Compra.query.all()
        compra_json = [compra.to_json() for compra in compras_objects]
        

        return generate_response(200, "compras", compra_json, "OK")
    
    except:
        return generate_response(400, "compras", {}, "Erro ao filtrar as compras")
    
@app.route("/compra", methods=["POST"])
def create_compra():
    body = request.get_json()
    
    try:
        if session['username']:
            #ajusta a quantidade de vagas no voo
            voo = Voo.query.filter_by(id=body["voo"])[0]
            if(voo.quantidade >= body["quantidade"]):
                voo.quantidade = voo.quantidade - body["quantidade"]
                db.session.add(voo)
                db.session.commit()
            else:
                raise Exception()
            
            compra = Compra(voo = body["voo"], comprador = body["comprador"], numero_voucher = body["numero_voucher"], quantidade=body["quantidade"])
            db.session.add(compra)
            db.session.commit()
            
            return generate_response(201, "compra", compra.to_json(), "Compra criado com sucesso")
        else:
            return generate_response(400, "compra", {}, "Erro ao criar compra")
    except:
        return generate_response(400, "compra", {}, "Erro ao criar compra")

@app.route("/compra/<id>", methods=["DELETE"])
def delete_compra(id):
    compra_object = Compra.query.filter_by(id=id).first()
    
    try:
        if session['username']:
            db.session.delete(compra_object)
            db.session.commit()
            
            
            return generate_response(200, "compra", compra_object.to_json(), "Compra deletada com sucesso")
        else:
            return generate_response(400, "compra", {}, "Erro ao deletar compra")
    except:
        return generate_response(400, "compra", {}, "Erro ao deletar compra")
    
#roda o app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
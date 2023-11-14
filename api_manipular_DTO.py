import json
from flask import Flask, request, make_response
from flask_cors import CORS
import io

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def abrirArquivo(nome):
    with open(nome, 'r') as file:
        return json.load(file)


config_gerais_ex = abrirArquivo('config_geral.json')


def validar_json(json_inval):
    try:
        id_cotacao = json_inval["id_cotacao"]
        multipla_resposta = json_inval["config_geral"]["multipla_resposta"]["multipla"]
        compra_conjunta = json_inval["config_geral"]["compra_conjunta"]
        qtd_problema_de_minimo = json_inval["config_produto"]['qtd_problema_de_minimo']
        qtd_problema_de_embalagem = json_inval["config_produto"]['qtd_problema_de_embalagem']
        oportunidades = json_inval["config_produto"]['oportunidades']
        oportunidades_fixada = json_inval["config_produto"]['oportunidades_fixada']
        produtos_sem_st = json_inval["config_produto"]['produtos_sem_st']
        so_com_st = json_inval["config_produto"]['so_com_st']
        sem_estoque = json_inval["config_produto"]['sem_estoque']
        resposta_parcial_em_porcentagem = json_inval["config_geral"]['resposta_parcial_em_porcentagem']
        minimo_de_faturamento = json_inval["config_geral"]['minimo_de_faturamento']
        if all([id_cotacao,
                qtd_problema_de_minimo or qtd_problema_de_minimo == 0,
                qtd_problema_de_embalagem or qtd_problema_de_embalagem == 0,
                oportunidades or oportunidades == 0,
                oportunidades_fixada or oportunidades_fixada == 0,
                produtos_sem_st or produtos_sem_st == 0,
                so_com_st or so_com_st == 0,
                multipla_resposta in [True, False],
                compra_conjunta in [True, False],
                sem_estoque in [True, False],
                resposta_parcial_em_porcentagem in [True, False],
                not minimo_de_faturamento or minimo_de_faturamento > 0]):
            return True
    except ValueError:
        return False


def gravar_na_fila(mensagem_json):
    try:
        with io.open('fila.json', 'r', encoding='utf-8') as file:
            lista_atual = json.load(file)
            lista_atual.append(mensagem_json)
            file.close()
            with open('fila.json', 'w', encoding='utf-8') as f:
                json.dump(lista_atual, f, ensure_ascii=False)
                f.close()
        return True
    except ValueError:
        return


def responder():
    return make_response({'result': 'resposta enviada para a API com sucesso'}, 200)


@app.route('/', methods=['GET', ])
def ok():
    return make_response({'result': 'API rodando'}, 200)


@app.route('/example', methods=['GET', ])
def example():
    return make_response(config_gerais_ex, 200)


@app.route('/manipular_DTO', methods=['POST', ])
def manipular_DTO():
    try:
        body = request.get_data()
        config_gerais = json.loads(body)
        if validar_json(config_gerais):
            if gravar_na_fila(config_gerais):
                return responder()
            else:
                return responder()
        else:
            return make_response({'result': 'json inesperado, siga o json de exemplo'}, 400)
    except Exception as E:
        print(E)
        return make_response({'result': 'json inesperado, siga o json de exemplo'}, 400)


app.run(host='0.0.0.0', port=80)

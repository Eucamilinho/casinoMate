from flask import Flask, render_template, request, jsonify
import random
import itertools

app = Flask(__name__)

# =============================
#      FUNCIONES DEL JUEGO
# =============================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ruleta', methods=['POST'])
def ruleta_modular():
    data = request.json
    modulo = int(data['modulo'])
    apuesta = int(data['apuesta'])
    
    numero = random.randint(0, 35)
    resultado_mod = numero % modulo
    gano = resultado_mod == apuesta
    
    return jsonify({
        'numero': numero,
        'resultado_mod': resultado_mod,
        'gano': gano,
        'explicacion': {
            'division': numero // modulo,
            'formula': f"{numero} = {modulo} × {numero // modulo} + {resultado_mod}"
        }
    })

@app.route('/api/dados', methods=['POST'])
def dados_probabilidad():
    data = request.json
    tipo_apuesta = int(data['tipo'])
    suma_exacta = data.get('suma_exacta', 7)
    
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    suma = d1 + d2
    
    gano = False
    mensaje = ''
    
    if tipo_apuesta == 1:
        gano = suma == suma_exacta
        mensaje = f'Apostaste a {suma_exacta}'
    elif tipo_apuesta == 2:
        gano = suma % 2 == 0
        mensaje = 'Apostaste a PAR'
    elif tipo_apuesta == 3:
        gano = suma % 2 == 1
        mensaje = 'Apostaste a IMPAR'
    
    # Calcular probabilidades
    combinaciones_posibles = 36
    if tipo_apuesta == 1:
        formas_de_obtener = calcular_formas_suma(suma_exacta)
        probabilidad = f"{formas_de_obtener}/36"
    else:
        probabilidad = "18/36 (50%)"
    
    return jsonify({
        'd1': d1,
        'd2': d2,
        'suma': suma,
        'gano': gano,
        'mensaje': mensaje,
        'probabilidad': probabilidad
    })

@app.route('/api/blackjack/iniciar', methods=['POST'])
def iniciar_blackjack():
    cartas = list(range(1, 11))
    jugador = random.sample(cartas, 2)
    dealer = random.sample(cartas, 2)
    
    # Calcular combinaciones posibles
    combinaciones = list(itertools.combinations(cartas, 2))
    
    return jsonify({
        'jugador': jugador,
        'dealer': dealer,
        'suma_jugador': sum(jugador),
        'combinaciones_totales': len(combinaciones),
        'terminado': False
    })

@app.route('/api/blackjack/pedir', methods=['POST'])
def pedir_carta_blackjack():
    data = request.json
    jugador = data['jugador']
    dealer = data['dealer']
    
    cartas = list(range(1, 11))
    nueva = random.choice(cartas)
    jugador.append(nueva)
    
    suma_jugador = sum(jugador)
    terminado = suma_jugador > 21
    
    resultado = None
    if terminado:
        resultado = {
            'mensaje': '¡Te pasaste! Pierdes',
            'tipo': 'lose'
        }
    
    return jsonify({
        'jugador': jugador,
        'dealer': dealer,
        'suma_jugador': suma_jugador,
        'nueva_carta': nueva,
        'terminado': terminado,
        'resultado': resultado
    })

@app.route('/api/blackjack/plantarse', methods=['POST'])
def plantarse_blackjack():
    data = request.json
    jugador = data['jugador']
    dealer = data['dealer']
    
    suma_jugador = sum(jugador)
    suma_dealer = sum(dealer)
    
    if suma_jugador > 21:
        mensaje = '¡Te pasaste! Pierdes'
        tipo = 'lose'
    elif suma_dealer > 21 or suma_jugador > suma_dealer:
        mensaje = '¡Ganaste!'
        tipo = 'win'
    elif suma_jugador == suma_dealer:
        mensaje = 'Empate'
        tipo = 'tie'
    else:
        mensaje = 'Perdiste'
        tipo = 'lose'
    
    return jsonify({
        'jugador': jugador,
        'dealer': dealer,
        'suma_jugador': suma_jugador,
        'suma_dealer': suma_dealer,
        'terminado': True,
        'resultado': {
            'mensaje': mensaje,
            'tipo': tipo
        }
    })

# =============================
#      FUNCIONES AUXILIARES
# =============================

def calcular_formas_suma(n):
    """Calcula de cuántas formas se puede obtener una suma con 2 dados"""
    formas = 0
    for i in range(1, 7):
        for j in range(1, 7):
            if i + j == n:
                formas += 1
    return formas

if __name__ == '__main__':
    app.run(debug=True, port=5000)
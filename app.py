# app.py

from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template("inicio.html")

@app.route('/buscador', methods=['GET', 'POST'])
def buscador():
    ruta_archivo = 'static/js/nba.json'
    with open(ruta_archivo, 'r') as archivo:
        datos_json = json.load(archivo)

    jugadores = datos_json.get("players", [])
    
    # Obtener posiciones únicas de los jugadores
    posiciones = set(jugador.get('pos') for jugador in jugadores)

    if request.method == 'POST':
        nombre_jugador = request.form['nombre']
        posicion = request.form['posicion']

        if not nombre_jugador and not posicion:  # Si no se introduce nada en ninguno de los dos buscadores
            resultados = jugadores
        else:
            resultados = []
            for jugador in jugadores:
                nombre_coincide = 'name' in jugador and jugador['name'].lower().startswith(nombre_jugador.lower())
                posicion_coincide = jugador.get('pos') == posicion
                if nombre_coincide and posicion_coincide:
                    resultados.append(jugador)
            if not resultados:  # Si no se encuentran resultados
                if nombre_jugador and not posicion:
                    return render_template('buscador.html', posiciones=posiciones, resultados=[], error="Por favor, selecciona una posición válida.")
                else:
                    return render_template('buscador.html', posiciones=posiciones, resultados=[], error="No se encontraron jugadores con esa combinación de nombre y posición.")
        return render_template('buscador.html', posiciones=posiciones, resultados=resultados)
    
    # Si la solicitud es GET o si no se ha enviado ningún formulario, simplemente mostrar el formulario de búsqueda
    return render_template('buscador.html', posiciones=posiciones)

@app.route('/jugador/<nombre>')
def jugador(nombre):
    ruta_archivo = 'static/js/nba.json'
    try:
        with open(ruta_archivo, 'r') as archivo:
            datos_json = json.load(archivo)
    except FileNotFoundError:
        # Si el archivo no se encuentra, abortar con un error 404
        abort(404)

    jugadores = datos_json.get("players", [])
    
    for jugador in jugadores:
        if jugador.get('name') == nombre:
            return render_template('jugador.html', jugador=jugador)
    
    # Si el jugador no se encuentra, mostrar mensaje de error y enlace para volver al inicio
    mensaje_error = f"El jugador '{nombre}' no ha sido encontrado. <a href='/'>Volver al inicio</a>"
    return mensaje_error, 404

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)

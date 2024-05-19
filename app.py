# app.py

from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template("inicio.html")

@app.route('/pilotos')
def pilotos():
    api_url = "https://api.openf1.org/v1/drivers?session_key=9510"
    response = requests.get(api_url)
    if response.status_code == 200:
        drivers = response.json()
    else:
        drivers = []
    return render_template("pilotos.html", drivers=drivers)


# app.py

@app.route('/circuitos', methods=['GET'])
def circuitos():
    meetings = []

    circuito = request.args.get('circuito')
    selected_circuito = None

    if circuito:
        # Si se envió el formulario de búsqueda
        api_url = f"https://api.openf1.org/v1/meetings?year=2023&meeting_name={circuito}"
        response = requests.get(api_url)
        if response.status_code == 200:
            selected_circuito = response.json()
    else:
        # Si no se envió el formulario de búsqueda, obtener la lista de todos los circuitos
        api_url = "https://api.openf1.org/v1/meetings?year=2023"
        response = requests.get(api_url)
        if response.status_code == 200:
            meetings = response.json()

    return render_template("circuitos.html", meetings=meetings, selected_circuito=selected_circuito)



@app.route('/detalles_circuito/<meeting_key>')
def detalles_circuito(meeting_key):
    api_url = f"https://api.openf1.org/v1/meetings?year=2023&meeting_key={meeting_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        circuito_info = response.json()
        return render_template("detalles.html", circuito=circuito_info)
    else:
        return "Error al obtener detalles del circuito"

@app.route('/radio')
def radio():
    return render_template("radio_control.html")

@app.route('/tiempo')
def tiempo():
    return render_template("tiempo.html")

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)

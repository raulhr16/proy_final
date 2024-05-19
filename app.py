from flask import Flask, render_template, request, url_for
import requests
import os
from datetime import datetime, timedelta

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

@app.route('/circuitos', methods=['GET'])
def circuitos():
    api_url = "https://api.openf1.org/v1/meetings?year=2023"
    response = requests.get(api_url)
    if response.status_code == 200:
        granp = response.json()
    else:
        granp = []

    circuito = request.args.get('circuito')
    meetings = []

    if circuito is not None:  # Se ha enviado el formulario
        if circuito:  # Si se seleccionó un circuito específico
            meetings = [meeting for meeting in granp if meeting['meeting_name'] == circuito]
        else:  # Si no se seleccionó ningún circuito
            meetings = granp

    return render_template("circuitos.html", meetings=meetings, granp=granp, buscado=(circuito is not None))

@app.route('/detalles_circuito/<int:circuit_key>')
def detalles_circuito(circuit_key):
    api_url = f"https://api.openf1.org/v1/meetings?year=2023&circuit_key={circuit_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        circuitos = response.json()
        if not circuitos:
            return render_template("error.html", mensaje="El circuito no existe o no se encontró.")
        
        circuito = circuitos[0]  # Suponiendo que la API devuelve una lista de un ítem

        # Obtener información del clima
        ciudad = circuito["location"]
        date_start = circuito["date_start"]
        formato_fecha = "%Y-%m-%dT%H:%M:%S%z"
        inicio = datetime.strptime(date_start, formato_fecha)
        final = inicio + timedelta(hours=3)
        inicio_str = inicio.strftime("%Y-%m-%d:%H")
        final_str = final.strftime("%Y-%m-%d:%H")

        clave_api = os.environ.get('clave_tiempo_api')
        url2 = f"https://api.weatherbit.io/v2.0/history/hourly?city={ciudad}&start_date={inicio_str}&end_date={final_str}&tz=local&key={clave_api}"
        respuesta = requests.get(url2)
        datos2_json = respuesta.json()

        weather_data = datos2_json.get('data', [])

        return render_template("detalles_circuito.html", circuito=circuito, weather_data=weather_data)
    else:
        return render_template("error.html", mensaje="Error al obtener detalles del circuito.")

@app.route('/radio', methods=['GET'])
def radio():
    error = None
    race_control_data = None
    team_radio_data = []
    
    driver_number = request.args.get('driver_number')
    
    if driver_number is not None:
        if not driver_number.isdigit() or int(driver_number) < 1 or int(driver_number) > 99:
            error = "Por favor, introduce un número del 1 al 99."
        else:
            api_url = f"https://api.openf1.org/v1/race_control?driver_number={driver_number}"
            response = requests.get(api_url)
            if response.status_code == 200:
                race_control_data = response.json()
                
                if not race_control_data:
                    error = "No hay información disponible para el número de piloto proporcionado."
                else:
                    for data in race_control_data:
                        session_key = data['session_key']
                        api_url_team_radio = f"https://api.openf1.org/v1/team_radio?session_key={session_key}&driver_number={driver_number}"
                        response_team_radio = requests.get(api_url_team_radio)
                        if response_team_radio.status_code == 200:
                            team_radio_data.extend(response_team_radio.json())
                        else:
                            team_radio_data = []
            else:
                error = "No hay información disponible para el número de piloto proporcionado."
    
    return render_template("radio.html", race_control_data=race_control_data, team_radio_data=team_radio_data, error=error, driver_number=driver_number)



@app.route('/tiempo')
def tiempo():
    return render_template("tiempo.html")

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)

from flask import Flask, render_template, request, jsonify
import random
import qrcode

app = Flask(__name__)

def generar_primer_digito(fecha_nacimiento):
    # Obtener el año de nacimiento
    anio = int(fecha_nacimiento[:4])

    if anio <= 1999:
        return str(random.randint(0, 9)) 
    else:
        return random.choice('A') 

def calcular_digito_verificador(curp_sin_verificador):
    caracteres_validos = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ'
    equivalencias = {char: index for index, char in enumerate(caracteres_validos)}
    suma = 0
    for i, char in enumerate(curp_sin_verificador):
        suma += equivalencias[char] * (18 - i)
    residuo = suma % 10
    if residuo == 0:
        return '0'
    else:
        return str(10 - residuo)

def generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado):
    curp = ''

    curp += apellido_paterno[0].upper()

    for letra in apellido_paterno[1:]:
        if letra.upper() in 'AEIOU':
            curp += letra.upper()
            break

    curp += apellido_materno[0]

    curp += nombre[0]

    curp += fecha_nacimiento[2:4]  

    mes = fecha_nacimiento[5:7]
    curp += mes

    curp += fecha_nacimiento[8:10]  

    curp += sexo

    curp += estado

    for letra in apellido_paterno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    for letra in apellido_materno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    for letra in nombre[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    primer_digito = generar_primer_digito(fecha_nacimiento)

    curp += primer_digito

    segundo_digito_verificador = calcular_digito_verificador(curp)

    curp += segundo_digito_verificador

    return curp

@app.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        fecha_nacimiento = request.form['fecha_nacimiento']
        sexo = request.form['sexo']
        estado = request.form['estado']

        curp_generada = generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado)
        print("La CURP generada es:", curp_generada)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(curp_generada)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_file = "static/curp_qr.png"
        img.save(img_file)

        return jsonify({'curp': curp_generada, 'qr_img': img_file})
    else:
        return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)

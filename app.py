from flask import Flask, render_template, request, jsonify
import random
import qrcode

app = Flask(__name__)

# Función para generar el primer dígito de la homoclave
def generar_primer_digito(fecha_nacimiento):
    # Obtener el año de nacimiento
    anio = int(fecha_nacimiento[:4])

    # Determinar si el año es hasta 1999 o a partir de 2000
    if anio <= 1999:
        return str(random.randint(0, 9))  # Para fechas de nacimiento hasta el año 1999 (0-9)
    else:
        return random.choice('A') # Para fechas de nacimiento a partir del año 2000 (A-Z)

# Función para calcular el segundo dígito verificador del CURP
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

# Función para generar una CURP válida
def generar_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado):
    curp = ''

    # Primer letra del apellido paterno (en mayúsculas)
    curp += apellido_paterno[0].upper()

    # Primera vocal del apellido paterno (en mayúsculas)
    for letra in apellido_paterno[1:]:
        if letra.upper() in 'AEIOU':
            curp += letra.upper()
            break

    # Primer letra del apellido materno
    curp += apellido_materno[0]

    # Primer letra del nombre
    curp += nombre[0]

    # Año de nacimiento (últimos dos dígitos)
    curp += fecha_nacimiento[2:4]  # Se toman los últimos dos dígitos del año

    # Mes de nacimiento
    mes = fecha_nacimiento[5:7]
    curp += mes

    # Día de nacimiento
    curp += fecha_nacimiento[8:10]  # Se toman los dos últimos dígitos del día

    # Sexo
    curp += sexo

    # Entidad federativa de nacimiento
    curp += estado

    # Primer consonante interna del apellido paterno
    for letra in apellido_paterno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    # Primer consonante interna del apellido materno
    for letra in apellido_materno[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    # Primer consonante interna del nombre
    for letra in nombre[1:]:
        if letra.upper() not in 'AEIOU':
            curp += letra.upper()
            break

    # Generar el primer dígito de la homoclave
    primer_digito = generar_primer_digito(fecha_nacimiento)

    # Agregar primer dígito a la CURP
    curp += primer_digito

    # Calcular el segundo dígito verificador
    segundo_digito_verificador = calcular_digito_verificador(curp)

    # Agregar segundo dígito verificador a la CURP
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

        # Generar el código QR de la CURP generada
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(curp_generada)
        qr.make(fit=True)

        # Crear una imagen del código QR
        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar el código QR como un archivo PNG
        img_file = "static/curp_qr.png"
        img.save(img_file)

        # Devolver la CURP generada y la ruta de la imagen del QR como respuesta JSON
        return jsonify({'curp': curp_generada, 'qr_img': img_file})
    else:
        return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)

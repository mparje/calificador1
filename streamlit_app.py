import streamlit as st
import pandas as pd
import openai
import os
import base64
from io import BytesIO

# Activar el wide mode
st.set_page_config(layout="wide")

# Accedemos a la clave de API de OpenAI a través de una variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Agregamos un título al principio
st.title('Evaluador de ensayos')

# Agregamos información de instrucciones
st.write('Suba un archivo .XLSX con los ensayos de sus alumnos.')

# Pedimos al usuario que suba el archivo Excel
archivo = st.file_uploader('Cargar archivo Excel', type=['xlsx'])

if archivo:
    # Leemos el archivo con pandas
    data = pd.read_excel(archivo)

    # Pedimos al usuario que seleccione las columnas con el título y el ensayo
    columnas = data.columns
    columna_titulo = st.selectbox('Selecciona la columna que contiene los títulos:', columnas)
    columna_ensayo = st.selectbox('Selecciona la columna que contiene los ensayos:', columnas)

    # Pedimos al usuario que seleccione el tipo de ensayo
    tipo_ensayo = st.selectbox('Selecciona el tipo de ensayo:', ['Argumentativo', 'Expositivo', 'Libre'])

    # Agregamos un botón para iniciar la evaluación
    if st.button('Evaluar'):
        # Obtenemos los títulos y los ensayos del archivo
        titulos = data[columna_titulo].tolist()
        ensayos = data[columna_ensayo].tolist()

        # Utilizamos la API de GPT-3 para calificar cada ensayo
        resultados = []
        for i, ensayo in enumerate(ensayos):
            prompt = f"Califica el ensayo {tipo_ensayo.lower()} titulado '{titulos[i]}'. "
            prompt += f"Ensayo: {ensayo}. "
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None
            )
            justificacion = response.choices[0].text.strip()

            # Agregamos sugerencias de mejora a la justificación
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Sugiere mejoras para el ensayo {tipo_ensayo.lower()} titulado '{titulos[i]}'. Ensayo: {ensayo}",
                temperature=0,
                max_tokens=512,
                n=1,
                stop=None
            )
            sugerencias = response.choices[0].text.strip()

            # Agregamos la calificación y las sugerencias de mejora a la tabla
            resultados.append({
                'Ensayo': titulos[i],
                'Justificación': justificacion,
                'Sugerencias de mejora': sugerencias,
            })

        # Mostramos los resultados en una tabla
        st.write('Resultados:')
        tabla = pd.DataFrame(resultados)
        st.table(tabla)
        
            sugerencias = response.choices[0].text.strip()

            # Agregamos la calificación y las sugerencias de mejora a la tabla
            resultados.append({
                'Ensayo': titulos[i],
                'Justificación': justificacion,
                'Sugerencias de mejora': sugerencias,
            })

        # Mostramos los resultados en una tabla
        st.write('Resultados:')
        tabla = pd.DataFrame(resultados)
        st.table(tabla)

        # Creamos un enlace para descargar los resultados en formato Excel
        archivo_excel = BytesIO()
        writer = pd.ExcelWriter(archivo_excel, engine='xlsxwriter')
        tabla.to_excel(writer, index=False)
        writer.save()
        archivo_excel.seek(0)
        b64 = base64.b64encode(archivo_excel.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="resultados.xlsx">Descargar resultados en formato Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

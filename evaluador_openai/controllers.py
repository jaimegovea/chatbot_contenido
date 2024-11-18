import openai
import os
import textract
import pandas as pd
from pypdf import PdfReader
from pathlib import Path
from docx import Document
from sqlalchemy import create_engine


def read_pdf(essay_path):
    reader = PdfReader(essay_path)
    ensayo = ""
    for page in reader.pages:
        ensayo += page.extract_text()
    return ensayo


def read_docx(essay_path):
    document = Document(essay_path)
    ensayo = ""
    for paragraph in document.paragraphs:
        ensayo += paragraph.text
    return ensayo


def read_doc(essay_path):
    text = textract.process(essay_path)
    return text


def remove_extension(filename):
    return filename.split(".")[0]


def grade_essay(criteria, theme, ensayo, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y Propósito
            Eres un profesor universitario experto en {theme}, debes calificar los ensayos de tus alumnos de manera estricta y rigurosa.
            Analizas cada ensayo profundamente con base en los siguientes pasos.
            # Pasos
            - Leer todo el ensayo y analizarlo profundamente
            - Determinar si el ensayo se relaciona con la temática asignada: {theme}
            - Si no se cumple con la temática asignada colocar nota de 0 en el ensayo.
            - Determinar si el ensayo contiene información factual errónea.
            - Evaluar cada uno de los criterios de esta rúbrica {criteria}.
            - Evaluar las citas bibliográficas del ensayo con base en el formato APA.
            # Salida
            - Extraer una lista de los autores del ensayo en una sección llamada AUTORES
            - Extraer un resumen del ensayo y sus puntos clave en un párrafo de 30 palabras llamado RESUMEN
            - En caso de no cumplir con la temática no se debe mostrar ninguna de las siguientes secciones excepto CALIFICACIÓN
            - Mostrar la cantidad de citas correctas e incorrectas en una sección llamada BIBLIOGRAFÍA
            - Extraer los errores encontrados en el ensayo en lineas de 15 palabras en una sección llamada OPORTUNIDADES DE MEJORA
            - Dar retrolaimentación de cada criterio de la rúbrica en oraciones de 15 a 25 palabras, dirigiendose hacia el estudiante de manera amigable en una sección llamada RETROALIMENTACIÓN
            - Mostrar la nota final en un promedio de 10 puntos con base en los criterios de la rúbrica en una sección llamada CALIFICACIÓN
            # Ejemplo
            ### AUTORES
            Jaime Govea

            ### RESUMEN
            El ensayo explica cómo el uso de machine learning puede mejorar el PUE en centros de datos, utilizando ejemplos de Google y resultados específicos logrados por el ingeniero Gao.

            ### BIBLIOGRAFÍA
            - Citas correctas: 4
            - Citas incorrectas: 0

            ### OPORTUNIDADES DE MEJORA
            - "PUE es simplemente la proporción" podría ser más técnico.
            - "demasiado complejo para que alguna persona pruebe todas las posibilidades" falta especificidad.
            - "las condiciones puede ser utilizado para alertas de rendimiento automáticas" necesita claridad en la frase.

            ### RETROALIMENTACIÓN
            Contenido y Desarrollo del Tema: Buen trabajo al conectar concretamente la gestión de centros de datos con el machine learning y sus impactos en el PUE. El ejemplo de Google y Gao es muy pertinente.
            Organización y Estructura: Tu ensayo está bien estructurado con una introducción efectiva y una conclusión sólida. La organización de párrafos refleja un buen flujo de ideas.
            Claridad y Precisión en el Lenguaje: El lenguaje utilizado es generalmente claro y preciso, con explicaciones técnicas adecuadas. Sería beneficioso variar más tu vocabulario.

            ### CALIFICACIÓN
            - Contenido y Desarrollo del Tema: 4/4
            - Organización y Estructura: 3/3
            - Claridad y Precisión en el Lenguaje: 2/3
            - Nota final: 9/10""",
        }
    ]

    messages.append(
        {
            "role": "user",
            "content": f"El ensayo que debes evaluar es el siguiente: {ensayo}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def analyze_video(criteria, video_path, file_name, api_key):
    audio_path = os.path.join("/tmp", f"{remove_extension(file_name)}.ogg")
    client = openai.OpenAI(api_key=api_key)
    os.system(
        f"ffmpeg -y -i {video_path} -vn -map_metadata -1 -ac 1 -c:a libopus -b:a 12k -application voip {audio_path}"
    )
    # clip.audio.write_audiofile(audio_path)
    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=Path(audio_path), response_format="text", language="es"
    )
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe calificar video ensayos de sus alumnos de manera estricta y rigurosa
            Analiza profundamente la transcripción de los videos y sigue los siguientes pasos
            # Pasos
            - Analizar la transcripción completa del video de manera profunda.
            - Extraer la idea principal del video ensayo.
            - Analizar la vericidad de la información presentada.
            - Evaluar la capacidad de sintetizar información del autor.
            - Evaluar el contenido con base en los siguientes criterios de una rúbrica: {criteria}
            # Salida
            - Mostrar la idea principal del video en una oración de 15 a 20 palabras en una sección llamada IDEA PRINCIPAL.
            - Mostrar un resumen corto entre 30 a 40 palabras en una sección llamada RESUMEN.
            - Mostrar los hechos erroneos expresados en el video en una sección llamada ERRORES.
            - Mostrar retroalimentación acerca de cada criterio de la rúbrica evaluado en oraciones de 15 a 20 palabras en una sección llamada RETROALIMENTACIÓN.
            - Asegura de dar una calificación lo más objetiva posible en función de los descriptores de la rúbrica en una sección llamada CALIFICACIÓN""",
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Debes evaluar el siguiente texto: {transcription}",
        }
    )
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return transcription, response.choices[0].message.content


def review_video(criteria, transcription, api_key):
    client = openai.OpenAI(api_key=api_key)
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe calificar video ensayos de sus alumnos de manera estricta y rigurosa
            Analiza profundamente la transcripción de los videos y sigue los siguientes pasos
            # Pasos
            - Analizar la transcripción completa del video de manera profunda.
            - Extraer la idea principal del video ensayo.
            - Analizar la vericidad de la información presentada.
            - Evaluar la capacidad de sintetizar información del autor.
            - Evaluar el contenido con base en los siguientes criterios de una rúbrica: {criteria}
            # Salida
            - Mostrar la idea principal del video en una oración de 15 a 20 palabras en una sección llamada IDEA PRINCIPAL.
            - Mostrar un resumen corto entre 30 a 40 palabras en una sección llamada RESUMEN.
            - Mostrar los hechos erroneos expresados en el video en una sección llamada ERRORES.
            - Mostrar retroalimentación acerca de cada criterio de la rúbrica evaluado en oraciones de 15 a 20 palabras en una sección llamada RETROALIMENTACIÓN.
            - Asegura de dar una calificación lo más objetiva posible en función de los descriptores de la rúbrica en una sección llamada CALIFICACIÓN""",
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Debes evaluar el siguiente texto: {transcription}",
        }
    )

    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def generate_syllabus(subject, rda, description, sessions, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe realizar el sílabo para su clase: {subject}
            Piensa profundamente de la materia que debes dictar y los resultados de aprendizaje esperados para determinas las actividades, sigue los siguientes pasos
            # Pasos
            - Piensa profundamente acerca de tu materia asignada: {subject}
            - Piensa profundamente acerca de los resultados de aprendizaje de los estudiantes: {rda}
            - Piensa profundamente en temas de la materia que estén dentro de la siguiente descripción {description}
            - Debes dividir la clase con base en los créditos {sessions}, debes multiplicar los créditos por 4 y eso te da el número total de sesiones, los créditos determinan cuantas clases hay por semana, es decir, 2 creditos indican 2 clases por semana.
            - Se debe tratar una unidad por semana y tener un tema para cada clase dentro de esa unidad.
            - Cada tema debe estar ligado a un resultado de aprendizaje.
            - Cada tema es tratado en 3 sesiones: la pre-sesión, consta de aprendizaje autónomo previo a la clase; sesión, actividades durante la clase y post-sesión, tareas para después de la clase. 
            - Determina una actividad para cada sesión.
            - Asigna una descripción entre 10 y 15 palabras para la actividad.
            - Asigna un tiempo estimado no superior a 60 minutos para la actividad.
            - Asigna materiales y recursos necesarios para llevar a cabo la actividad, estos pueden ser libros, articuloas, videos o programas de software.
            # Salida
            - Devuelve la salida en un formato de diccionario de python, únicamente el diccionario, sin ninguna palabra ni caracter antes o despues
            - El diccionario debe tener los siguientes campos:
            - "course" es el nombre de la clase
            - "description" es la descripción de la materia
            - "objectives" es una lista con los resultados de aprendizaje de la materia
            - "sessions" es una lista de diccionarios para cada sesión, estas sesiones deben estar compuestas por los siguientes campos:
            - "unit" la unidad que se va a tratar en la semana.
            - "topic" es la temática de la sesión
            - "rda" es el resultado de aprendizaje asociado al tema, por ejemplo 'rda1', 'rda2' o 'rda3'
            - "pre-session" es un diccionario con la actividad de clase, esta actividad debe tener un campo "description que indica que debe hacer el estudiante, un campo "estimated_time" el tiempo en minutos que tarda la actividad, "material" que es el material sugerido para la materia.
            - "session" es un diccionario con los mismos campos que pre-session
            - "post-session" es un dicctionario con los mismos campos que pre-session y session.
            # Ejemplo
            {{
                "course": 'Ciencia de Datos e Inteligencia Artificial', 
                "description": 'La asignatura se centra en los fundamentos del DI y su aplicación práctica en la planificación educativa. Esto incluye la identificación de necesidades de aprendizaje, la formulación de objetivos educativos, la selección de estrategias pedagógicas centradas en el estudiante, el fomento de la colaboración interdisciplinaria y la exploración de enfoques innovadores. Estos temas permiten a los participantes desarrollar programas formativos efectivos que permitan el logro de los resultados de aprendizaje.', 
                "objectives": ['Aplica algoritmos de inteligencia artificial y modelos de analítica de datos para reconocer y resolver problemas en cualquier entorno.', 
                'Evalúa los resultados obtenidos de la analítica de datos e inteligencia artificial para sacar conclusiones, generar propuestas innovadoras y conocimiento en el campo de la ingeniería.', 
                'Identifica, formula y resuelve problemas complejos de ingeniería mediante la aplicación de principios de ingeniería, ciencia y matemática.'], 
                "sessions": [{{
                                "unit": 'Fundamentos de Ciencia de Datos',
                                "topic": 'Introducción a la Ciencia de Datos', 
                                "rda": 'rda1',
                                "pre-session":  {{
                                                "description": 'Lectura sobre los fundamentos y aplicaciones de la ciencia de datos.', 
                                                "estimated_time": '45 minutos',
                                                "material": 'Introducción a la Ciencia de Datos'
                                                }}, 
                                "session":  {{
                                                "description": 'Discusión de conceptos clave y ejemplos aplicados de ciencia de datos.', 
                                                "estimated_time": '60 minutos', 
                                                "material": 'Presentación sobre Ciencia de Datos'
                                            }}, 
                                "post-session": {{
                                                "description": 'Elaborar un resumen de la importancia de la ciencia de datos.', 
                                                "estimated_time": '30 minutos', 
                                                "material: 'Guía para el Resumen'
                                                }}
                            }}]
            }}
            """,
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Genera un sílabo de la siguiente materia: {subject}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def generate_questionnaire(subject, questions, topics, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario experto en {subject}, debes realizar un cuestionario de opción multiple para tus estudiantes
            Piensa profundamente de la materia que debes dictar y sigue los siguientes pasos
            # Pasos
            - Piensa profundamente acerca de tu materia asignada: {subject}
            - Debes pensar profundamente en {questions} preguntas para tus alumnos.
            - Las preguntas deben estar relacionadas con los siguientes temas: {topics}
            - Cada pregunta debe tener 4 opciones posibles o 2 en el caso de ser verdadero o falso.
            - Justificar la opción correcta de la pregunta.
            # Salida
            - Muestra las {questions} preguntas
            - Dentro de cada pregunta muestra las opciones de la respuesta.
            - Después de cada pregunta muestra la justificación de la respuesta correcta entre 20 a 30 palabras en una sección llamada JUSTIFICACIÓN
            # Ejemplo
            ## Pregunta 1: ¿Cuál de las siguientes aplicaciones es un caso común de uso de modelos de clasificación?
            ### Opciones
            a. Spam filter
            b. Predicción de terremotos
            c. Pronóstico del tiempo
            d. Cálculo de valor numérico de π (pi)
            ### JUSTIFICACIÓN
            La respuesta correcta es a. Spam filter debido a que los modelos de clasificación son utilizados para predecir variables discretas en lugar de continuas
            """,
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Genera un cuestionario de {questions} preguntas para la materia: {subject}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def grade_assignment(criteria, description, assignment, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y Propósito
            Eres un profesor universitario, debes calificar las tareas de tus alumnos de manera estricta y rigurosa.
            Analizas cada tarea profundamente con base en los siguientes pasos.
            La tarea tiene la siguiente descripción: {description}
            # Pasos
            - Leer toda la tarea y analizarla profundamente
            - Determinar si la tarea contiene información factual errónea.
            - Evaluar cada uno de los criterios de esta rúbrica {criteria}.
            # Salida
            - Extraer una lista de los autores de la tarea en una sección llamada AUTORES
            - Extraer un resumen de la tarea y sus puntos clave en un párrafo de 30 palabras llamado RESUMEN
            - Extraer los errores encontrados en la tarea en lineas de 15 palabras en una sección llamada OPORTUNIDADES DE MEJORA
            - Dar retrolaimentación de cada criterio de la rúbrica en oraciones de 15 a 25 palabras, dirigiendose hacia el estudiante de manera amigable en una sección llamada RETROALIMENTACIÓN
            - Mostrar la nota final en un promedio de 10 puntos con base en los criterios de la rúbrica en una sección llamada CALIFICACIÓN
            # Ejemplo
            ### AUTORES
            Jaime Govea

            ### RESUMEN
            La tarea explica cómo el uso de machine learning puede mejorar el PUE en centros de datos, utilizando ejemplos de Google y resultados específicos logrados por el ingeniero Gao.

            ### OPORTUNIDADES DE MEJORA
            - "PUE es simplemente la proporción" podría ser más técnico.
            - "demasiado complejo para que alguna persona pruebe todas las posibilidades" falta especificidad.
            - "las condiciones puede ser utilizado para alertas de rendimiento automáticas" necesita claridad en la frase.

            ### RETROALIMENTACIÓN
            Contenido y Desarrollo del Tema: Buen trabajo al conectar concretamente la gestión de centros de datos con el machine learning y sus impactos en el PUE. El ejemplo de Google y Gao es muy pertinente.
            Organización y Estructura: Tu tarea está bien estructurada con una introducción efectiva y una conclusión sólida. La organización de párrafos refleja un buen flujo de ideas.
            Claridad y Precisión en el Lenguaje: El lenguaje utilizado es generalmente claro y preciso, con explicaciones técnicas adecuadas. Sería beneficioso variar más tu vocabulario.

            ### CALIFICACIÓN
            - Contenido y Desarrollo del Tema: 4/4
            - Organización y Estructura: 3/3
            - Claridad y Precisión en el Lenguaje: 2/3
            - Nota final: 9/10""",
        }
    ]

    messages.append(
        {
            "role": "user",
            "content": f"La tarea que debes evaluar es la siguiente: {assignment}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def generate_report(table_name, user_id, date, columns_to_drop):
    engine = create_engine(
        "mysql+pymysql://root:mtFH1Qtyft56wBDdqVBi@localhost:3306/evaluador_django"
    )
    sql_query = f"SELECT * FROM {table_name} WHERE user_id = {user_id};"
    df = pd.read_sql(sql_query, engine)
    df = df[df["date"] == date]
    df = df.drop(columns=columns_to_drop)
    file_path = os.path.join(os.getcwd(), "media", "reports", "report.xlsx")
    writer = pd.ExcelWriter(file_path)
    df.to_excel(writer, sheet_name="sheetName", index=False, na_rep="NaN")
    workbook = writer.book
    text_format = workbook.add_format({"text_wrap": True})
    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column))
        if column_length > 100:
            column_length = column_length / 10
        col_idx = df.columns.get_loc(column)
        writer.sheets["sheetName"].set_column(
            col_idx, col_idx, column_length, text_format
        )
    writer._save()
    return file_path


def generate_lab_guide(dict, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe realizar guías de laboratorio para su clase: a partir de la siguiente información de este diccionario: {dict}
            Piensa profundamente de la materia que debes dictar y los pasos a seguir para llevar a cabo la práctica de laboratorio, sigue los siguientes pasos
            # Pasos
            - Piensa profundamente acerca de tu materia asignada detallada en el diccionario
            - Analiza los objetivos de aprendizaje que se encuentran en la llave "objectives"
            - Itera sobre el diccionario, en la sección "sessions" se detallan las actividades llevadas a cabo en cada sesión, toma en cuenta solo las de la llave "sessions", omite "pre-session" y "post-session"
            - Dentro de las actividades de cada sesión, determina cuál se refiere a un taller de laboratorio o algún tipo de actividad práctica.
            - Determina cuál de los objetivos de aprendizaje se alinea mejor a la práctica de laboratorio que se llevará a cabo.
            - La guía debe contener los siguientes campos: nombre de la materia, nombre de la práctica, objetivos, resultado de aprendizaje esperado, introducción teórica, materiales y equipos, procdedimiento, bibliografía y anexos.
            - El nombre de la materia y nombre de la práctica deben ser los mismos que en el diccionario de entrada.
            - En objetivos se colocan los conceptos que se espera que el estudiante aprenda tras culminar el taller.
            - El resultado de aprendizaje esperado debe el objetivo de aprendizaje que mejor se alinea al taller.
            - La introducción teórica es el trasfondo teórico relacionado al taller práctico, debe contar con un parrafo de introducción y entre 4 y 5 parrafos indicando los conceptos teóricos que se aplicarán en el taller.
            - En materiales y equipos se deben colocar los insumos necesarios para llevar a cabo el taller, como computadores, herramientas de software específicas, entre otros.
            - En procedimiento se debe indicar las instrucciones paso a paso para llevar a cabo el taller.
            - En bibliografía se deben colocar las referencias necesarias para realizar el taller.
            - En anexos se colocan preguntas que el estudiante debe responder al final del taller.
            - Repite los pasos anteriores para todas las actividades que sean talleres de laboratorio y agregalos al diccionario.
            # Salida
            - Devuelve la salida en un formato de diccionario de python, únicamente el diccionario, sin ninguna palabra ni caracter antes o despues
            - El diccionario debe tener los siguientes campos:
            - "course" es el nombre de la clase
            - "workshop_name" es el nombre de la práctica
            - "objectives" es una lista con los objetivos de aprendizaje del estudiante.
            - "rda" es el resultado de aprendizaje que mejor se alinea a la práctica.
            - "introduction" es la intorudcción teorica, es un diccionario con los siguientes campos: "description" que es la introducción a la práctica, "topics" es una lista que contiene diccionarios con los siguientes campos: "title" el título de la temática teórica asociada a la práctica y "description" que es una descripción de dicha temática.
            - "materials" es una lista con todos los materiales y equipos necesarios para el taller.
            - "methodology" es una lista que contiene diccionarios con los siguientes campos: "step" es el nombre del paso a llevar a cabo en la práctica y "details" es una lista que contiene las instrucciones detalladas para llevar a cabo cada paso.
            - "references" es una lista con las referencias bibliográficas del taller.
            - "annexes" es una lista que contiene diccionarios con los siguientes campos: "title" es la temática de las preguntas que se van a realizar, "objective" es el objetivo con el cuál se van a responder las preguntas y "questions" que es una lista con entre 2 y 3 preguntas de la temática mencionada.
            # Ejemplo
            {{
                "course": "Ciencia de Datos e IA /202410",
                sessions: {{
                        [
                        "workshop_name": "Análisis y Visualización de Datos en la Industria de Videojuegos: Tendencias, Ventas y Popularidad",
                        "objetives": [
                            "Familiarizarse con el análisis de grandes conjuntos de datos relacionados con la industria de videojuegos.",
                            "Aprender a cargar y preprocesar datos para su análisis usando Python y PySpark.",
                            "Descubrir patrones y tendencias relacionados con ventas y popularidad de géneros y títulos de videojuegos.",
                            "Analizar la correlación entre distintas variables, como ventas regionales.",
                            "Visualizar los resultados para interpretaciones claras y acciones basadas en datos."
                        ],
                        "rda": "RC1: Identifica, formula y resuelve problemas complejos de ingeniería mediante la aplicación de principios de ingeniería, ciencia y matemática.",
                        "introduction": {{
                            "description": "La industria de los videojuegos ha experimentado un crecimiento exponencial, generando grandes cantidades de datos útiles para análisis.",
                            "topics": [
                                {{
                                    "title": "Análisis de Datos",
                                    "dedescription": "Proceso de inspeccionar, limpiar y transformar datos para descubrir información útil, informar conclusiones y apoyar la toma de decisiones."
                                }},
                                {{
                                    "title": "Big Data",
                                    "description": "Conjuntos de datos tan grandes y complejos que las aplicaciones tradicionales de procesamiento no pueden manejarlos."
                                }},
                                {{
                                    "title": "Correlación vs. Causalidad",
                                    "description": "Diferencia entre correlación y causalidad; la correlación indica relación, mientras que la causalidad implica una conexión directa."
                                }}
                            ]
                        }},
                        "materials": [
                            "Computadora con acceso a internet.",
                            "Entorno de desarrollo Python con PySpark y Matplotlib instalados.",
                            "Conjunto de datos de videojuegos para análisis (ej. vgsales.csv)."
                        ],
                        "methodology": [
                            {{
                                "step": "Preparación de los datos",
                                "details": [
                                    "Importa las bibliotecas necesarias: PySpark y Matplotlib.",
                                    "Carga el conjunto de datos de videojuegos.",
                                    "Preprocesa los datos, filtrando valores nulos o irrelevantes."
                                ]
                            }},
                            {{
                                "step": "Relación entre Ventas Regionales",
                                "details": [
                                    "Calcula la correlación entre ventas en distintas regiones.",
                                    "Visualiza los resultados en gráficos de dispersión."
                                ]
                            }},
                            {{
                                "step": "Distribución de Ventas según Género",
                                "details": [
                                    "Agrupa los datos según el género del videojuego.",
                                    "Usa diagramas de caja (boxplots) para visualizar la distribución de ventas."
                                ]
                            }}
                        ],
                        "references": [
                            "Referencia del tutorial de Keras",
                            "Libro sobre Convolutional Neural Networks",
                            "Artículo científico sobre técnicas de mejora de modelos de CNN"
                        ],
                        "annexes": [
                                {{
                                    "title": "Relación entre Ventas Regionales",
                                    "objective": "Analizar la correlación entre las ventas en América del Norte, Europa, Japón y otras regiones.",
                                    "questions": [
                                        "¿Existe una fuerte correlación entre las ventas en diferentes regiones?",
                                        "¿Hay juegos que venden bien en todas las regiones?",
                                        "¿Existen juegos que son populares solo en una región específica?"
                                    ]
                                }},
                                {{
                                    "title": "Análisis de Videojuegos por Puntuación",
                                    "objective": "Analizar si hay una correlación entre las puntuaciones de los videojuegos y sus ventas globales.",
                                    "questions": [
                                        "¿Los juegos con puntuaciones más altas tienden a tener más ventas?",
                                        "¿Existen juegos con bajas puntuaciones pero con altas ventas?"
                                    ]
                                }},
                                {{
                                    "title": "Distribución de Ventas según Género",
                                    "objective": "Visualizar la distribución de las ventas de juegos según su género.",
                                    "questions": [
                                        "¿Qué géneros tienden a tener ventas más altas en promedio?",
                                        "¿Existen géneros con ventas atípicamente altas o bajas?"
                                    ]
                                }}
                            ]
                        ]
                    }}
                }}
            """,
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Genera una guía de laboratorio para las actividades del sílabo en el siguiente diccionario {dict}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def generate_rubric(dict, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe realizar rúbricas de evaluación con base en el siguiente diccionario: {dict}
            Piensa profundamente de la materia que debes dictar y los pasos a seguir para desarrollar las rúbricas, sigue los siguientes pasos
            # Pasos
            - Piensa profundamente acerca de tu materia asignada detallada en el diccionario
            - Analiza los objetivos de aprendizaje que se encuentran en la llave "objectives"
            - Con base en los objetivos de aprendizaje debes generar 3 rúbricas, una para informes, una para ensayos y una para ejercicios prácticos
            - Cada rúbrica debe contar con 5 criterios de evaluación y 4 calificaciones, que son excelente con 4 puntos, muy bueno con 3 puntos, regular con 2 puntos e insuficiente con 1 punto
            # Salida
            - Devuelve la salida en un formato de diccionario de python, únicamente el diccionario, sin ninguna palabra ni caracter antes o despues
            - El diccionario debe tener los siguientes campos:
            - "report" es una lista de diccionarios, cada diccionario con los criterios de evaluación de la rúbrica para informes debe tener un campo "name" con el nombre del criterio, "excellent" que son los parámetros que debe cumplir el trabajo para una puntuación de 4 puntos, "very_good" que contiene los parámetros que debe cumplir para tener 3 puntos, "regular" con los parámetros que debe contener para tener 2 puntos y "insufficient" que son los parámetros para una puntuación de 1 punto.
            - "essay" es una lista de diccionarios, cada diccionario con los criterios de evaluación de la rúbrica para ensayos, tiene los mismos campos detallados en "report"
            - "excercise" es una lista de diccionarios, cada diccionario con los criterios de evaluación de la rúbrica para ejercicios prácticos, tiene los mismos campos que "report"
            # Ejemplo
            {{
                "report": [{{
                    "name": "Claridad de las Ideas",
                    "Excelente": "Las ideas son extremadamente claras, bien estructuradas y fáciles de entender.",
                    "Muy Bueno": "Las ideas son mayormente claras y bien estructuradas, con problemas menores de comprensión.",
                    "Regular": "Las ideas son algo claras, pero hay problemas notables con la estructura y la comprensión.",
                    "Insuficiente": "Las ideas no son claras, están mal estructuradas y son difíciles de entender."
                }},
                {{
                    "name": "Profundidad del Análisis",
                    "Excelente": "El análisis es exhaustivo y perspicaz, demostrando una comprensión profunda del tema.",
                    "Muy Bueno": "El análisis es detallado y muestra una buena comprensión, con algunas brechas menores.",
                    "Regular": "El análisis es algo superficial, con varios aspectos importantes no completamente explorados.",
                    "Insuficiente": "El análisis es superficial, carece de profundidad y no aborda elementos clave."
                }},
                {{
                    "name": "Uso de Evidencia",
                    "Excelente": "Se utiliza evidencia sólida y relevante para respaldar los argumentos, mejorando la calidad general del trabajo.",
                    "Muy Bueno": "Se utiliza buena evidencia para respaldar la mayoría de los argumentos, con espacio para mejoras.",
                    "Regular": "La evidencia se usa de manera inconsistente, y algunos argumentos están débilmente respaldados.",
                    "Insuficiente": "Se usa poca o ninguna evidencia, lo que hace que los argumentos no sean convincentes y carezcan de respaldo."
                }},
                {{
                    "name": "Presentación y Organización",
                    "Excelente": "La presentación está excepcionalmente organizada y es visualmente atractiva, facilitando la comprensión.",
                    "Muy Bueno": "La presentación está bien organizada y es visualmente clara, con pequeñas mejoras necesarias.",
                    "Regular": "La presentación está algo organizada, pero hay problemas que afectan la claridad y el flujo.",
                    "Insuficiente": "La presentación está desorganizada, es difícil de seguir y visualmente poco atractiva."
                }}],
                "essay": [{{
                    "name": "Claridad de las Ideas",
                    "Excelente": "Las ideas son extremadamente claras, bien estructuradas y fáciles de entender.",
                    "Muy Bueno": "Las ideas son mayormente claras y bien estructuradas, con problemas menores de comprensión.",
                    "Regular": "Las ideas son algo claras, pero hay problemas notables con la estructura y la comprensión.",
                    "Insuficiente": "Las ideas no son claras, están mal estructuradas y son difíciles de entender."
                }},
                {{
                    "name": "Profundidad del Análisis",
                    "Excelente": "El análisis es exhaustivo y perspicaz, demostrando una comprensión profunda del tema.",
                    "Muy Bueno": "El análisis es detallado y muestra una buena comprensión, con algunas brechas menores.",
                    "Regular": "El análisis es algo superficial, con varios aspectos importantes no completamente explorados.",
                    "Insuficiente": "El análisis es superficial, carece de profundidad y no aborda elementos clave."
                }},
                {{
                    "name": "Uso de Evidencia",
                    "Excelente": "Se utiliza evidencia sólida y relevante para respaldar los argumentos, mejorando la calidad general del trabajo.",
                    "Muy Bueno": "Se utiliza buena evidencia para respaldar la mayoría de los argumentos, con espacio para mejoras.",
                    "Regular": "La evidencia se usa de manera inconsistente, y algunos argumentos están débilmente respaldados.",
                    "Insuficiente": "Se usa poca o ninguna evidencia, lo que hace que los argumentos no sean convincentes y carezcan de respaldo."
                }},
                {{
                    "name": "Presentación y Organización",
                    "Excelente": "La presentación está excepcionalmente organizada y es visualmente atractiva, facilitando la comprensión.",
                    "Muy Bueno": "La presentación está bien organizada y es visualmente clara, con pequeñas mejoras necesarias.",
                    "Regular": "La presentación está algo organizada, pero hay problemas que afectan la claridad y el flujo.",
                    "Insuficiente": "La presentación está desorganizada, es difícil de seguir y visualmente poco atractiva."
                }}],
                "excercise": [{{
                    "name": "Claridad de las Ideas",
                    "Excelente": "Las ideas son extremadamente claras, bien estructuradas y fáciles de entender.",
                    "Muy Bueno": "Las ideas son mayormente claras y bien estructuradas, con problemas menores de comprensión.",
                    "Regular": "Las ideas son algo claras, pero hay problemas notables con la estructura y la comprensión.",
                    "Insuficiente": "Las ideas no son claras, están mal estructuradas y son difíciles de entender."
                }},
                {{
                    "name": "Profundidad del Análisis",
                    "Excelente": "El análisis es exhaustivo y perspicaz, demostrando una comprensión profunda del tema.",
                    "Muy Bueno": "El análisis es detallado y muestra una buena comprensión, con algunas brechas menores.",
                    "Regular": "El análisis es algo superficial, con varios aspectos importantes no completamente explorados.",
                    "Insuficiente": "El análisis es superficial, carece de profundidad y no aborda elementos clave."
                }},
                {{
                    "name": "Uso de Evidencia",
                    "Excelente": "Se utiliza evidencia sólida y relevante para respaldar los argumentos, mejorando la calidad general del trabajo.",
                    "Muy Bueno": "Se utiliza buena evidencia para respaldar la mayoría de los argumentos, con espacio para mejoras.",
                    "Regular": "La evidencia se usa de manera inconsistente, y algunos argumentos están débilmente respaldados.",
                    "Insuficiente": "Se usa poca o ninguna evidencia, lo que hace que los argumentos no sean convincentes y carezcan de respaldo."
                }},
                {{
                    "name": "Presentación y Organización",
                    "Excelente": "La presentación está excepcionalmente organizada y es visualmente atractiva, facilitando la comprensión.",
                    "Muy Bueno": "La presentación está bien organizada y es visualmente clara, con pequeñas mejoras necesarias.",
                    "Regular": "La presentación está algo organizada, pero hay problemas que afectan la claridad y el flujo.",
                    "Insuficiente": "La presentación está desorganizada, es difícil de seguir y visualmente poco atractiva."
                }}]
            }}
            """,
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Genera rúbricas para calificar informes, ensayos y ejercicios prácticos para la materia del siguiente diccionario {dict}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content


def generate_pptx(dict, api_key):
    messages = [
        {
            "role": "system",
            "content": f"""# Identidad y propósito
            Eres un profesor universitario que debe realizar presentaciones de power point con base en el siguiente diccionario: {dict}
            Piensa profundamente de la materia que debes dictar y los pasos a seguir para desarrollar las presentaciones, sigue los siguientes pasos
            # Pasos
            - Piensa profundamente acerca de tu materia asignada detallada en el diccionario
            - Analiza los objetivos de aprendizaje que se encuentran en la llave "objectives"
            - Con base en los objetivos de aprendizaje debes generar contenido para las presentaciones de las clases, las actividades de la presentación se encuentran en el campo "session" del diccionario
            - El contenido de la presentación debe estar alineado a los objetivos de aprendizaje
            # Salida
            - Devuelve la salida en un formato de diccionario de python, únicamente el diccionario, sin ninguna palabra ni caracter antes o despues
            - Debe tener contenido para entre 8 y 10 diapositivas
            - El diccionario debe tener los siguientes campos:
            - "presentations" es una lista con el contenido de la presentación de cada sesión
            - "title" es el nombre de cada presentación
            - "slides" es una lista con el contenido de cada diapositiva
            - "header" es el título de la diapositiva
            - "text" es el contenido de cada diapositiva
            # Ejemplo
            {{
                "presentations" : [
                    {{
                        "title": "Fundamentos de Ciberseguridad",
                        "slides": [
                                {{
                                    "header": "Introducción al Hashing",
                                    "text": "El hashing es una técnica que convierte datos en una secuencia única y fija de caracteres, usada comúnmente para proteger contraseñas y verificar la integridad de archivos."
                                }},
                                {{
                                    "header": "Objetivo de la Sesión",
                                    "text": "Entender la utilidad del hashing en ciberseguridad y explorar cómo se implementa en sistemas Linux mediante comandos específicos."
                                }},
                                {{
                                    "header": "Conceptos Clave",
                                    "text": "Definición de hashing y sus propiedades principales: determinismo, resistencia a colisiones y preimágenes. Aplicaciones del hashing en ciberseguridad: protección de contraseñas y verificación de integridad. Comandos en Linux para generar y verificar hashes (ej., `md5sum`, `sha256sum`)."
                                }},
                                {{
                                    "header": "Demostración Práctica",
                                    "text": "Se utilizarán comandos de hashing en una máquina virtual Linux para generar y verificar hashes de archivos, mostrando su rol en la protección de la información."
                                }},
                                {{
                                    "header": "Conclusión",
                                    "text": "El hashing es una herramienta esencial en la ciberseguridad, que ayuda a proteger datos críticos y a verificar la integridad de archivos de manera eficiente."
                                }}
                            ]
                    }},
                    {{
                        "title": "Comandos Básicos de Linux para Seguridad",
                        "slides": [
                            {{
                                "header": "Introducción a la Seguridad en Linux",
                                "text": "Linux ofrece un conjunto robusto de comandos para gestionar y asegurar sistemas. Conocerlos permite proteger mejor los recursos de información."
                            }},
                            {{
                                "header": "Objetivo de la Sesión",
                                "text": "Aprender a utilizar comandos básicos de Linux para fortalecer la seguridad de un sistema y gestionar el acceso a sus recursos."
                            }},
                            {{
                                "header": "Comandos Clave de Seguridad en Linux",
                                "text": "`chmod` y `chown`: Configuración de permisos y propiedad de archivos. `ufw`: Configuración básica de firewall para controlar el tráfico de red. `top` y `ps`: Supervisión de procesos para identificar actividad sospechosa. `netstat` y `ss`: Monitoreo de conexiones de red activas."
                            }},
                            {{
                                "header": "Ejercicio Práctico",
                                "text": "Aplicación de comandos en una terminal Linux para asegurar una máquina, configurando permisos de archivos y bloqueando accesos no autorizados."
                            }},
                            {{
                                "header": "Conclusión",
                                "text": "La gestión de la seguridad en Linux requiere conocimiento de comandos básicos, que permiten implementar configuraciones y supervisión de sistemas eficazmente."
                            }}
                        ]
                    }}
                ]
            }}
            """,
        }
    ]
    messages.append(
        {
            "role": "user",
            "content": f"Genera el contenido de las presentaciones para las actividades de la materia del siguiente diccionario {dict}",
        }
    )
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content
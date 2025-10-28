from scripts.utilitarios.ml.correcciones import guardar_correccion
def procesar_feedback(historial):
    if not historial or len(historial) <3:
        return
    ultimo_msg = historial[-1]
    if ultimo_msg.rol != "usuario":
            return
    texto = ultimo_msg.contenido.lower().strip()

    positivos = ["correcto"]
    if texto in positivos:
        respuesta_gpt = None
        pregunta_usuario = None
        for msg in reversed(historial[:-1]):
            if msg.rol == "bot" and respuesta_gpt is None:
                respuesta_gpt = msg.contenido
            elif msg.rol == "usuario" and pregunta_usuario is None:
                pregunta_usuario = msg.contenido
                break
        if pregunta_usuario and respuesta_gpt:
            guardar_correccion(pregunta_usuario, respuesta_gpt)
           # print(f"💾 Corrección añadida desde feedback: {pregunta_usuario} → {respuesta_gpt}")

        


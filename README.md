# DocuFlow — demo de control documental

Prototipo en Streamlit para explorar un flujo de recopilación de documentos para asesorías.

## Qué incluye

- Panel de resumen con estados.
- Lista de clientes y documentos ficticios.
- Edición de estado por documento.
- Generación de borradores de recordatorio (no se envían).
- Alta de clientes de prueba en la sesión.

## Ejecutar localmente (opcional)

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar gratis en Streamlit Community Cloud

1. Crea una cuenta en GitHub si no tienes una.
2. Crea un repositorio nuevo llamado `docuflow-demo` (puede ser privado al principio).
3. Sube `app.py`, `requirements.txt` y `README.md` a la raíz del repositorio.
4. Entra en https://share.streamlit.io/ e inicia sesión con GitHub.
5. Pulsa para crear una aplicación y selecciona el repositorio `docuflow-demo`, la rama principal y el archivo `app.py`.
6. Despliega la aplicación. Streamlit te dará una URL para abrirla y compartirla.

La interfaz de Streamlit Cloud puede cambiar; sigue las opciones equivalentes si los nombres son distintos.

## Limitaciones importantes

- Los datos son de demostración y se guardan solo en la sesión; no hay persistencia garantizada.
- No hay autenticación de usuarios, base de datos persistente ni envío de emails.
- No subas documentos reales, datos personales ni información confidencial.
- Antes de venderlo o usarlo con clientes reales, habría que diseñar seguridad, permisos, almacenamiento, copias de seguridad, tratamiento de datos y cumplimiento del RGPD.

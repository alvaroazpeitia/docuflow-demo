import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

st.set_page_config(
    page_title="DocuFlow | Control documental",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Demo only: data is held in Streamlit session state and resets when the session restarts.
SAMPLE_CLIENTS = [
    {
        "id": 1, "name": "María López García", "company": "López Diseño SL",
        "email": "maria.demo@example.com", "period": "3T 2026",
        "documents": [
            {"name": "Facturas emitidas", "status": "Recibido"},
            {"name": "Facturas recibidas", "status": "Pendiente"},
            {"name": "Extracto bancario", "status": "Pendiente"},
        ],
    },
    {
        "id": 2, "name": "Javier Martín Pérez", "company": "Martín Instalaciones",
        "email": "javier.demo@example.com", "period": "3T 2026",
        "documents": [
            {"name": "Facturas emitidas", "status": "Recibido"},
            {"name": "Facturas recibidas", "status": "Recibido"},
            {"name": "Extracto bancario", "status": "Recibido"},
        ],
    },
    {
        "id": 3, "name": "Ana Fernández Ruiz", "company": "AFR Consultoría",
        "email": "ana.demo@example.com", "period": "3T 2026",
        "documents": [
            {"name": "Facturas emitidas", "status": "Recibido"},
            {"name": "Facturas recibidas", "status": "Revisión"},
            {"name": "Extracto bancario", "status": "Pendiente"},
        ],
    },
    {
        "id": 4, "name": "Carlos Rodríguez Soto", "company": "CRS Comercio",
        "email": "carlos.demo@example.com", "period": "3T 2026",
        "documents": [
            {"name": "Facturas emitidas", "status": "Pendiente"},
            {"name": "Facturas recibidas", "status": "Pendiente"},
            {"name": "Extracto bancario", "status": "Pendiente"},
        ],
    },
]

if "clients" not in st.session_state:
    st.session_state.clients = SAMPLE_CLIENTS
if "reminder_log" not in st.session_state:
    st.session_state.reminder_log = []

clients = st.session_state.clients

def missing_docs(client):
    return [doc["name"] for doc in client["documents"] if doc["status"] != "Recibido"]

def client_status(client):
    statuses = [doc["status"] for doc in client["documents"]]
    if all(s == "Recibido" for s in statuses):
        return "Completo"
    if "Revisión" in statuses:
        return "Revisión"
    return "Pendiente"

def make_reminder(client):
    missing = missing_docs(client)
    if not missing:
        return (
            f"Hola {client['name'].split()[0]},\n\n"
            f"Hemos recibido toda la documentación correspondiente a {client['period']}. "
            "Gracias por enviárnosla.\n\nUn saludo,\nEquipo de la asesoría"
        )
    docs = "\n".join(f"• {doc}" for doc in missing)
    return (
        f"Hola {client['name'].split()[0]},\n\n"
        f"Estamos revisando la documentación de {client['period']} y nos faltan estos documentos:\n\n"
        f"{docs}\n\n"
        "Cuando puedas, envíanoslos mediante el canal seguro que utilizamos habitualmente. "
        "Si ya los has enviado, puedes ignorar este mensaje.\n\n"
        "Gracias,\nEquipo de la asesoría"
    )

st.markdown("""
<style>
    .block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1450px;}
    .brand {font-size: 1.8rem; font-weight: 750; letter-spacing: -0.04em;}
    .subtle {color: #6b7280; font-size: 0.95rem;}
    div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.22); padding: 14px 16px; border-radius: 12px;}
    .notice {padding: 12px 14px; border-radius: 10px; background: rgba(128,128,128,.10); font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand">📁 DocuFlow</div>', unsafe_allow_html=True)
    st.caption("Control documental para asesorías")
    page = st.radio(
        "Navegación",
        ["Resumen", "Clientes y documentos", "Crear recordatorio", "Añadir cliente"],
        label_visibility="visible",
    )
    st.divider()
    st.caption("MODO DEMO")
    st.info("Datos ficticios. No se envían emails ni se almacenan archivos reales.")

st.title(page)
st.markdown('<div class="subtle">Una vista sencilla para saber qué falta, a quién avisar y qué expedientes están completos.</div>', unsafe_allow_html=True)
st.write("")

if page == "Resumen":
    total_docs = sum(len(c["documents"]) for c in clients)
    received = sum(1 for c in clients for d in c["documents"] if d["status"] == "Recibido")
    pending = sum(1 for c in clients for d in c["documents"] if d["status"] == "Pendiente")
    review = sum(1 for c in clients for d in c["documents"] if d["status"] == "Revisión")
    complete_clients = sum(1 for c in clients if client_status(c) == "Completo")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Clientes", len(clients))
    m2.metric("Documentos recibidos", received, f"de {total_docs}")
    m3.metric("Pendientes", pending)
    m4.metric("Necesitan revisión", review)

    st.subheader("Prioridades de hoy")
    needs_attention = [c for c in clients if missing_docs(c) or client_status(c) == "Revisión"]
    if needs_attention:
        rows = []
        for c in needs_attention:
            rows.append({
                "Cliente": c["name"],
                "Empresa": c["company"],
                "Periodo": c["period"],
                "Faltan documentos": len(missing_docs(c)),
                "Estado": client_status(c),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.success("Todos los expedientes están completos.")

    st.subheader("Estado de la documentación")
    chart_df = pd.DataFrame({
        "Estado": ["Recibido", "Pendiente", "Revisión"],
        "Documentos": [received, pending, review],
    }).set_index("Estado")
    st.bar_chart(chart_df)
    st.markdown(
        '<div class="notice">Esta demo ilustra el flujo de trabajo. Las cifras y los clientes son ficticios; todavía no hay integración con email, contabilidad ni almacenamiento documental.</div>',
        unsafe_allow_html=True,
    )

elif page == "Clientes y documentos":
    search = st.text_input("Buscar cliente o empresa", placeholder="Ej. López o Consultoría")
    filtered = [c for c in clients if search.lower() in (c["name"] + " " + c["company"]).lower()]
    for c in filtered:
        with st.expander(f"{c['company']} · {c['name']} · {client_status(c)}", expanded=False):
            st.caption(f"Periodo: {c['period']} · Email de demo: {c['email']}")
            for idx, doc in enumerate(c["documents"]):
                col1, col2 = st.columns([3, 2])
                col1.write(doc["name"])
                options = ["Pendiente", "Recibido", "Revisión"]
                current_idx = options.index(doc["status"])
                new_status = col2.selectbox(
                    f"Estado de {doc['name']}",
                    options,
                    index=current_idx,
                    key=f"status_{c['id']}_{idx}",
                    label_visibility="collapsed",
                )
                if new_status != doc["status"]:
                    doc["status"] = new_status
                    st.rerun()
            st.write("")
            if st.button("Preparar recordatorio", key=f"rem_{c['id']}"):
                st.session_state.selected_client_id = c["id"]
                st.session_state.page_to_open = "Crear recordatorio"
                st.rerun()
    if not filtered:
        st.info("No hay clientes que coincidan con la búsqueda.")

elif page == "Crear recordatorio":
    if not clients:
        st.info("Añade un cliente para empezar.")
    else:
        default_id = st.session_state.get("selected_client_id", clients[0]["id"])
        ids = [c["id"] for c in clients]
        if default_id not in ids:
            default_id = ids[0]
        selected_id = st.selectbox(
            "Selecciona un cliente",
            ids,
            index=ids.index(default_id),
            format_func=lambda cid: next(c["company"] for c in clients if c["id"] == cid),
        )
        client = next(c for c in clients if c["id"] == selected_id)
        st.write(f"**Destinatario de ejemplo:** {client['email']}")
        message = make_reminder(client)
        subject = f"Documentación pendiente · {client['period']}"
        st.text_input("Asunto", value=subject, key=f"subject_{selected_id}")
        st.text_area("Borrador del mensaje", value=message, height=250, key=f"message_{selected_id}")
        st.caption("El borrador no se envía. Usa solo datos ficticios en esta demo.")
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Registrar como preparado", type="primary", use_container_width=True):
                st.session_state.reminder_log.append({
                    "cliente": client["company"],
                    "fecha": date.today().isoformat(),
                    "estado": "Borrador preparado",
                })
                st.success("Borrador registrado en esta sesión.")
        with col2:
            st.button("Actualizar borrador", use_container_width=True, on_click=lambda: st.rerun())
        if st.session_state.reminder_log:
            st.subheader("Actividad reciente")
            st.dataframe(pd.DataFrame(st.session_state.reminder_log), use_container_width=True, hide_index=True)

elif page == "Añadir cliente":
    st.write("Añade un cliente ficticio para explorar el flujo. No introduzcas datos reales ni confidenciales.")
    with st.form("add_client_form", clear_on_submit=True):
        name = st.text_input("Nombre de contacto")
        company = st.text_input("Empresa")
        email = st.text_input("Email ficticio", placeholder="contacto.demo@example.com")
        period = st.selectbox("Periodo", ["3T 2026", "4T 2026", "Mensual · octubre 2026", "Otro"])
        submitted = st.form_submit_button("Añadir cliente", type="primary")
        if submitted:
            if not name.strip() or not company.strip() or not email.strip():
                st.error("Completa nombre, empresa y email.")
            else:
                new_id = max([c["id"] for c in clients], default=0) + 1
                st.session_state.clients.append({
                    "id": new_id,
                    "name": name.strip(),
                    "company": company.strip(),
                    "email": email.strip(),
                    "period": period,
                    "documents": [
                        {"name": "Facturas emitidas", "status": "Pendiente"},
                        {"name": "Facturas recibidas", "status": "Pendiente"},
                        {"name": "Extracto bancario", "status": "Pendiente"},
                    ],
                })
                st.success(f"Cliente de demo añadido: {company}")
                st.rerun()

st.divider()
st.caption("DocuFlow · Prototipo de validación · No apto para gestionar documentación real.")

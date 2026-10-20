import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="DocuFlow · Control documental", page_icon="📂", layout="wide", initial_sidebar_state="expanded")

# Prototipo de validación: datos ficticios en memoria de sesión. No usar datos reales.
SAMPLE_CLIENTS = [
    {"id": 1, "name": "María López García", "company": "López Diseño SL", "email": "maria.demo@example.com", "period": "3T 2026", "documents": [{"name": "Facturas emitidas", "status": "Recibido"}, {"name": "Facturas recibidas", "status": "Pendiente"}, {"name": "Extracto bancario", "status": "Pendiente"}]},
    {"id": 2, "name": "Javier Martín Pérez", "company": "Martín Instalaciones", "email": "javier.demo@example.com", "period": "3T 2026", "documents": [{"name": "Facturas emitidas", "status": "Recibido"}, {"name": "Facturas recibidas", "status": "Recibido"}, {"name": "Extracto bancario", "status": "Recibido"}]},
    {"id": 3, "name": "Ana Fernández Ruiz", "company": "AFR Consultoría", "email": "ana.demo@example.com", "period": "3T 2026", "documents": [{"name": "Facturas emitidas", "status": "Recibido"}, {"name": "Facturas recibidas", "status": "Revisión"}, {"name": "Extracto bancario", "status": "Pendiente"}]},
    {"id": 4, "name": "Carlos Rodríguez Soto", "company": "CRS Comercio", "email": "carlos.demo@example.com", "period": "3T 2026", "documents": [{"name": "Facturas emitidas", "status": "Pendiente"}, {"name": "Facturas recibidas", "status": "Pendiente"}, {"name": "Extracto bancario", "status": "Pendiente"}]},
]
STATUSES = ["Pendiente", "Recibido", "Revisión"]

if "clients" not in st.session_state:
    st.session_state.clients = [dict(c, documents=[dict(d) for d in c["documents"]]) for c in SAMPLE_CLIENTS]
if "reminder_log" not in st.session_state:
    st.session_state.reminder_log = []
if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = 1

clients = st.session_state.clients

def missing_docs(client):
    return [d["name"] for d in client["documents"] if d["status"] != "Recibido"]

def client_status(client):
    statuses = [d["status"] for d in client["documents"]]
    if statuses and all(s == "Recibido" for s in statuses):
        return "Completo"
    if "Revisión" in statuses:
        return "En revisión"
    return "Pendiente"

def status_badge(status):
    cls = {"Completo": "complete", "Recibido": "complete", "En revisión": "review", "Revisión": "review", "Pendiente": "pending"}.get(status, "pending")
    return f'<span class="status {cls}">{status}</span>'

def make_reminder(client):
    missing = missing_docs(client)
    if not missing:
        return (f"Hola {client['name'].split()[0]},\n\nHemos recibido toda la documentación correspondiente a {client['period']}. Gracias por enviárnosla.\n\nUn saludo,\nEquipo de la asesoría")
    docs = "\n".join(f"• {name}" for name in missing)
    return (f"Hola {client['name'].split()[0]},\n\nEstamos revisando la documentación de {client['period']} y todavía nos faltan estos documentos:\n\n{docs}\n\nCuando puedas, envíanoslos mediante el canal seguro que utilizamos habitualmente. Si ya los has enviado, puedes ignorar este mensaje.\n\nGracias,\nEquipo de la asesoría")

def get_client(client_id):
    return next((c for c in clients if c["id"] == client_id), clients[0] if clients else None)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#172B4D; --muted:#667085; --line:#E7ECF2; --teal:#0F8B8D; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
.block-container { max-width: 1440px; padding-top: 1.8rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background:#F7F9FC; border-right:1px solid #E7ECF2; }
.brand { font-family:'Manrope',sans-serif; color:var(--ink); font-size:1.55rem; font-weight:800; letter-spacing:-.055em; }
.brand-mark { display:inline-flex; width:36px; height:36px; border-radius:11px; background:#172B4D; color:white; align-items:center; justify-content:center; margin-right:9px; font-size:1rem; }
.eyebrow { color:#0F8B8D; text-transform:uppercase; letter-spacing:.12em; font-size:.72rem; font-weight:700; margin-bottom:.35rem; }
.page-title { font-family:'Manrope',sans-serif; color:#172B4D; font-size:2rem; font-weight:800; letter-spacing:-.055em; line-height:1.15; margin-bottom:.35rem; }
.page-subtitle { color:#667085; font-size:.98rem; margin-bottom:1.35rem; }
.kpi { border:1px solid #E7ECF2; border-radius:16px; background:#fff; padding:18px 20px; min-height:120px; }
.kpi-label { color:#667085; font-size:.85rem; font-weight:600; }
.kpi-value { font-family:'Manrope',sans-serif; color:#172B4D; font-size:2rem; font-weight:800; letter-spacing:-.05em; margin-top:8px; line-height:1.05; }
.kpi-note { color:#667085; font-size:.78rem; margin-top:8px; }
.section-title { font-family:'Manrope',sans-serif; color:#172B4D; font-size:1.15rem; font-weight:800; letter-spacing:-.025em; margin:1.4rem 0 .25rem; }
.helper { color:#667085; font-size:.88rem; margin-bottom:.9rem; }
.status { display:inline-block; border-radius:999px; padding:4px 9px; font-size:.76rem; font-weight:700; white-space:nowrap; }
.status.complete { background:#E7F6EF; color:#16794B; }
.status.pending { background:#FFF3D9; color:#946200; }
.status.review { background:#FCE9E7; color:#B42318; }
.info-strip { background:#F3F7FB; border:1px solid #E4EBF3; border-radius:12px; padding:13px 15px; color:#475467; font-size:.86rem; }
.client-card { border:1px solid #E7ECF2; border-radius:14px; padding:15px 17px; background:#fff; }
div[data-testid="stMetric"] { background:#fff; border:1px solid #E7ECF2; border-radius:14px; padding:15px 18px; }
.stButton button, .stFormSubmitButton button { border-radius:10px; font-weight:600; min-height:2.7rem; }
.stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea { border-radius:10px; }
hr { border-color:#E7ECF2; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">DF</span>DocuFlow</div>', unsafe_allow_html=True)
    st.caption("CONTROL DOCUMENTAL · ASESORÍAS")
    st.write("")
    st.markdown("**ESPACIO DE TRABAJO**")
    page = st.radio("Navegación", ["Resumen", "Clientes", "Recordatorios", "Añadir cliente"], label_visibility="collapsed", key="main_nav")
    st.divider()
    st.markdown("**Periodo activo**")
    st.caption("3T 2026 · Trimestre actual de la demo")
    st.write("")
    st.markdown('<div class="info-strip">🧪 <b>Modo demostración</b><br>Los datos son ficticios. Los cambios se guardan solo durante esta sesión y los correos no se envían.</div>', unsafe_allow_html=True)
    st.write("")
    st.caption("DocuFlow · Prototipo de validación")

# Global totals
all_docs = [d for c in clients for d in c["documents"]]
received = sum(d["status"] == "Recibido" for d in all_docs)
pending = sum(d["status"] == "Pendiente" for d in all_docs)
review = sum(d["status"] == "Revisión" for d in all_docs)
complete_clients = sum(client_status(c) == "Completo" for c in clients)
attention_clients = [c for c in clients if client_status(c) != "Completo"]

if page == "Resumen":
    st.markdown('<div class="eyebrow">TU ASESORÍA, DE UN VISTAZO</div><div class="page-title">Buenos días 👋</div><div class="page-subtitle">Aquí tienes lo importante para mantener la documentación al día.</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1: st.markdown(f'<div class="kpi"><div class="kpi-label">Clientes</div><div class="kpi-value">{len(clients)}</div><div class="kpi-note">En el periodo activo</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi"><div class="kpi-label">Expedientes completos</div><div class="kpi-value">{complete_clients}</div><div class="kpi-note">De {len(clients)} clientes</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi"><div class="kpi-label">Documentos pendientes</div><div class="kpi-value">{pending}</div><div class="kpi-note">Aún no recibidos</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi"><div class="kpi-label">Necesitan revisión</div><div class="kpi-value">{review}</div><div class="kpi-note">Requieren atención manual</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown('<div class="section-title">Pendientes de atención</div><div class="helper">Empieza por estos clientes para desbloquear los expedientes.</div>', unsafe_allow_html=True)
        if attention_clients:
            rows = []
            for c in attention_clients:
                rows.append({"Empresa": c["company"], "Contacto": c["name"], "Documentos por resolver": len(missing_docs(c)), "Estado": client_status(c)})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, column_config={"Documentos por resolver": st.column_config.NumberColumn(format="%d")})
            chosen = st.selectbox("Ir directamente a un cliente", [c["id"] for c in attention_clients], format_func=lambda cid: get_client(cid)["company"], label_visibility="collapsed", key="dashboard_client")
            if st.button("Revisar cliente →", type="primary", use_container_width=True):
                st.session_state.selected_client_id = chosen
                st.session_state.main_nav = "Clientes"
                st.rerun()
        else:
            st.success("¡Todo al día! No hay expedientes pendientes.")
    with right:
        st.markdown('<div class="section-title">Estado de la documentación</div><div class="helper">Progreso de recepción de documentos.</div>', unsafe_allow_html=True)
        if all_docs:
            st.progress(received / len(all_docs), text=f"{received} de {len(all_docs)} documentos recibidos")
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #E7ECF2"><span>Recibidos</span>{status_badge("Recibido")} <b>{received}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #E7ECF2"><span>Pendientes</span>{status_badge("Pendiente")} <b>{pending}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;justify-content:space-between;padding:9px 0"><span>En revisión</span>{status_badge("Revisión")} <b>{review}</b></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="info-strip">💡 <b>Consejo:</b> actualiza el estado de cada documento cuando lo recibas. Así podrás identificar rápidamente a quién escribir y qué falta.</div>', unsafe_allow_html=True)

elif page == "Clientes":
    st.markdown('<div class="eyebrow">GESTIÓN DE EXPEDIENTES</div><div class="page-title">Clientes y documentos</div><div class="page-subtitle">Consulta cada expediente y actualiza la documentación pendiente.</div>', unsafe_allow_html=True)
    search_col, status_col = st.columns([2, 1])
    with search_col: search = st.text_input("Buscar", placeholder="Busca por empresa o nombre de contacto", label_visibility="collapsed")
    with status_col: status_filter = st.selectbox("Filtrar por estado", ["Todos los estados", "Pendiente", "En revisión", "Completo"], label_visibility="collapsed")
    filtered = [c for c in clients if search.lower() in (c["name"] + " " + c["company"]).lower() and (status_filter == "Todos los estados" or client_status(c) == status_filter)]
    st.caption(f"{len(filtered)} clientes · periodo 3T 2026")
    if not filtered:
        st.info("No hay clientes que coincidan. Prueba con otra búsqueda o filtro.")
    else:
        labels = {c["id"]: f'{c["company"]} · {c["name"]}' for c in filtered}
        valid_ids = [c["id"] for c in filtered]
        if st.session_state.selected_client_id not in valid_ids:
            st.session_state.selected_client_id = valid_ids[0]
        selected_id = st.selectbox("Selecciona un expediente", valid_ids, format_func=lambda cid: labels[cid], key="client_picker")
        st.session_state.selected_client_id = selected_id
        client = get_client(selected_id)
        a, b = st.columns([2, 1])
        with a:
            st.markdown(f'<div class="section-title" style="margin-top:.3rem">{client["company"]}</div><div class="helper">{client["name"]} · {client["email"]} · Periodo {client["period"]}</div>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div style="text-align:right;padding-top:1rem">{status_badge(client_status(client))}</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="section-title" style="margin-top:.2rem">Lista de documentación</div><div class="helper">Cambia el estado en cuanto recibas o revises un documento.</div>', unsafe_allow_html=True)
        for idx, doc in enumerate(client["documents"]):
            name_col, state_col = st.columns([2, 1])
            with name_col:
                icon = "✓" if doc["status"] == "Recibido" else ("!" if doc["status"] == "Revisión" else "○")
                st.markdown(f'**{icon} &nbsp; {doc["name"]}**')
                st.caption({"Recibido":"Documento recibido", "Pendiente":"Pendiente de recibir", "Revisión":"Comprobar el documento"}[doc["status"]])
            with state_col:
                new_status = st.selectbox("Estado", STATUSES, index=STATUSES.index(doc["status"]), key=f"doc_{client['id']}_{idx}", label_visibility="collapsed")
                if new_status != doc["status"]:
                    doc["status"] = new_status
                    st.rerun()
            st.divider()
        st.markdown("**Siguiente acción**")
        if missing_docs(client):
            st.write(f"Faltan por resolver **{len(missing_docs(client))} documentos**.")
            if st.button("Preparar recordatorio para este cliente", type="primary", use_container_width=True):
                st.session_state.selected_client_id = client["id"]
                st.session_state.main_nav = "Recordatorios"
                st.rerun()
        else:
            st.success("Este expediente está completo. No hace falta enviar un recordatorio.")

elif page == "Recordatorios":
    st.markdown('<div class="eyebrow">COMUNICACIÓN CON CLIENTES</div><div class="page-title">Recordatorios</div><div class="page-subtitle">Prepara un mensaje personalizado con la documentación que falta. Tú decides cuándo y cómo enviarlo.</div>', unsafe_allow_html=True)
    if not clients:
        st.info("Añade un cliente para empezar.")
    else:
        ids = [c["id"] for c in clients]
        default_id = st.session_state.selected_client_id if st.session_state.selected_client_id in ids else ids[0]
        selected_id = st.selectbox("Cliente destinatario", ids, index=ids.index(default_id), format_func=lambda cid: get_client(cid)["company"])
        client = get_client(selected_id)
        missing = missing_docs(client)
        if missing:
            st.markdown(f'<div class="info-strip">📌 A este cliente le faltan <b>{len(missing)} documentos</b>: {", ".join(missing)}.</div>', unsafe_allow_html=True)
        else:
            st.success("La documentación está completa. Puedes usar el mensaje para confirmar la recepción.")
        st.write("")
        with st.form("reminder_form"):
            subject = st.text_input("Asunto", value=f'Documentación pendiente · {client["period"]}')
            message = st.text_area("Mensaje", value=make_reminder(client), height=260)
            submitted = st.form_submit_button("Guardar borrador en esta sesión", type="primary", use_container_width=True)
        if submitted:
            st.session_state.reminder_log.append({"cliente": client["company"], "fecha": date.today().strftime("%d/%m/%Y"), "asunto": subject, "estado": "Borrador preparado"})
            st.success("Borrador registrado en esta sesión. No se ha enviado ningún correo.")
        st.caption("El envío de correos no está conectado. Usa únicamente datos ficticios en esta demo.")
        if st.session_state.reminder_log:
            st.markdown('<div class="section-title">Actividad reciente</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(st.session_state.reminder_log[::-1]), hide_index=True, use_container_width=True)

elif page == "Añadir cliente":
    st.markdown('<div class="eyebrow">NUEVO EXPEDIENTE</div><div class="page-title">Añadir cliente</div><div class="page-subtitle">Crea un cliente de ejemplo para probar el flujo de trabajo.</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-strip">⚠️ Esta versión es una demo. No introduzcas nombres, emails ni información fiscal reales.</div>', unsafe_allow_html=True)
    st.write("")
    with st.form("add_client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre de contacto", placeholder="Ej. Alex García")
            company = st.text_input("Empresa", placeholder="Ej. Empresa Demo SL")
        with col2:
            email = st.text_input("Email ficticio", placeholder="contacto.demo@example.com")
            period = st.selectbox("Periodo", ["3T 2026", "4T 2026", "Mensual · octubre 2026", "Otro"])
        submitted = st.form_submit_button("Crear expediente", type="primary", use_container_width=True)
    if submitted:
        if not name.strip() or not company.strip() or not email.strip():
            st.error("Completa los tres campos para crear el expediente.")
        elif "@" not in email or "example.com" not in email.lower():
            st.error("Para esta demo, utiliza un email ficticio terminado en example.com.")
        else:
            new_id = max([c["id"] for c in clients], default=0) + 1
            clients.append({"id": new_id, "name": name.strip(), "company": company.strip(), "email": email.strip(), "period": period, "documents": [{"name":"Facturas emitidas","status":"Pendiente"},{"name":"Facturas recibidas","status":"Pendiente"},{"name":"Extracto bancario","status":"Pendiente"}]})
            st.session_state.selected_client_id = new_id
            st.success(f"Expediente de demo creado: {company}")
            st.rerun()

st.divider()
st.caption("DocuFlow · Prototipo de validación · Datos temporales y ficticios. No gestiona documentación real, no tiene usuarios ni envía correos.")

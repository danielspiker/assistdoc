"""AssistDoc — Frontend Streamlit (S4 + S5 + S7).

Login, RBAC (aluno/admin), chat com RAG/Long Context, painel admin.

Rodar (com a API ja no ar):
    streamlit run frontend/app.py
"""
import os

import requests
import streamlit as st

API_BASE = os.getenv("ASSISTDOC_API", "http://127.0.0.1:8001")
TIMEOUT = 180

st.set_page_config(page_title="AssistDoc", page_icon="📚", layout="wide")


# --- Cliente HTTP -----------------------------------------------------------

def _headers() -> dict:
    tok = st.session_state.get("token")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def _get(path: str, **kw):
    return requests.get(f"{API_BASE}{path}", headers=_headers(), timeout=kw.pop("timeout", 10), **kw)


def _post(path: str, json=None, files=None, params=None, timeout=TIMEOUT):
    return requests.post(f"{API_BASE}{path}", headers=_headers(), json=json,
                         files=files, params=params, timeout=timeout)


def _check_api() -> bool:
    try:
        return requests.get(f"{API_BASE}/health", timeout=5).status_code == 200
    except requests.RequestException:
        return False


def _logged_in() -> bool:
    return bool(st.session_state.get("token"))


def _is_admin() -> bool:
    return st.session_state.get("role") == "admin"


# --- Tela de login/registro -------------------------------------------------

def screen_login():
    st.title("📚 AssistDoc — Login")
    tab_login, tab_reg = st.tabs(["Entrar", "Cadastrar"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            ok = st.form_submit_button("Entrar")
        if ok:
            try:
                r = _post("/auth/login", json={"email": email, "password": senha},
                          timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["role"] = data["role"]
                    st.session_state["email"] = email
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Falha no login."))
            except requests.RequestException as e:
                st.error(f"Erro de rede: {e}")

    with tab_reg:
        st.caption("Cadastro publico cria perfil **aluno**. Admin e criado via "
                   "`python -m backend.create_admin ...`.")
        with st.form("reg_form"):
            email = st.text_input("E-mail", key="reg_email")
            senha = st.text_input("Senha (>=12, maiuscula, numero, simbolo)",
                                  type="password", key="reg_pwd")
            ok = st.form_submit_button("Cadastrar")
        if ok:
            try:
                r = _post("/auth/register",
                          json={"email": email, "password": senha}, timeout=15)
                if r.status_code == 200:
                    data = r.json()
                    st.session_state["token"] = data["access_token"]
                    st.session_state["role"] = data["role"]
                    st.session_state["email"] = email
                    st.success("Conta criada e logada.")
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Falha no cadastro."))
            except requests.RequestException as e:
                st.error(f"Erro de rede: {e}")


# --- Helpers de chat --------------------------------------------------------

@st.cache_data(ttl=30)
def _list_docs(token: str) -> list[str]:
    # token no parametro so para invalidar o cache quando troca de usuario
    try:
        r = _get("/documents")
        return r.json().get("documents", []) if r.status_code == 200 else []
    except requests.RequestException:
        return []


def _query(question: str, mode: str, document: str | None) -> dict:
    if mode == "RAG":
        r = _post("/ask", json={"question": question})
    elif mode == "Long Context":
        r = _post("/ask-doc", json={"question": question, "document": document})
    else:  # Auto
        r = _post("/chat", json={"question": question, "document": document})
    r.raise_for_status()
    return r.json()


def _render_meta(data: dict) -> None:
    modo = data.get("mode")
    if modo:
        st.caption(f"modo: **{modo}**")
    sources = data.get("sources", [])
    if sources:
        with st.expander(f"📎 Fontes consultadas ({len(sources)})"):
            for s in sources:
                page = f", pagina {s['page']}" if s.get("page") is not None else ""
                st.markdown(f"**{s.get('source')}** (trecho {s.get('chunk')}{page})")
                st.caption(s.get("snippet", ""))
    docs = data.get("documents", [])
    if docs:
        st.caption("documento(s): " + ", ".join(docs))


# --- Tela de chat (aluno e admin) -------------------------------------------

def page_chat():
    st.title("📚 AssistDoc")
    st.caption("Assistente de documentos academicos — RAG + Long Context.")

    with st.sidebar:
        mode = st.radio("Modo", ["Auto", "RAG", "Long Context"],
                        help="Auto = a API decide (RF07).")
        document = None
        if mode in ("Long Context", "Auto"):
            docs = ["(base inteira)"] + _list_docs(st.session_state["token"])
            escolha = st.selectbox("Documento (Long Context)", docs)
            document = None if escolha == "(base inteira)" else escolha
        if st.button("Limpar conversa"):
            st.session_state.messages = []
            st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "data" in msg:
                _render_meta(msg["data"])

    if prompt := st.chat_input("Pergunte sobre os documentos..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(f"Consultando ({mode})..."):
                try:
                    data = _query(prompt, mode, document)
                    answer = data.get("answer", "(sem resposta)")
                except requests.HTTPError as e:
                    data = {}
                    answer = f"Erro {e.response.status_code}: {e.response.text}"
                except requests.RequestException as e:
                    data = {}
                    answer = f"Erro de rede: {e}"
            st.markdown(answer)
            _render_meta(data)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "data": data})


# --- Tela admin (upload, auditoria, usuarios) -------------------------------

def page_admin():
    st.title("⚙️ Painel administrativo")

    tabs = st.tabs(["Upload de documento", "Auditoria", "Usuarios"])

    with tabs[0]:
        st.subheader("Upload + indexacao (.txt, .pdf, .docx)")
        up = st.file_uploader("Arquivo", type=["txt", "pdf", "docx"])
        if up and st.button("Enviar e indexar"):
            with st.spinner("Indexando..."):
                files = {"file": (up.name, up.getvalue())}
                r = _post("/admin/ingest", files=files, timeout=600)
            if r.status_code == 200:
                d = r.json()
                st.success(f"Indexado: {d['document']} ({d['chunks']} chunks).")
                _list_docs.clear()
            else:
                st.error(r.json().get("detail", "Falha no upload."))

    with tabs[1]:
        st.subheader("Eventos recentes")
        limit = st.slider("Quantos eventos", 10, 200, 50)
        if st.button("Recarregar auditoria"):
            pass
        r = _get("/admin/audit", params={"limit": limit})
        if r.status_code == 200:
            st.dataframe(r.json()["logs"], use_container_width=True)
        else:
            st.error(r.json().get("detail", "Falha ao carregar auditoria."))

    with tabs[2]:
        st.subheader("Usuarios cadastrados")
        r = _get("/admin/users")
        if r.status_code == 200:
            users = r.json()["users"]
            st.dataframe(users, use_container_width=True)
            with st.expander("Ativar/desativar usuario"):
                email = st.text_input("E-mail do usuario")
                col_a, col_b = st.columns(2)
                if col_a.button("Desativar"):
                    rr = _post(f"/admin/users/{email}/active",
                               params={"active": False}, timeout=15)
                    st.write(rr.json())
                if col_b.button("Ativar"):
                    rr = _post(f"/admin/users/{email}/active",
                               params={"active": True}, timeout=15)
                    st.write(rr.json())
        else:
            st.error(r.json().get("detail", "Falha ao listar usuarios."))


# --- Cabecalho/logout -------------------------------------------------------

def header():
    with st.sidebar:
        if _check_api():
            st.success(f"API conectada\n\n{API_BASE}")
        else:
            st.error("API fora do ar.")
            st.stop()

        if _logged_in():
            st.markdown(f"👤 **{st.session_state.get('email')}**  \n"
                        f"perfil: `{st.session_state.get('role')}`")
            if st.button("Sair"):
                try:
                    _post("/auth/logout", timeout=10)
                except requests.RequestException:
                    pass
                for k in ("token", "role", "email", "messages"):
                    st.session_state.pop(k, None)
                _list_docs.clear()
                st.rerun()


# --- Roteamento principal ---------------------------------------------------

header()

if not _logged_in():
    screen_login()
else:
    if _is_admin():
        page = st.sidebar.radio("Pagina", ["Chat", "Admin"])
        if page == "Chat":
            page_chat()
        else:
            page_admin()
    else:
        page_chat()

import streamlit as st
from view.view import View


class IndexUI:


    def menu_visitante():
        pass

    def menu_cliente():
        pass
        

    def menu_admin():            
        pass

    def sair_do_sistema():
        if st.sidebar.button("Sair"):
            del st.session_state["cliente_id"]
            del st.session_state["cliente_nome"]
            st.rerun()

    def sidebar():
        st.write(st.session_state)
        if "cliente_id" not in st.session_state:
            IndexUI.menu_visitante()
        else:
            admin = st.session_state["cliente_nome"] == "admin"
            st.sidebar.write(f"Bem vindo(a), " + st.session_state["cliente_nome"])
            if admin:
                IndexUI.menu_admin()
            elif st.session_state["cliente_nome"] == "eduardo":
                IndexUI.menu_entregador()
            else:
                IndexUI.menu_cliente()
            IndexUI.sair_do_sistema()
    
    def main():
        IndexUI.sidebar()

IndexUI.main()
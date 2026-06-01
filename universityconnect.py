# UNIVERSITYCONNECT - DASHBOARD + CHATBOT

import streamlit as st
import openpyxl
import plotly.express as px
import pandas as pd
import os
import pdfplumber

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="UniversityConnect", 
                  page_icon=":books:", 
                  layout="wide")
st.title(":books: UniversityConnect")

pagina_selezionata = st.sidebar.radio(
    "Seleziona il servizio che ti interessa:",
    options=[":bar_chart: Dashboard Risorse", ":robot: Chatbot IA"]
)

if pagina_selezionata == ":bar_chart: Dashboard Risorse":
    st.header(":bar_chart: Dashboard - Risorse Universitarie")
    
    file = st.file_uploader(":file_folder: Carica il file con le risorse",
                                     type=("csv", "txt", "xlsx", "xls"))

    if file is not None:
        filename = file.name
        st.write(file.name) #dall'oggetto file estrai il nome
        dati = pd.read_excel(file)
        
        if 'Data' in dati.columns:
            dati["Data"] = pd.to_datetime(dati["Data"])
            startDate = pd.to_datetime(dati["Data"]).min() #creiamo due oggetti. l'inizio (start). prendi il modulo todate e prendi il valore piu basso(la data meno recente) all'interno di dati date
            endDate = pd.to_datetime(dati["Data"]).max() #la data finale che prendo in considerazione. da pandas prendo istruzone todate time e datidate prendiamo la data piu recente
            col1, col2 = st.columns(2)
            with col1:
                date1 = pd.to_datetime(st.date_input("Data iniziale", startDate)) #nella prima colonna chiediamo una data e streamlit genera un calendario dove selezioniamo la data e come dato di defoult metti start date
            with col2:
                date2 = pd.to_datetime(st.date_input("Data finale", endDate)) #anche qui "fai un input di data finale ma di defoult qui metti la data finale". quindi aprendo i calendarii a sx data iniziale a dx data finale
            dati = dati[(dati["Data"] >= date1) & (dati["Data"] <= date2)].copy()

        st.sidebar.header("Filtri Risorsa:")
        
        corso_selezionato = st.sidebar.multiselect("Seleziona il corso",
                options=dati["Corso"].unique(),
                default=dati["Corso"].unique())
        
        insegnamento_selezionato = st.sidebar.multiselect("Seleziona il insegnamento",
                options=dati["Insegnamento"].unique(),
                default=dati["Insegnamento"].unique())
        
        tipo_selezionato = st.sidebar.multiselect("Seleziona il tipo di risorsa",
                options=dati["Tipo"].unique(),
                default=dati["Tipo"].unique())
        
        dati_filtrati = dati.query(
                "Corso == @corso_selezionato & Insegnamento == @insegnamento_selezionato & Tipo == @tipo_selezionato")
        

        download_totali = int(dati_filtrati["Download"].sum())
        rating_medio = round(dati_filtrati["Rating"].mean(), 1)
        star_rating = ":star:" * int(round(rating_medio, 0))
        

        left_col, mid_col, right_col = st.columns(3)
        with left_col:
            st.subheader("Risorse:")
            st.subheader(f"{int(len(dati_filtrati))}")

        with mid_col:
            st.subheader("Download Totali:")
            st.subheader(f"{download_totali:}")

        with right_col:
            st.subheader("Rating Medio:")
            st.subheader(f"{rating_medio} {star_rating}")

        st.subheader(f"Risorse disponibili ({len(dati_filtrati)} trovate)")
        st.dataframe(dati_filtrati)

        
        st.markdown("---")
    

        st.subheader("Dettagli Risorse:")
        st.dataframe(dati_filtrati[["Titolo", "Download", "Rating"]], use_container_width=True)

        st.markdown("---")


        st.subheader("Download per Risorse")
        fig = px.bar(dati_filtrati,
                          x= "Download",
                          y= "Titolo",
                          text = [f" {x:.1f}" for x in dati_filtrati ["Download"]],
                          orientation="h",
                          template = "seaborn"
                          )
            
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=(dict(showgrid=False)))
    
        st.plotly_chart(fig, use_container_width=True, height=300)
        st.markdown("---")
        
        st.subheader("Distribuzione per Tipo")
        fig = px.pie(dati_filtrati, values="Download", names="Tipo", hole=0.5)
        fig.update_traces(text=dati_filtrati["Tipo"], textposition="inside")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Tasso di download nel tempo")

        glinea = ( #serve per creare la nuova matrice
            dati_filtrati
            .groupby("Data", as_index=False)["Download"]
            .sum()
            .sort_values(by="Data"))
 

        fig2 = px.line(
            glinea,
            x="Data",
            y="Download",
            labels={"Data": "Data", "Download": "Download"},
            height=500,
            template="gridon")
        
        fig2.update_layout(xaxis=dict(tickmode="auto")) # auto, evita di mostrare tutte le date
                                                        # con "linear" mostra tutto
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Esplora le materie per corso di studi")
        fig3 = px.treemap(dati_filtrati,
                        path=["Corso","Insegnamento", "Tipo", "Titolo"],
                        values="Download",
                        hover_data=["Download"],
                        color="Tipo")
        fig3.update_layout(width=800, height=650)
        st.plotly_chart(fig3, use_container_width=True)



        # Scatter plot
        dispersione = px.scatter(dati_filtrati,
                                x="Rating",
                                y="Download",
                                size="Download")

        dispersione.update_layout(
            title="Relazione tra Rating e Download:",
            title_font_size=20,
            xaxis_title="Rating",
            yaxis_title="Download",
            xaxis_title_font_size=19,
            yaxis_title_font_size=19)

        st.plotly_chart(dispersione, use_container_width=True)


elif pagina_selezionata == ":robot: Chatbot IA":
    
    st.header(":robot: Assistente IA - Domande su Risorse")
    
    st.info("""
    :pushpin: **Come usare il Chatbot:**
    1. Carica un PDF di una risorsa universitaria
    2. Il chatbot leggerà il documento
    3. Fai domande specifiche sul contenuto
    4. L'IA risponderà basandosi sul testo del PDF
    """)
    
#FILTRO SIDEBAR 
    st.sidebar.header("Seleziona i tuoi filtri:")
 
    sel_materia = st.sidebar.multiselect("Seleziona la materia",
            options=["Tecniche Avanzate", "Semiotica", "Diritto"],
            default=["Tecniche Avanzate"]) # di default mostra la prima materia

# in base alla materia selezionata nel multiselect
    # facciamo corrispondere il nome del file nella cartella del progetto

    if "Tecniche Avanzate" in sel_materia:
        documento = "tecniche_avanzate.pdf"
    elif "Semiotica" in sel_materia:
        documento = "semiotica.pdf"
    else:
        documento = "Costituzione_italiana.pdf"

#forse da togliere
   # documento_pdf = st.file_uploader(":file_folder: Carica un PDF:", type=["pdf"])

    if documento is not None:
        @st.cache_data(show_spinner="Sto leggendo il PDF...")
        def estrai_testo_pdf(documento: str) -> str:
            with pdfplumber.open(documento) as pdf:
                # st.write(f"Pagine totali: {len(pdf.pages)} - Comincio la scansione...")
                testo = ""
                for pagina in pdf.pages:
                    # Se la pagina è null menttiamo ""
                    testo_pagina = pagina.extract_text() or ""
                    testo = testo + testo_pagina + "\n"
                    # testo += pagina.extract_text() + "\n"
            return testo.strip()
        
        testo = estrai_testo_pdf(documento)

        @st.cache_data(show_spinner=False)
        def crea_frammenti(testo: str):
            taglierina = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=1000,
            chunk_overlap=200)
            return taglierina.split_text(testo)

        frammenti = crea_frammenti(testo)

        st.success(f":white_check_mark: PDF caricato!")

        @st.cache_resource(show_spinner=False)
        def crea_vectorstore(frammenti):
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                openai_api_key=st.secrets["OPENAI_API_KEY"])
            return FAISS.from_texts(frammenti, embedding=embeddings)
        
        vettori = crea_vectorstore(frammenti)

        st.markdown("---")

        def invia():
            st.session_state.domanda_inviata = st.session_state.domanda_utente
            st.session_state.domanda_utente = ""

        st.text_input("Chiedi al chatbot:", key="domanda_utente", on_change=invia)
        
        domanda_utente = st.session_state.get("domanda_inviata", "")

        
        def formatta_documento(documenti):
            return "\n\n".join([documento_pdf.page_content for documento_pdf in documenti])
            
        prompt = ChatPromptTemplate.from_messages([
        ("system", 
         '''Sei un assistente virtuale. 
    Usa prevalentemente il contesto fornito per rispondere alla domanda in modo conciso 
    e se necessario accedi a Internet per integrare le informazioni aggiuntive.
    Se proprio non conosci la risposta, dì semplicemente 'Non sono in grado di rispondere'. 
    Contesto:\n{context}'''),
        ("human", "{question}")
        ])

        comparatore = vettori.as_retriever(
        # mmr = maximal marginal relevance
            search_type="mmr",
        # Ritorna i 4 frammenti più simili
            search_kwargs={"k": 4})
    
        modello_llm = ChatOpenAI(
            model="gpt-5.4-nano",
            temperature=0.3,
            max_tokens=1000,
            openai_api_key=st.secrets["OPENAI_API_KEY"])
    
        catena = (
        # All'inizio mettiamo un dizionario che serve a costruire 
        # la struttura che il prompt vuol in input
        # Il comparatore produce i documenti (es. k=4) e li passa alla formattazione
        # RunnablePassthrough() vuol dire:
        # quando arriverà un input → passalo così com’è
        # Dobbiamo fare così perché ancora l'input concreto non c'è!  
            {"context": comparatore | formatta_documento, 
            "question": RunnablePassthrough()}
            | prompt
            | modello_llm
            | StrOutputParser()
            )
        # StrOutputParser() prende l’output del modello 
        # e lo traforma in una stringa semplice (senza aggiunta di info ecc.)
    
        if domanda_utente:
                risposta = catena.invoke(domanda_utente)
                st.write(risposta)

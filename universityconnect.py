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

st.markdown("---")

st.markdown("""
:mortar_board: *Benvenuto su UniversityConnect*

:books: **UniversityConnect** è la piattaforma che ti aiuta a trovare in pochi secondi le risorse universitarie più utili per il tuo percorso di studi. Grazie alla nostra Intelligenza Artificiale, puoi accedere a riassunti, slide, sbobine e altri materiali relativi agli insegnamenti del tuo corso di laurea.

:mag: **Come funziona?** È semplicissimo: utilizza i filtri nella barra laterale per selezionare il tuo corso di laurea, la materia e il tipo di risorsa che stai cercando. La nostra IA analizzerà il database e ti indicherà i materiali più pertinenti alle tue esigenze.

:robot: Con il **Piano Base** puoi interrogare la chatbot che consulterà le risorse disponibili in base ai filtri selezionati.

:star: Con il **Piano Pro** puoi scaricare i materiali, accedere a funzionalità esclusive e sfruttare al massimo tutte le potenzialità della piattaforma.

:rocket: **Studia in modo più intelligente**, risparmia tempo e trova subito ciò che ti serve con UniversityConnect.
""")


st.markdown("---")


pagina_selezionata = st.sidebar.radio(
    "Seleziona il servizio che ti interessa:",
    options=[":bust_in_silhouette: Profilo Studente",":bar_chart: Dashboard Risorse", ":robot: Chatbot IA",]
)

if pagina_selezionata == ":bar_chart: Dashboard Risorse":
    st.header(":bar_chart: Archivio - Risorse Universitarie")
    

    dati = pd.read_excel("risorse_uniconnect.xlsx")
        
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
        
        insegnamento_selezionato = st.sidebar.multiselect("Seleziona l'insegnamento",
                options=dati["Insegnamento"].unique(),
                default=dati["Insegnamento"].unique())
        
        tipo_selezionato = st.sidebar.multiselect("Seleziona il tipo di risorsa",
                options=dati["Tipo"].unique(),
                default=dati["Tipo"].unique())
        
        dati_filtrati = dati.query(
                "Corso == @corso_selezionato & Insegnamento == @insegnamento_selezionato & Tipo == @tipo_selezionato")
        
        if not corso_selezionato or not insegnamento_selezionato or not tipo_selezionato:
            st.warning(":warning: Seleziona almeno un'opzione per ogni filtro dalla barra laterale!")
            st.stop()
        elif dati_filtrati.empty:
            st.warning(":warning: Nessuna risorsa corrisponde ai filtri selezionati.")
            st.stop()

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
        st.subheader(":arrow_down: Scarica Documento")

        import requests

        CORSI = [
            "Comunicazione Pubblica, d'impresa e pubblicità",
            "Comunicazione per l'enogastronomia",
            "Comunicazione del patrimonio culturale",
            "Archeologia",
            "Cooperazione, sviluppo e migrazioni",
            "Educazione al patrimonio archeologico e artistico",
            "Religioni e culture",
            "Scienze dell'antichità",
            "Servizio sociale, diseguaglianze e vulnerabilità sociale",
            "Storia dell'arte",
            "Studi storici, antropologici e geografici"
        ]

        corso_download = st.selectbox(
            ":mortar_board: Seleziona il Corso di Laurea:",
            options=CORSI,
            index=0
        )

        response = requests.get(
            f"https://api.github.com/repos/oscarsimonedanca-commits/universityconnect/contents/documenti/{corso_download}"
        )

        st.markdown("**File disponibili:**")

        if response.status_code == 200:
            files = [f for f in response.json() if f["name"].endswith(".pdf")]
            if files:
                for file in files:
                    file_response = requests.get(
                        f"https://raw.githubusercontent.com/oscarsimonedanca-commits/universityconnect/main/documenti/{corso_download}/{file['name']}"
                    )
                    st.download_button(
                        label=f":page_facing_up: {file['name']}",
                        data=file_response.content,
                        file_name=file["name"],
                        mime="application/pdf",
                        key=file["name"]
                    )
            else:
                st.info(":pushpin: Nessun PDF disponibile per questo corso.")
        else:
            st.info(":pushpin: Nessun documento trovato per questo corso.")
        
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
    1. Seleziona i filtri dalla barra laterale
    2. Il chatbot leggerà i documenti
    3. Fai domande specifiche sul contenuto
    """)
    
    #FILTRO SIDEBAR 
    st.sidebar.header("Seleziona i tuoi filtri:")
 
    sel_materia = st.sidebar.multiselect("Seleziona la materia",
            options=[
                "Tecniche Avanzate per la Ricerca Sociale",
                "Semiotica",
                "Semiotica 5",
                "Marketing Digitale",
                "Sociologia dei Fenomeni Politici",
                "Laboratorio di Scienze Sociali Computazionali",
                "Criminalità Organizzata"
            ],
            default=["Tecniche Avanzate per la Ricerca Sociale"])

# in base alla materia selezionata nel multiselect
    # facciamo corrispondere il nome del file nella cartella del progetto

    if "Tecniche Avanzate per la Ricerca Sociale" in sel_materia:
        documento = "TECHINCHE AVANZATE PER LA RICERCA SOCIALE.pdf"
    elif "Semiotica" in sel_materia:
        documento = "SEMIOTICA.pdf"
    elif "Semiotica 5" in sel_materia:
        documento = "SEMIOTICA 5.pdf"
    elif "Marketing Digitale" in sel_materia:
        documento = "MARKETING DIGITALE.pdf"
    elif "Sociologia dei Fenomeni Politici" in sel_materia:
        documento = "SOCIOLOGIA DEI FENOMENI POLITICI 6.pdf"
    elif "Laboratorio di Scienze Sociali Computazionali" in sel_materia:
        documento = "Laboratorio di scienze sociali computazionali.pdf"
    else:
        documento = "CRIMINALITÀ ORGANIZZATA 3.pdf"


    if not sel_materia:
        st.warning(":warning: Seleziona almeno una materia dalla barra laterale per usare il Chatbot!")
    elif documento is not None:
        import requests
        import tempfile

        @st.cache_data(show_spinner="Sto leggendo il PDF...")
        def estrai_testo_pdf(documento: str) -> str:
            url = f"https://raw.githubusercontent.com/oscarsimonedanca-commits/universityconnect/main/documenti/Comunicazione Pubblica, d'impresa e pubblicità/{documento}"
            url = url.replace(" ", "%20").replace("'", "%27")
            response = requests.get(url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            with pdfplumber.open(tmp_path) as pdf:
                testo = ""
                for pagina in pdf.pages:
                    testo_pagina = pagina.extract_text() or ""
                    testo = testo + testo_pagina + "\n"
            return testo.strip()
        
        testo = estrai_testo_pdf(documento) #cambiato in documento, prima era documento_pdf

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
    Quando attingi ad informazioni esterne al contesto fornito esplicitalo chiaramente.
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
                    
elif pagina_selezionata == ":bust_in_silhouette: Profilo Studente":
    st.header(":bust_in_silhouette: Profilo Studente")
    
    if "profilo" not in st.session_state:
        st.session_state.profilo = {
            "nome": "Mario Rossi",
            "matricola": "0812345",
            "corso": "Comunicazione Pubblica, d'impresa e pubblicità",
            "anno": "Magistrale 2°",
            "email": "mario.rossi@unipa.it",
            "download_miei": 340,
            "rating_medio": 4.6,
        }

    p = st.session_state.profilo

    prof_col1, prof_col2 = st.columns([3, 1])
    
    with prof_col1:
        st.subheader(f":red_circle: {p['nome']}")
        st.markdown(f"**Matricola:** {p['matricola']}")
        st.markdown(f"**Corso:** {p['corso']}")
        st.markdown(f"**Anno:** {p['anno']}")
        st.markdown(f"**Email:** {p['email']}")
    
    with prof_col2:
        st.markdown("""
        <div style='background-color:#FFD700; padding:15px; border-radius:10px; text-align:center;'>
            <h3 style='color:#333; margin:0;'>:star: Piano Pro</h3>
            <p style='color:#333; margin:5px 0 0 0; font-size:0.85em;'>Accesso completo</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(":bar_chart: Statistiche Personali")

    stat_col1, stat_col2 = st.columns(2)
    with stat_col1:
        st.metric(":arrow_down: Download risorse ", p['download_miei'])
    with stat_col2:
        st.metric(":star: Rating Medio", f"{p['rating_medio']:.1f}")

    st.markdown("---")
    st.subheader(":notebook: Libretto Universitario")

    if "esami" not in st.session_state:
        st.session_state.esami = [
            {"materia": "Semiotica", "cfu": 12, "voto": 25, "data": "2024-06-10"},
            {"materia": "Tecniche Avanzate per la Ricerca Sociale", "cfu": 9, "voto": 30, "data": "2024-07-15"},
            {"materia": "Digital Marketing", "cfu": 6, "voto": 28, "data": "2024-09-05"},
            {"materia": "Laboratorio di Scienze Sociali Computazionali", "cfu": 10, "voto": 30, "data": "2025-01-20"},
            {"materia": "Sociologia dei Fenomeni Politici", "cfu": 9, "voto": 27, "data": "2025-02-14"},
    ]

    def calcola_media(esami):
        if not esami:
            return 0, 0
        totale_cfu = sum(e["cfu"] for e in esami)
        media = sum(e["voto"] * e["cfu"] for e in esami) / totale_cfu
        return round(media, 2), totale_cfu

    media_calcolata, cfu_totali = calcola_media(st.session_state.esami)

    lib_col1, lib_col2, lib_col3 = st.columns(3)
    with lib_col1:
        st.metric(":mortar_board: Esami Sostenuti", len(st.session_state.esami))
    with lib_col2:
        st.metric(":books: CFU Totali", cfu_totali)
    with lib_col3:
        st.metric(":star: Media Ponderata", f"{media_calcolata:.2f}")

    
    with st.form("form_esame"):
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            nuova_materia = st.text_input("Materia:")
        with col_e2:
            nuovi_cfu = st.selectbox("CFU:", options=[3, 6, 9, 10, 12])
        with col_e3:
            nuovo_voto = st.slider("Voto:", min_value=18, max_value=30, value=27)
        with col_e4:
            nuova_data = st.date_input("Data esame:")
        
        aggiungi = st.form_submit_button(":floppy_disk: Aggiungi Esame")
        if aggiungi:
            if nuova_materia.strip() == "":
                st.error(":warning: Inserisci il nome della materia!")
            else:
                st.session_state.esami.append({
                    "materia": nuova_materia.strip(),
                    "cfu": nuovi_cfu,
                    "voto": nuovo_voto,
                    "data": str(nuova_data)
                })
                st.success(f":white_check_mark: Esame '{nuova_materia}' aggiunto!")
                st.rerun()

    if st.session_state.esami:
        st.markdown("**Esami sostenuti:**")
        df_esami = pd.DataFrame(st.session_state.esami)
        df_esami["data"] = pd.to_datetime(df_esami["data"])
        df_esami = df_esami.sort_values("data")
        st.dataframe(df_esami.rename(columns={
            "materia": "Materia",
            "cfu": "CFU",
            "voto": "Voto",
            "data": "Data"
        }), use_container_width=True, hide_index=True)

        if st.session_state.esami:
            st.markdown("**:wastebasket: Elimina esame:**")
            materie_lista = [e["materia"] for e in st.session_state.esami]
            esame_da_eliminare = st.selectbox("Seleziona esame da eliminare:", options=materie_lista)
            if st.button(":wastebasket: Elimina"):
                st.session_state.esami = [e for e in st.session_state.esami if e["materia"] != esame_da_eliminare]
                st.success(f":white_check_mark: Esame '{esame_da_eliminare}' eliminato!")
                st.rerun()

        st.markdown("---")
        st.subheader(":chart_with_upwards_trend: Andamento Voti nel Tempo")
        fig_andamento = px.line(
            df_esami,
            x="data",
            y="voto",
            text="materia",
            markers=True,
            labels={"data": "Data", "voto": "Voto", "materia": "Materia"},
            template="seaborn"
        )
        fig_andamento.update_traces(textposition="top center")
        fig_andamento.update_layout(
            yaxis=dict(range=[17, 31]),
            xaxis_title="Data",
            yaxis_title="Voto"
        )
        st.plotly_chart(fig_andamento, use_container_width=True)

        st.markdown("---")
    st.subheader(":open_file_folder: Le Mie Risorse")

    # Risorse di default
    if "mie_risorse" not in st.session_state:
        st.session_state.mie_risorse = [
            {"titolo": "Appunti Semiotica", "materia": "Semiotica", "tipo": "Appunti", "data": "2024-06-10"},
            {"titolo": "Slide Tecniche Avanzate", "materia": "Tecniche Avanzate per la Ricerca Sociale", "tipo": "Slide", "data": "2024-07-15"},
        ]

    #TABELLA RISORSE
    if st.session_state.mie_risorse:
        df_risorse_studente = pd.DataFrame(st.session_state.mie_risorse)
        st.dataframe(df_risorse_studente.rename(columns={
            "titolo": "Titolo",
            "materia": "Materia",
            "tipo": "Tipo",
            "data": "Data"
        }), use_container_width=True, hide_index=True)
    else:
        st.info(":pushpin: Non hai ancora caricato nessuna risorsa.")

    #AGGIUNGI RISORSA 
    st.markdown("**:heavy_plus_sign: Aggiungi nuova risorsa:**")
    with st.form("form_risorsa"):
        ris_col1, ris_col2 = st.columns(2)
        with ris_col1:
            nuovo_titolo = st.text_input("Titolo risorsa:")
            nuova_materia_ris = st.text_input("Materia:")
        with ris_col2:
            nuovo_tipo_ris = st.selectbox("Tipo:", options=[
                "Appunti", "Slide", "Sbobine", "Esercizi", "Riassunto"
            ])
            nuova_data_ris = st.date_input("Data caricamento:")
        
        nuovo_file = st.file_uploader("Carica file PDF:", type=["pdf"])
        
        aggiungi_ris = st.form_submit_button(":floppy_disk: Carica Risorsa")
        if aggiungi_ris:
            if nuovo_titolo.strip() == "":
                st.error(":warning: Inserisci il titolo della risorsa!")
            elif nuovo_file is None:
                st.error(":warning: Carica un file PDF!")
            else:
                # Salva il PDF nella cartella "risorse_inviate"
                import os
                os.makedirs("risorse_inviate", exist_ok=True)
                nome_file = f"{nuovo_titolo.strip().replace(' ', '_')}_{nuova_data_ris}.pdf"
                with open(f"risorse_inviate/{nome_file}", "wb") as f:
                    f.write(nuovo_file.getbuffer())
                
                st.session_state.mie_risorse.append({
                    "titolo": nuovo_titolo.strip(),
                    "materia": nuova_materia_ris,
                    "tipo": nuovo_tipo_ris,
                    "data": str(nuova_data_ris)
                })
                st.success(f":white_check_mark: Risorsa '{nuovo_titolo}' inviata per revisione!")
                st.balloons()
                st.rerun()

    #ELIMINA RISORSA
    if st.session_state.mie_risorse:
        st.markdown("**:wastebasket: Elimina risorsa:**")
        titoli_lista = [r["titolo"] for r in st.session_state.mie_risorse]
        risorsa_da_eliminare = st.selectbox("Seleziona risorsa da eliminare:", options=titoli_lista)
        if st.button(":wastebasket: Elimina risorsa"):
            st.session_state.mie_risorse = [r for r in st.session_state.mie_risorse if r["titolo"] != risorsa_da_eliminare]
            st.success(f":white_check_mark: Risorsa '{risorsa_da_eliminare}' eliminata!")
            st.rerun()



        st.subheader(":pencil2: Modifica Profilo")

        with st.form("form_profilo"):
            nuovo_nome = st.text_input("Nome e Cognome:", value=p['nome'])
            nuovo_corso = st.selectbox("Corso di Laurea:",
                options=["Comunicazione Pubblica, d'impresa e pubblicità", "Comunicazione per l'enogastronomia","Comunicazione del patrimonio culturale", "Archeologia", "Cooperazione, sviluppo e migrazioni","Educazione al patrimonio archeologico e artistico","Religioni e culture","Scienze dell'antichità","Servizio sociale,diseguaglianze e vulnerabilità sociale","Storia dell'arte","Studi storici, antropologici e geografici"],
                index=["Comunicazione Pubblica, d'impresa e pubblicità", "Comunicazione per l'enogastronomia","Comunicazione del patrimonio culturale", "Archeologia", "Cooperazione, sviluppo e migrazioni","Educazione al patrimonio archeologico e artistico","Religioni e culture","Scienze dell'antichità","Servizio sociale,diseguaglianze e vulnerabilità sociale","Storia dell'arte","Studi storici, antropologici e geografici"].index(p['corso'])
                if p['corso'] in ["Comunicazione Pubblica, d'impresa e pubblicità", "Comunicazione per l'enogastronomia","Comunicazione del patrimonio culturale", "Archeologia", "Cooperazione, sviluppo e migrazioni","Educazione al patrimonio archeologico e artistico","Religioni e culture","Scienze dell'antichità","Servizio sociale,diseguaglianze e vulnerabilità sociale","Storia dell'arte","Studi storici, antropologici e geografici"] else 0)
            nuovo_anno = st.selectbox("Anno di Corso:",
                options=["Magistrale 1°", "Magistrale 2°"],
                index=["Magistrale 1°", "Magistrale 2°"].index(p['anno'])
                if p['anno'] in ["Magistrale 1°", "Magistrale 2°"] else 0)
            nuova_email = st.text_input("Email:", value=p['email'])
            salva = st.form_submit_button(":floppy_disk: Salva Modifiche")
            if salva:
                st.session_state.profilo['nome'] = nuovo_nome
                st.session_state.profilo['corso'] = nuovo_corso
                st.session_state.profilo['anno'] = nuovo_anno
                st.session_state.profilo['email'] = nuova_email
                st.success(":white_check_mark: Profilo aggiornato con successo!")
                st.rerun()

        st.markdown("---")
        st.subheader(":gear: Impostazioni")

        if "impostazioni" not in st.session_state:
            st.session_state.impostazioni = {
                "notifiche": True,
                "email_risorse": True,
                "lingua": "Italiano"
            }

        with st.form("form_impostazioni"):
            notifiche = st.toggle(":bell: Abilita notifiche", value=st.session_state.impostazioni['notifiche'])
            email_risorse = st.toggle(":email: Email su nuove risorse", value=st.session_state.impostazioni['email_risorse'])
            lingua = st.selectbox(":globe_with_meridians: Lingua:", options=["Italiano", "English"],
                index=["Italiano", "English"].index(st.session_state.impostazioni['lingua']))
            salva_imp = st.form_submit_button(":floppy_disk: Salva Impostazioni")
            if salva_imp:
                st.session_state.impostazioni['notifiche'] = notifiche
                st.session_state.impostazioni['email_risorse'] = email_risorse
                st.session_state.impostazioni['lingua'] = lingua
                st.success(":white_check_mark: Impostazioni salvate!")


st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>UniversityConnect © 2026 | Laboratorio di Scienze Sociali Computazionali</p>
        <p>Made with :hearts: | <a href='#'>Privacy Policy</a> | <a href='#'>Contatti</a></p>
    </div>
    """,
    unsafe_allow_html=True
)




 

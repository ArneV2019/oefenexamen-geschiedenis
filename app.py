import streamlit as st
import anthropic

# 1. API Configuratie
# Vul hier je actieve API-sleutel in
API_KEY = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=API_KEY)

# 2. De opmaak van de webpagina
st.set_page_config(page_title="Oefenexamen Geschiedenis", page_icon="🏛️")
st.title("Oefenexamen geschiedenis")
st.markdown("Welkom bij dit oefenexamen geschiedenis. Als jij er klaar voor bent, kunnen we beginnen. Succes!")

# 3. Jouw instructies voor de AI (System Prompt)
# Kopieer hier de tekst van je cursus en de rubric tussen de juiste tags
system_prompt = f"""
Je bent een empathische, constructieve maar academisch uitdagende leerkracht geschiedenis. Je neemt een formatief mondeling oefenexamen af voor leerlingen uit het 4de jaar secundair onderwijs. 
Je doel is om de leerling via gerichte, dialogische interactie te laten oefenen in historisch redeneren. Je stelt NOOIT alle vragen tegelijk. Je wacht altijd op het antwoord van de leerling voordat je reageert of naar de volgende stap gaat.

**Jouw Kennisbasis:**
<cursus_leander>
{cursus_tekst}
</cursus_leander>

<bronvragen>
{bronnen_tekst}
</bronvragen>

<beoordelingsdocument>
{rubric_tekst}
</beoordelingsdocument>

**Het Examenverloop (Stap voor Stap):**
**STAP 1: De Introductie**
Begin een geopend gesprek meteen op de volgende manier!
"Welkom. Fijn dat je het proefexamen eventjes probeert!" Ga daarna verder met deel I.
Begroet de leerling vriendelijk. Leg kort uit dat het examen uit drie delen bestaat (begrip, centrale vraag, bron). Vraag aan de leerling of hij of zij een willekeurig thema wil herhalen of specifiek uit een bepaald deel vragen wil. WACHT OP ANTWOORD.

**STAP 2: Het Begrip (Conceptuele kennis)**
Geef het begrip (of de keuze tussen twee begrippen) uit het gekozen thema. Vraag de leerling om dit te definiëren en contextualiseren in de tijd, ruimte en het domein. WACHT OP ANTWOORD. Als het antwoord rudimentair is, stel één gerichte doorvraag. 

**STAP 3: De Centrale Vraag (Causaal Redeneren)**
Stel de centrale vraag. WACHT OP ANTWOORD. Als het antwoord te simpel is, daag hen uit om multifactorieel te redeneren (bv. "Kan je ook een sociaaleconomische factor noemen?"). 

**STAP 4: De Bron (Bronnenkritiek)**
Presenteer de historische bron. Vraag de leerling naar de standplaatsgebondenheid, betrouwbaarheid en link met de centrale vraag. WACHT OP ANTWOORD.

**STAP 5: Feedback en Evaluatie**
Bedank de leerling. Geef een heldere evaluatie op basis van de rubric (Niveau 1 t/m 4 per domein: Conceptuele kennis, Causaal redeneren, Bronnenkritiek, Historische communicatie). Geef één concrete tip.

**Toon en Stijl:**
- Gebruik toegankelijk Nederlands.
- Wees aanmoedigend maar laat hen nadenken (socratische methode).
- Geef aan dat de score indicatief is.
"""

# 4. Het geheugen van de chat instellen
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Bestaande berichten tonen (zodat de chat blijft staan na elk antwoord)
for msg in st.session_state.messages:
    # Verberg onze geheime "start"-zin voor de leerlingen
    if msg["content"] != "Start het examen volgens de instructies.":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. De Startknop
if len(st.session_state.messages) == 0:
    if st.button("Start het proefexamen"):
        start_bericht = "Start het examen volgens de instructies."
        st.session_state.messages.append({"role": "user", "content": start_bericht})
        
        with st.spinner("De leerkracht bekijkt zijn notities..."):
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620", 
                max_tokens=1000,
                system=system_prompt,
                messages=st.session_state.messages
            )
            bot_reply = response.content[0].text
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun() # Ververs de pagina om het bericht te tonen

# 7. Het invoerveld voor de leerling
if prompt := st.chat_input("Typ hier je antwoord..."):
    
    # Toon wat de leerling net typte
    with st.chat_message("user"):
        st.markdown(prompt)
        
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Laat de AI nadenken en antwoorden
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("De leerkracht luistert en denkt na..."):
            try:
                response = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                bot_reply = response.content[0].text
                message_placeholder.markdown(bot_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Er is een fout opgetreden: {e}")

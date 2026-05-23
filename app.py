import streamlit as st
import anthropic

# 1. Configuratie van de API via Streamlit Secrets
API_KEY = st.secrets["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=API_KEY)

# 2. Pagina instellingen en UI
st.set_page_config(page_title="Oefenexamen Geschiedenis", page_icon="🏛️")
st.title("Oefenexamen geschiedenis - juni 2026")
st.markdown("Welkom bij dit oefenexamen geschiedenis. Heb je grondig gestudeerd? Dan kan je deze tool gebruiken als test. Hou er rekening mee dat dit een automatische tool is die fouten kan maken. Succes!")

# 3. Functie om de tekstbestanden veilig in te lezen
# (Dit MOET boven de system_prompt staan)
def lees_tekstbestand(bestandsnaam):
    try:
        with open(bestandsnaam, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Let op: Het bestand '{bestandsnaam}' staat niet op GitHub. Voeg dit toe.")
        return ""

cursus_tekst = lees_tekstbestand("cursus.txt")
bronnen_tekst = lees_tekstbestand("bronnen.txt")
rubric_tekst = lees_tekstbestand("rubric.txt")

# 4. De System Prompt
# Let op de 'f' vlak voor de drie aanhalingstekens!
system_prompt = f"""
Je bent een empathische, constructieve maar academisch uitdagende leerkracht geschiedenis. Je neemt een formatief mondeling oefenexamen af voor leerlingen uit het 4de jaar secundair onderwijs. 
Je doel is om de leerling via gerichte, dialogische interactie te laten oefenen in historisch redeneren. Je stelt NOOIT alle vragen tegelijk. Je wacht altijd op het antwoord van de leerling voordat je reageert of naar de volgende stap gaat.

**Jouw Kennisbasis:**
Gebruik uitsluitend de 'cursus', 'de bronvragen' en het 'Beoordelingsdocument' die hieronder in deze prompt zijn opgenomen. Verzin zelf geen nieuwe historische concepten of vragen buiten dit curriculum.

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
Geef het begrip (of de keuze tussen twee begrippen) uit het gekozen thema. Vraag de leerling om dit te definiëren en te contextualiseren in de tijd, de ruimte en bij het passende domein (sociaal, economisch, cultureel of politiek). WACHT OP ANTWOORD.
*Beoordeling:* Als het antwoord rudimentair is, stel één gerichte doorvraag (scaffolding) om te kijken of ze het in het juiste historische referentiekader kunnen plaatsen. Bevestig kort het juiste antwoord en ga dan over naar stap 3.

**STAP 3: De Centrale Vraag (Causaal Redeneren)**
Stel de centrale vraag uit de set. WACHT OP ANTWOORD.
*Beoordeling:* Dit is het zwaartepunt. Leerlingen vallen vaak terug op lineaire verklaringen. Als het antwoord te simpel is, daag hen uit: "Kan je ook een sociaaleconomische / politieke factor noemen?" of "Hoe leidde dat specifieke feit tot die bredere maatschappelijke verandering?". Forceer hen om op niveau 3 of 4 van de rubric te komen (multifactorieel redeneren). Ga na een korte dialoog over naar stap 4.

**STAP 4: De Bron (Bronnenkritiek)**
Presenteer de historische bron uit de set (geef een korte beschrijving als het een grafiek of spotprent is, of citeer het relevante tekstfragment). Vraag de leerling de bron te analyseren: wat is de standplaatsgebondenheid, betrouwbaarheid, en wat vertelt dit ons in functie van de centrale vraag? WACHT OP ANTWOORD.
*Beoordeling:* Vraag gericht door naar de intenties of de vooringenomenheid van de auteur/maker. 

**STAP 5: Feedback en Evaluatie**
Zodra de drie delen zijn afgerond, bedank je de leerling. Geef een heldere, constructieve evaluatie op basis van de vier domeinen van de bijgevoegde rubric:
1. Conceptuele kennis
2. Causaal redeneren
3. Bronnenkritiek
4. Historische communicatie
Ken per domein een niveau toe (Niveau 1 t/m 4) en geef één concrete tip voor het echte examen. Sluit positief en motiverend af.

**Toon en Stijl:**
- Gebruik toegankelijk Nederlands (geschikt voor 16-jarigen in Vlaanderen).
- Wees aanmoedigend ("Goed op weg, maar bedenk ook even...").
- Speel de rol van examinator vol overtuiging; wees geen encyclopedie die het antwoord direct voorkauwt, maar laat de leerling zweten en nadenken via de socratische methode.
- geef telkens aan dat de score indicatief is en dat de werkelijke score op het examen kan afwijken!
"""

# 5. Chatgeschiedenis initialiseren
if "messages" not in st.session_state:
    st.session_state.messages = []

# 6. Bestaande berichten op het scherm tonen
for msg in st.session_state.messages:
    if msg["content"] != "Start het examen volgens de instructies.":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. Startknop (zorgt dat de bot het gesprek opent)
if len(st.session_state.messages) == 0:
    if st.button("Start het proefexamen"):
        start_bericht = "Start het examen volgens de instructies."
        st.session_state.messages.append({"role": "user", "content": start_bericht})
        
        with st.spinner("Ik bekijk even mijn notities..."):
            response = client.messages.create(
                model="claude-3-haiku-20240307", 
                max_tokens=1000,
                system=system_prompt,
                messages=st.session_state.messages
            )
            bot_reply = response.content[0].text
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            st.rerun()

# 8. Inputveld voor de leerling
if prompt := st.chat_input("Typ hier je antwoord..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Ik luister en denk na..."):
            try:
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=st.session_state.messages
                )
                bot_reply = response.content[0].text
                message_placeholder.markdown(bot_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Er ging iets mis met de verbinding: {e}")

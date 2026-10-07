import speech_recognition as sr
import os
import webbrowser
from datetime import datetime
import pyttsx3
import pyaudio
from api import ask_ai
from security import security_check

def say(text):
    print(f"JARVIS: {text}")

    try:
        engine = pyttsx3.init("sapi5")

        voices = engine.getProperty("voices")

        # Try to select a male voice
        for voice in voices:
            name = voice.name.lower()
            if "david" in name or "mark" in name or "male" in name:
                engine.setProperty("voice", voice.id)
                break

        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.say(str(text))
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("TTS ERROR:", e) 

        
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("No clear speech detected. Listening again...")
        return None
    return query

if __name__ == "__main__":

    # =========================================================
    # JARVIS SECURITY
    # =========================================================
    access_granted = security_check()

    if not access_granted:
        print("JARVIS access denied.")
        raise SystemExit

    say("Hi, I am Jarvis, your personal AI assistant. How can I help you?")

    sleeping = False

    SLEEP_COMMANDS = [
        "go to sleep",
        "sleep jarvis",
        "jarvis sleep",
        "go offline",
        "sleep"
    ]

    WAKE_COMMANDS = [
        "wake up jarvis",
        "wake jarvis",
        "hey jarvis",
        "jarvis"
    ]

    while True:
        print("Listening...")

        query = take_command()

        # No speech / speech not understood -> don't send to Groq
        if query is None:
            continue

        query = query.lower().strip()

        if not query:
            continue

        # =========================================================
        # SLEEP MODE
        # =========================================================
        if sleeping:
            if any(command in query for command in WAKE_COMMANDS):
                sleeping = False
                say("I am awake. How can I help you?")
            else:
                # Ignore everything except wake command.
                continue

            # Do not send the wake phrase itself to Groq.
            continue

        # =========================================================
        # SLEEP COMMAND
        # =========================================================
        if any(command in query for command in SLEEP_COMMANDS):
            sleeping = True
            say("Going to sleep. Say wake up Jarvis when you need me.")
            continue

        sites = [
    ["google", "https://www.google.com"],
    ["youtube", "https://www.youtube.com"],
    ["facebook", "https://www.facebook.com"],
    ["instagram", "https://www.instagram.com"],
    ["x", "https://x.com"],
    ["reddit", "https://www.reddit.com"],
    ["wikipedia", "https://www.wikipedia.org"],
    ["chatgpt", "https://chatgpt.com"],
    ["gemini", "https://gemini.google.com"],
    ["claude", "https://claude.ai"],
    ["copilot", "https://copilot.microsoft.com"],
    ["perplexity", "https://www.perplexity.ai"],
    ["deepseek", "https://chat.deepseek.com"],
    ["grok", "https://grok.com"],
    ["openai", "https://openai.com"],
    ["huggingface", "https://huggingface.co"],
    ["bing", "https://www.bing.com"],
    ["yahoo", "https://www.yahoo.com"],
    ["duckduckgo", "https://duckduckgo.com"],
    ["google maps", "https://maps.google.com"],
    ["google news", "https://news.google.com"],
    ["google translate", "https://translate.google.com"],
    ["google drive", "https://drive.google.com"],
    ["google docs", "https://docs.google.com"],
    ["google sheets", "https://sheets.google.com"],
    ["google slides", "https://slides.google.com"],
    ["google calendar", "https://calendar.google.com"],
    ["google photos", "https://photos.google.com"],
    ["google meet", "https://meet.google.com"],
    ["gmail", "https://mail.google.com"],
    ["google flights", "https://www.google.com/travel/flights"],
    ["my website", "https://codewithbhavit.bolt.host"],

    ["whatsapp", "https://web.whatsapp.com"],
    ["telegram", "https://web.telegram.org"],
    ["discord", "https://discord.com"],
    ["snapchat", "https://www.snapchat.com"],
    ["threads", "https://www.threads.com"],
    ["linkedin", "https://www.linkedin.com"],
    ["pinterest", "https://www.pinterest.com"],
    ["tumblr", "https://www.tumblr.com"],
    ["quora", "https://www.quora.com"],
    ["twitch", "https://www.twitch.tv"],

    ["netflix", "https://www.netflix.com"],
    ["prime video", "https://www.primevideo.com"],
    ["disney plus", "https://www.disneyplus.com"],
    ["crunchyroll", "https://www.crunchyroll.com"],
    ["dailymotion", "https://www.dailymotion.com"],
    ["imdb", "https://www.imdb.com"],
    ["spotify", "https://open.spotify.com"],
    ["soundcloud", "https://soundcloud.com"],
    ["apple music", "https://music.apple.com"],
    ["shazam", "https://www.shazam.com"],
    ["bandcamp", "https://bandcamp.com"],

    ["github", "https://github.com"],
    ["gitlab", "https://gitlab.com"],
    ["stackoverflow", "https://stackoverflow.com"],
    ["stack exchange", "https://stackexchange.com"],
    ["codepen", "https://codepen.io"],
    ["replit", "https://replit.com"],
    ["jsfiddle", "https://jsfiddle.net"],
    ["npm", "https://www.npmjs.com"],
    ["pypi", "https://pypi.org"],
    ["docker hub", "https://hub.docker.com"],
    ["vercel", "https://vercel.com"],
    ["netlify", "https://www.netlify.com"],
    ["heroku", "https://www.heroku.com"],
    ["firebase", "https://firebase.google.com"],
    ["aws", "https://aws.amazon.com"],
    ["azure", "https://azure.microsoft.com"],
    ["google cloud", "https://cloud.google.com"],
    ["digitalocean", "https://www.digitalocean.com"],
    ["railway", "https://railway.app"],
    ["render", "https://render.com"],
    ["glitch", "https://glitch.com"],
    ["w3schools", "https://www.w3schools.com"],
    ["mdn", "https://developer.mozilla.org"],
    ["geeksforgeeks", "https://www.geeksforgeeks.org"],
    ["freecodecamp", "https://www.freecodecamp.org"],
    ["leetcode", "https://leetcode.com"],
    ["hackerrank", "https://www.hackerrank.com"],
    ["codeforces", "https://codeforces.com"],
    ["codechef", "https://www.codechef.com"],
    ["kaggle", "https://www.kaggle.com"],
    ["exercism", "https://exercism.org"],
    ["dev.to", "https://dev.to"],
    ["hashnode", "https://hashnode.com"],
    ["product hunt", "https://www.producthunt.com"],

    ["amazon", "https://www.amazon.com"],
    ["ebay", "https://www.ebay.com"],
    ["walmart", "https://www.walmart.com"],
    ["etsy", "https://www.etsy.com"],
    ["aliexpress", "https://www.aliexpress.com"],
    ["best buy", "https://www.bestbuy.com"],
    ["ikea", "https://www.ikea.com"],
    ["target", "https://www.target.com"],
    ["flipkart", "https://www.flipkart.com"],
    ["myntra", "https://www.myntra.com"],
    ["meesho", "https://www.meesho.com"],
    ["ajio", "https://www.ajio.com"],
    ["nykaa", "https://www.nykaa.com"],
    ["snapdeal", "https://www.snapdeal.com"],
    ["croma", "https://www.croma.com"],
    ["reliance digital", "https://www.reliancedigital.in"],

    ["khan academy", "https://www.khanacademy.org"],
    ["coursera", "https://www.coursera.org"],
    ["edx", "https://www.edx.org"],
    ["udemy", "https://www.udemy.com"],
    ["quizlet", "https://quizlet.com"],
    ["duolingo", "https://www.duolingo.com"],
    ["brilliant", "https://brilliant.org"],
    ["mit opencourseware", "https://ocw.mit.edu"],
    ["stanford online", "https://online.stanford.edu"],
    ["harvard online", "https://pll.harvard.edu"],
    ["wolfram alpha", "https://www.wolframalpha.com"],
    ["desmos", "https://www.desmos.com"],
    ["symbolab", "https://www.symbolab.com"],
    ["photomath", "https://photomath.com"],
    ["ncert", "https://ncert.nic.in"],
    ["cbse", "https://www.cbse.gov.in"],
    ["diksha", "https://diksha.gov.in"],
    ["unacademy", "https://unacademy.com"],
    ["byjus", "https://byjus.com"],
    ["vedantu", "https://www.vedantu.com"],
    ["physics wallah", "https://www.pw.live"],

    ["bbc", "https://www.bbc.com"],
    ["cnn", "https://www.cnn.com"],
    ["reuters", "https://www.reuters.com"],
    ["the guardian", "https://www.theguardian.com"],
    ["new york times", "https://www.nytimes.com"],
    ["washington post", "https://www.washingtonpost.com"],
    ["the times", "https://www.thetimes.com"],
    ["the telegraph", "https://www.telegraph.co.uk"],
    ["al jazeera", "https://www.aljazeera.com"],
    ["ap news", "https://apnews.com"],
    ["times of india", "https://timesofindia.indiatimes.com"],
    ["hindustan times", "https://www.hindustantimes.com"],
    ["the hindu", "https://www.thehindu.com"],
    ["indian express", "https://indianexpress.com"],
    ["ndtv", "https://www.ndtv.com"],
    ["india today", "https://www.indiatoday.in"],
    ["news18", "https://www.news18.com"],
    ["economic times", "https://economictimes.indiatimes.com"],

    ["canva", "https://www.canva.com"],
    ["adobe", "https://www.adobe.com"],
    ["figma", "https://www.figma.com"],
    ["framer", "https://www.framer.com"],
    ["dribbble", "https://dribbble.com"],
    ["behance", "https://www.behance.net"],
    ["unsplash", "https://unsplash.com"],
    ["pexels", "https://www.pexels.com"],
    ["pixabay", "https://pixabay.com"],
    ["remove bg", "https://www.remove.bg"],
    ["photopea", "https://www.photopea.com"],
    ["ilovepdf", "https://www.ilovepdf.com"],
    ["smallpdf", "https://smallpdf.com"],
    ["tinyurl", "https://tinyurl.com"],
    ["bitly", "https://bitly.com"],
    ["grammarly", "https://www.grammarly.com"],
    ["notion", "https://www.notion.so"],
    ["evernote", "https://evernote.com"],
    ["trello", "https://trello.com"],
    ["asana", "https://asana.com"],
    ["todoist", "https://todoist.com"],
    ["slack", "https://slack.com"],
    ["zoom", "https://zoom.us"],

    ["booking", "https://www.booking.com"],
    ["airbnb", "https://www.airbnb.com"],
    ["tripadvisor", "https://www.tripadvisor.com"],
    ["expedia", "https://www.expedia.com"],
    ["makemytrip", "https://www.makemytrip.com"],
    ["goibibo", "https://www.goibibo.com"],
    ["cleartrip", "https://www.cleartrip.com"],
    ["skyscanner", "https://www.skyscanner.com"],
    ["uber", "https://www.uber.com"],
    ["ola", "https://www.olacabs.com"],

    ["weather", "https://weather.com"],
    ["accuweather", "https://www.accuweather.com"],
    ["windy", "https://www.windy.com"],
    ["time and date", "https://www.timeanddate.com"],
    ["world time buddy", "https://www.worldtimebuddy.com"],

    ["paypal", "https://www.paypal.com"],
    ["stripe", "https://stripe.com"],
    ["razorpay", "https://razorpay.com"],
    ["google pay", "https://pay.google.com"],
    ["phonepe", "https://www.phonepe.com"],
    ["paytm", "https://paytm.com"],

    ["espn", "https://www.espn.com"],
    ["cricbuzz", "https://www.cricbuzz.com"],
    ["icc", "https://www.icc-cricket.com"],
    ["fifa", "https://www.fifa.com"],
    ["nba", "https://www.nba.com"],
    ["formula 1", "https://www.formula1.com"],
    ["olympics", "https://olympics.com"],
    ["uefa", "https://www.uefa.com"],

    ["pastebin", "https://pastebin.com"],
    ["jsdelivr", "https://www.jsdelivr.com"],
    ["cdnjs", "https://cdnjs.com"],
    ["apache", "https://www.apache.org"],
    ["python", "https://www.python.org"],
    ["java", "https://www.java.com"],
    ["rust", "https://www.rust-lang.org"],
    ["go", "https://go.dev"],
    ["cplusplus", "https://isocpp.org"],

    ["internet archive", "https://archive.org"],
    ["britannica", "https://www.britannica.com"],
    ["google scholar", "https://scholar.google.com"],
    ["researchgate", "https://www.researchgate.net"],
    ["semantic scholar", "https://www.semanticscholar.org"],
    ["arxiv", "https://arxiv.org"],
    ["pubmed", "https://pubmed.ncbi.nlm.nih.gov"],

    ["virustotal", "https://www.virustotal.com"],
    ["have i been pwned", "https://haveibeenpwned.com"],
    ["speedtest", "https://www.speedtest.net"],
    ["downdetector", "https://downdetector.com"],
    ["cloudflare", "https://www.cloudflare.com"],
    ["urlscan", "https://urlscan.io"]
    ]
        website_opened = False

        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]}")
                webbrowser.open(site[1])
                website_opened = True
                break

        if website_opened:
            continue

        if "time" in query:
            strTime = datetime.now().strftime("%I:%M %p")
            say(f"The time is {strTime}")
            continue

        try:
            response = ask_ai(query)

            print(f"JARVIS: {response}")
            say(response)

        except Exception as e:
            print("AI ERROR:", e)
            say("Sorry, I could not connect to my AI brain.")

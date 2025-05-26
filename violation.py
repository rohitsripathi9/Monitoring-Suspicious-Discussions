from nltk.stem import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
from thefuzz import fuzz
import nltk

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
stemmer = PorterStemmer()

bad_words = {
    "pedophile": 5,
    "bomb": 5,
    "hate": 3,
    "kill": 5,
    "racist": 4,
    "terrorist": 5,
    "nuclear": 4,
    "weapon": 3,
    "fuck": 2,
    "assault": 4,
    "abuse": 4,
    "molest": 5,
    "rape": 5,
    "murder": 5,
    "stab": 4,
    "gun": 3,
    "shoot": 4,
    "explosive": 4,
    "hostage": 5,
    "violence": 4,
    "suicide": 5,
    "threat": 4,
    "hijack": 5,
    "extort": 4,
    "porn": 2,
    "nudity": 2,
    "sex": 2,
    "semen": 2,
    "genocide": 5,
    "lynch": 5,
    "massacre": 5,
    "slaughter": 5,
    "bloodshed": 4,
    "dictator": 3,
    "incest": 5,
    "drug": 3,
    "cocaine": 4,
    "meth": 4,
    "heroin": 4,
    "overdose": 4,
    "alcoholic": 2,
    "addict": 2,
    "junkie": 2,
    "smuggle": 3,
    "cartel": 4,
    "trafficking": 5,
    "prostitute": 3,
    "hooker": 3,
    "pimp": 3,
    "slut": 3,
    "whore": 3,
    "bitch": 3,
    "bastard": 3,
    "dumb": 2,
    "idiot": 2,
    "moron": 2,
    "retard": 4,
    "cripple": 3,
    "fag": 4,
    "faggot": 5,
    "nigger": 5,
    "negro": 4,
    "chink": 5,
    "spic": 5,
    "wetback": 5,
    "tranny": 4,
    "kike": 5,
    "gook": 5,
    "dyke": 4,
    "slant": 4,
    "raghead": 5,
    "camel": 3,
    "queer": 3,
    "shemale": 3,
    "dick": 2,
    "cock": 2,
    "boobs": 1,
    "vagina": 2,
    "penis": 2,
    "anal": 2,
    "oral": 2,
    "cum": 2,
    "orgy": 2,
    "gangbang": 3,
    "fetish": 2,
    "kinky": 1,
    "bdsm": 2,
    "threesome": 2,
    "rapeplay": 5,
    "snuff": 5,
    "necrophilia": 5,
    "zoophilia": 5,
    "bestiality": 5,
    "grooming": 4,
    "molestation": 5,
    "exploitation": 4,
    "abduction": 5,
    "execution": 5,
    "torture": 5,
    "sadism": 4,
    "psychopath": 3,
    "sociopath": 3,
    "incel": 3,
    "radical": 3,
    "extremist": 4,
    "cult": 3,
    "conspiracy": 2,
    "hatecrime": 5,
    "antisemite": 4,
    "homophobe": 4,
    "misogynist": 3,
    "xenophobe": 3,
    "violator": 4,
    "nigger": 5,
    "nigga": 5,
    "chink": 5,
    "gook": 5,
    "kike": 5,
    "spic": 5,
    "wetback": 5,
    "raghead": 5,
    "towelhead": 5,
    "coon": 5,
    "jiggaboo": 5,
    "porchmonkey": 5,
    "sambo": 5,
    "beaner": 5,
    "zipperhead": 5,
    "redskin": 5,
    "paki": 5,
    "gypsy": 4,
    "cracker": 4,
    "honky": 4,
    "whitey": 4,
    "jap": 5,
    "nips": 5,
    "dothead": 5,
    "sandnigger": 5,
    "halfbreed": 4,
    "mulatto": 4,
    "mongoloid": 5,
    "zulu": 4,
    "ape": 4,
    "squaw": 4,
    "nuclear": 3,
    "shit": 1
}

def analyze_post(text):
    text_lower = text.lower()
    words = text_lower.split()
    stemmed_bad_words = {stemmer.stem(k): v for k, v in bad_words.items()}
    viol_words = []
    violation_score = 0
    threshold = 80

    for w in words:
        stem_w = stemmer.stem(w)
        if stem_w in stemmed_bad_words:
            viol_words.append(w)
            violation_score += stemmed_bad_words[stem_w]
        else:
            for bad_stem in stemmed_bad_words:
                score = fuzz.ratio(stem_w, bad_stem)
                if score >= threshold:
                    viol_words.append(w)
                    violation_score += stemmed_bad_words[bad_stem]
                    break

    sentiment = sia.polarity_scores(text)
    sentiment_score = sentiment['compound']

    final_thought = ""
    if violation_score == 0 and sentiment_score > 0:
        final_thought = "good"
    elif violation_score <=10 and sentiment_score > -0.5:
        final_thought = "no_score"
    elif violation_score > 10 and sentiment_score > -0.5:
        final_thought = "admin"
    elif violation_score <= 10 and sentiment_score < -0.5:
        final_thought = "admin"
    else:
        final_thought="deleted"
    
    return {"final_thought":final_thought,"violation_score":violation_score,"sentiment_score":sentiment_score}

def change_score(sentiment_score,final_thought,user_score):
    if final_thought=="good":
        sentiment_score = -1*sentiment_score if sentiment_score<0 else sentiment_score
        user_score+=sentiment_score
    elif final_thought=="deleted" or final_thought == "delete":
        sentiment_score=-1*sentiment_score if sentiment_score < 0 else sentiment_score
        user_score-=sentiment_score
    if user_score>150:
        user_score=150
    return user_score
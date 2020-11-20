import streamlit as st
import lyricsgenius
import json
import operator
import re
from collections import Counter
import math


st.title("VERSE_ly_")
st.markdown("_What would you favorite artist say?_")

st.sidebar.title("About")
st.sidebar.markdown("Versely lets you interact with your favorite artists by searching thousands of lyrics to find verses that are most relevant to how you are feeling.")

st.sidebar.title("How does it work?")               
st.sidebar.markdown("It downloads lyrics from Genius from your favorite artist and runs two algorithms: (i) Jaccard Similarity, and (ii) Cosine Similarity between your input and lyrics. Then, it finds verses from these lyrics that most closely align to your input.")

st.sidebar.title("Contribute")
st.sidebar.info("This is an open source app and you're welcome to provide your awesome feedback. More information on contribution coming soon!")

genius = lyricsgenius.Genius("YXdefAF0GIJ5SHnrPnpElbh0GYaDGs-3IJz2LUWRIYrjos-9-QDPr_Z8CD-FOL-t")

artist_name = st.text_input("Select artist")


@st.cache
def download_lyrics(artist_name):
    genius = lyricsgenius.Genius("YXdefAF0GIJ5SHnrPnpElbh0GYaDGs-3IJz2LUWRIYrjos-9-QDPr_Z8CD-FOL-t")
    artist_songs = genius.search_artist(artist_name, max_songs=3)
    lyrics_data = json.loads(artist_songs.to_json(sanitize=True))
    
    return lyrics_data


# Algorithm 1
def jaccard_similarity(query, document):
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection)/len(union)

def calc_jaccard_similarity(user_input):
    
    lyrics_jaccard = {}

    for lyric in set(song_lyrics_flat_list_clean):
        jaccard = jaccard_similarity(user_input, lyric)
        lyrics_jaccard[lyric] = jaccard
    
    return_lyric = max(lyrics_jaccard.items(), key=operator.itemgetter(1))[0]
    return_cosine = max(lyrics_jaccard.items(), key=operator.itemgetter(1))[1]
    
    return return_lyric


# Algorithm 2
WORD = re.compile(r"\w+", re.IGNORECASE)

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def calc_cosine_similarity(user_input):
    vector1 = text_to_vector(user_input)

    lyrics_cosine = {}

    for lyric in set(song_lyrics_flat_list_clean):
        cosine = get_cosine(vector1, text_to_vector(lyric))
        lyrics_cosine[lyric] = cosine   
    
    return_lyric = max(lyrics_cosine.items(), key=operator.itemgetter(1))[0]
    return_cosine = max(lyrics_cosine.items(), key=operator.itemgetter(1))[1]
    
    return return_lyric


if artist_name != "":
    
    lyrics_data = download_lyrics(artist_name)
    
    st.success("Finished downloading lyrics for "+ lyrics_data['name'] + "!")
    # Create a list of all sentences from lyrics (top N songs from artist)
    song_lyrics_vocab = []  

    for song in lyrics_data['songs']:
        song_lyrics = song['lyrics']
        split_song_lyrics = [p for p in song_lyrics.split('\n') if p]
        song_lyrics_vocab.append(split_song_lyrics)

    # Convert from list of lists to list
    song_lyrics_flat_list = []
    for sublist in song_lyrics_vocab:
        for item in sublist:
            song_lyrics_flat_list.append(item)

    # Remove lines that contain "[Versus]", "[Chorus]", etc.
    song_lyrics_flat_list_clean = [x for x in song_lyrics_flat_list if "[" not in x]
    
mood = st.text_input("How are you feeling?")

run = st.button("Go")


if mood != "" and run:
    
    st.header(lyrics_data['name'] + " says:")
    st.subheader(calc_jaccard_similarity(mood))
    st.subheader(calc_cosine_similarity(mood))



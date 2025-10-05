import streamlit as st
import pandas as pd
import random #used to pick random songs from billboard100
import spotipy #used to interact with spotify API
from spotipy.oauth2 import SpotifyClientCredentials #used for spotify authentication
import streamlit.components.v1 as components #used to embed spotify player
from config import client_id, client_secret #importing from config.py

# Load data
def load_billboard_data():
    return pd.read_csv("billboard100.csv")

def load_song_data():  #loads the clustered dataset
    return pd.read_csv("df_song_list.csv")

def authenticate_spotify(client_id, client_secret): #connects to Spotify API using credentials from config.py
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)

billboard100_df = load_billboard_data()
df_song_list = load_song_data()
sp = authenticate_spotify(client_id, client_secret) #search songs on spotify

cluster_descriptions = {
    "Trap, Hip-Hop": "High-energy Trap and Hip-Hop tracks with hard hitting beats",
    "Soft Beats, Romantic": "Soft, mellow tracks featuring romantic melodies and relaxing vibes.",
    "Classical,Dreamy": "Classical and dreamy songs for relaxing moments.",
    "Lively sounds": "Lively and upbeat tracks that lift your mood.",
    "High Rhythm, Danceable Songs": "Tracks with a strong, steady beat and energetic tempo.",
    "Deep pulsating beats": "Bass-Heavy tracks with pulsating rhythms.",
    "Loud, expressive songs": "Loud and expressive songs that emphasize strong vocals or dynamic instrumentation.",
    "Miscellaneous": "A mix of songs that don’t clearly fit into other categories, eclectic in style."
}

# Streamlit UI
def recommend_trending_song_streamlit(billboard100_df, df_song_list, sp):
    st.title("🎵 Welcome to the Song Recommendation App")

    song_choice = st.radio("Do you want a trending song from Billboard 100?", ("Yes", "No"))

    if song_choice == "Yes":
        random_index = random.choice(billboard100_df.index) #picks a random song from billboard100
        song = billboard100_df.loc[random_index, "Song"] #displays the song and artist name
        artist = billboard100_df.loc[random_index, "Artist"]
        st.write(f"**{song}** by **{artist}**")
        results = sp.search(q=f"{song} {artist}", type="track", limit=1) #searches for the song on spotify 
        if results["tracks"]["items"]:
            track_id = results["tracks"]["items"][0]["id"]
            components.iframe(src=f"https://open.spotify.com/embed/track/{track_id}", width=300, height=80)

    else:
        available_labels = df_song_list["cluster_label"].unique()  #if the user selects no, they can choose a cluster from a dropdown
        choice = st.selectbox("Choose a cluster vibe:", available_labels)
        #Display cluster description
        if choice in cluster_descriptions:
            st.write(f"**Description:** {cluster_descriptions[choice]}")
        #Filter songs for that cluster and display 3 random samples
        cluster_songs = df_song_list[df_song_list["cluster_label"] == choice]
        samples = cluster_songs.sample(3)
        st.write(f"### Suggested songs from this cluster: {choice}")
        for i, (idx, row) in enumerate(samples.iterrows(), 1):    #loops through the 3 samples and displays each song's name and artist 
            song, artist = row["track_name"], row["artists"]
            st.write(f"{i}. **{song}** by **{artist}**")
            results = sp.search(q=f"{song} {artist}", type="track", limit=1) #searches spotify for the track, result is a dictionary 
            if results["tracks"]["items"]:
                track_id = results["tracks"]["items"][0]["id"] #extracts the track ID from the dictionary
                components.iframe(src=f"https://open.spotify.com/embed/track/{track_id}", width=300, height=80) #embeds the spotify player for each song

# Run the app
recommend_trending_song_streamlit(billboard100_df, df_song_list, sp)

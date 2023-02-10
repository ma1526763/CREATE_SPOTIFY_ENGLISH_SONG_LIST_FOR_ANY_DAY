import os
import requests
import spotipy
from tkinter import *
from datetime import datetime
from bs4 import BeautifulSoup
from tkinter import messagebox
from tkcalendar import Calendar
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

def create_playlist_to_spotify(sp, song_uris, user_date, playlist_name):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=f"{playlist_name}-{user_date}", public=False)
    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)


def authenticate_spotify_user():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(redirect_uri="http://example.com",
                                                     client_id=SPOTIFY_CLIENT_ID,
                                                     client_secret=SPOTIFY_CLIENT_SECRET,
                                                     cache_path="token.txt",
                                                     show_dialog=True,
                                                     scope="playlist-modify-private"))

def get_song_uris(song_list, sp, year):
    song_uris = []
    for song in song_list:
        result = sp.search(q=f"track:{song} year:{year}", type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")
    return song_uris

############## SONG TITLE LIST #############
def get_song_title_list(u_date):
    soup = BeautifulSoup(requests.get(f"https://www.billboard.com/charts/hot-100/{u_date}/").text, 'html.parser')
    return [i.text.strip() for i in soup.select('li #title-of-a-story')]


###### create playlist ######
def create_playlist():
    user_date = cal.get_date()
    if int(user_date.split("-")[0]) < 1960 or user_date > datetime.now().strftime("%Y-%m-%d"):
        return messagebox.showerror(title="Invalid date",
                                    message=f"Please select the date b/w 1960-01-01 - {datetime.now().strftime('%Y-%m-%d')}.")
    if not name_entry.get():
        return messagebox.showerror(title="Invalid Name", message="Please Enter a valid name for playlist.")
    song_title_list = get_song_title_list(user_date)
    sp = authenticate_spotify_user()
    all_valid_songs_uris = get_song_uris(song_title_list, sp, year=user_date.split('-')[0])
    create_playlist_to_spotify(sp, all_valid_songs_uris, user_date, name_entry.get())
    messagebox.showinfo(title="Successful", message=f"Playlist {name_entry.get()}-{user_date} has been created successfully")
    name_entry.delete(0, END)

################### GUI ##############
window = Tk()
window.title("Spotify List")
window.geometry("800x528+200+100")
window.resizable(False, False)
canvas = Canvas(width=800, height=528)
canvas.place(x=0, y=0)
img = PhotoImage(file="img.png")
canvas.create_image(400, 264, image=img)

# CALENDAR
cal = Calendar(window, selectmode='day', year=datetime.now().year, month=datetime.now().month,
               day=datetime.now().day, font="Arial 16", background="black", disabledbackground="black",
               bordercolor="#088a5c", headersbackground="#088a5c", normalbackground="#4cf5ca", foreground='white',
               normalforeground='#088a5c', headersforeground='white', date_pattern="yyyy-mm-dd")
cal.place(x=200, y=60)

# ENTRY
select_label = Label(text="Select date and Enter Playlist Name", foreground="#088a5c", font=("Arial", 17, "bold"))
select_label.place(x=200, y=346)
name_entry = Entry(width=30, font=("Arial", 17), highlightthickness=3, foreground="#2a5447", background="#4cf5ca",
                   highlightbackground="#062c1b", highlightcolor="#062c1b")
name_entry.place(x=200, y=390)
name_entry.focus()

# BUTTONS
add_button = Button(text="Create Playlist", background="#088a5c", foreground="white", font=("Arial", 15, "bold"),
                    command=create_playlist)
add_button.place(x=420, y=435, width=180)
window.mainloop()

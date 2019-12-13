# program to list a sonos playlist


import soco
import xlsxwriter
import time

def make_list(playlist_name="Jukebox Party"):
    #make a file
    jukebox_songs = open("JukeboxSongList.txt","w+")
    #make excel fil
    jukebox_sonos = xlsxwriter.Workbook('jukebox_sonos.xlsx')
    #add a sheet
    jukebox_list = jukebox_sonos.add_worksheet()
    '''
    insert routine to write to the excel file below.....
    '''

    letter_number = []
    #make list of letters. nb jukebox has no "i" or "o"
    letters = ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','U','V']
    numbers = [1,2,3,4,5,6,7,8,9,0]
    # make combined list of letters and numbers
    for num in numbers:
        for letter in letters:
            letter_number.append(letter + str(num))
    print(letter_number)
    print("length of letter_number: ",len(letter_number))
    # get a sonos unit
    #device = soco.discovery.by_name("Portable")
    device = soco.SoCo("192.168.1.35")
    #get the jukebox playlist
    playlist = device.get_sonos_playlist_by_attr("title", playlist_name)

    #print (playlist)
    track_list = device.music_library.browse(playlist, max_items=300)
    playlist_tracks = []
    #print(track_list)
    for index, track in enumerate(track_list):
        if track.title.find("(feat.") > -1:
            track_title = track.title[0:track.title.find("(feat.")]
        elif track.title.find(" - ") > -1:
            track_title = track.title[0:track.title.find(" - ")]

        else:
            track_title = track.title
        #print(track_title)
        # print(track.album)
        #print(track.creator)
        # make dictionary to hold track information
        playlist_item = {"number":index,"letter_number":letter_number[index],
                         "title":track_title,"artist":track.creator}
        playlist_tracks.insert(index,playlist_item)

        jukebox_songs.write(playlist_tracks[index]['title'])


    jukebox_songs.close()
    return playlist_tracks


def get_track_info(unit = "Portable"):
    device = soco.discovery.by_name(unit)
    track_info = device.get_current_track_info()
    print("track title: ",track_info["title"])
    print("track artist: ",track_info["artist"])

tracklist = make_list()
for items in tracklist:
    print(items)


#!/usr/bin/env python3
"""
Makes an xls (excel) file for an excel spreadsheet that formats labels for the wallbox pages
"""

import SonosUtils
import xlsxwriter

# page = input("Enter the RFID tag number of the pageset")
# if not len(page) == 4:
#     print("incorrect page number, using default")
#     page = "0000"

page = input("Enter pageset number:")
# get list of tracks
page_set = SonosUtils.make_pageset_tracklist(page)
page_tracks = page_set[0]["tracks"]

# make excel workbook and worksheet objects0
workbook = xlsxwriter.Workbook("wallboxlabels.xlsx")
worksheet = workbook.add_worksheet()

# set up column widths
for column in range(0, 4, 3):
    worksheet.set_column(column + 0, column + 0, 3)
    worksheet.set_column(column + 1, column + 1, 32)
    worksheet.set_column(column + 2, column + 2, 2)

# set margins
worksheet.set_margins(0, 0, 0, 0)

# set up page breaks

worksheet.set_h_pagebreaks([40, 80, 120, 160])

# make cell formats. We need a lot to do all the different colours and fancy formatting on the wallbox labels
# define tuples for common format parameters like colors and fonts
colors = ("#ccffcc", "#d9e1f2", "#c00000")
fonts = ("Franklin Gothic Demi",)

# formats for favorites and playlists.
fav_label_id_format = workbook.add_format(
    {"font_size": "8", "align": "center", "valign": "top", "bg_color": colors[0]}
)
fav_title_format = workbook.add_format(
    {
        "font_name": fonts[0],
        "font_size": "12",
        "bold": False,
        "shrink": True,
        "align": "center",
        "valign": "bottom",
        "bg_color": colors[0],
    }
)
fav_artist_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": "#ccffcc",
        "bottom": 5,
        "bottom_color": colors[2],
    }
)

fav_title_right_format = workbook.add_format({"bg_color": colors[0], "right": 5})
fav_artist_right_format = workbook.add_format(
    {"bg_color": colors[0], "right": 5, "bottom": 5, "bottom_color": colors[2]}
)

# formats for song tracks
song_label_id_format = workbook.add_format(
    {"font_size": "8", "align": "center", "valign": "top", "bg_color": colors[1]}
)
song_title_format = workbook.add_format(
    {
        "font_name": fonts[0],
        "font_size": "12",
        "bold": False,
        "shrink": True,
        "align": "center",
        "valign": "bottom",
        "bg_color": colors[1],
    }
)
song_artist_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": "#d9e1f2",
        "bottom": 5,
        "bottom_color": colors[2],
        "bold": True,
    }
)
song_title_right_format = workbook.add_format({"bg_color": colors[1], "right": 5})
song_artist_right_format = workbook.add_format(
    {"bg_color": colors[1], "right": 5, "bottom": 5, "bottom_color": colors[2]}
)

# formats to use at the bottom of a new label (set of two tracks) - just adds a thick border
song_artist_label_end_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": colors[1],
        "bottom": 5,
        "bold": True,
    }
)
song_artist_right_label_end_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": colors[1],
        "bottom": 5,
        "bold": True,
        "right": 5,
    }
)
fav_artist_label_end_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": colors[0],
        "bottom": 5,
        "bold": True,
    }
)
fav_artist_right_label_end_format = workbook.add_format(
    {
        "font_size": "10",
        "italic": "italic",
        "shrink": True,
        "align": "center",
        "valign": "top",
        "bg_color": colors[0],
        "bottom": 5,
        "bold": True,
        "right": 5,
    }
)

# make nested list of tracks & track info to simplify writing to rows in the excel spreadsheet
# tracks is the nested list
tracks = []
track_row = []
for index, track in enumerate(page_tracks):
    # there are 400 rows, two per track (title and artist).
    # build each row ( a list ), append to tracks list.
    # but, if we have more than 200 labels then exit
    if index > 199:
        break
    track_row.clear()
    track_row.append(track["letter_number"])
    # add the song title, but truncate it to fit on label
    track_row.append(track["song_title"][0:36])
    # add track type
    track_row.append(track["type"])
    # add the track row data, columns (ie, list items) 0 - 4 (in list slice the 5 is not included in the slice)
    tracks.append(track_row[0:5])
    # make a row for the artist
    track_row.clear()
    track_row.insert(2, track["artist"][0:36])
    # add it to the end of the list
    tracks.append(track_row[0:4])

# make excel file
# flag to indicate we are at the beginning of a new label (pair of tracks)
label_bottom = False
label_counter = 0
col_start = 0
for l_col in range(0, 2):
    # loop twice to make two columns of labels to save paper
    # set starting column for each of the two columns of labels
    col_start = l_col * 3
    for label_row in range(0, 200, 2):
        # adjust index for the column based on l_col
        index = label_row + (l_col * 200)
        # each label has two entries, each entry has two rows, ie title and artist
        # tracks list made above has 400 rows , title + artist on adjacent rows, total 200 selections
        # so, the for loop goes to 400, 2 at a time
        # check to see if it's a song, use song formatting, otherwise use favorite/playlist formatting
        print(
            "label: ",
            tracks[index][0],
            "track: ",
            label_counter,
            "Label No: ",
            index,
            "",
            "column: ",
            l_col,
            "track type: ",
            tracks[index][2],
            "Title",
            tracks[index][1],
            "artist: ",
            tracks[index + 1][0],
        )
        # check to see if label_counter is an odd number, means we are at the bottom of a label -each label has
        #   2 tracks (4 rows), we increment the counter each time through the for loop.
        if label_counter % 2 > 0:
            label_bottom = True
        else:
            label_bottom = False
        # set formats for song title, artist based on content type and position of track on label (top or bottom)
        if tracks[index][2] == "sonos_playlist_tracks":
            if label_bottom:
                # make extra thick line on bottom border
                artist_format = song_artist_label_end_format
                artist_right_format = song_artist_right_label_end_format
            else:
                artist_format = song_artist_format
                artist_right_format = song_artist_right_format

            label_format = song_label_id_format
            title_format = song_title_format
            title_right_format = song_title_right_format

        else:
            # set formats for favorites
            if label_bottom:
                # set formats for the bottom of the label (ie, the second track
                artist_format = fav_artist_label_end_format
                artist_right_format = fav_artist_right_label_end_format
            else:
                artist_format = fav_artist_format
                artist_right_format = fav_artist_right_format

            label_format = fav_label_id_format
            title_format = fav_title_format
            title_right_format = fav_title_right_format

        label_counter += 1

        # write to the spreadsheet with appropriate formatting as set above
        # labels have 4 columns - 0 is the selection letter+number, 1 is same thing printed on the label,
        #   2 is the title or artist, 3 is blank(just a spacer)
        # write the letter/number index in the first column - this is for reference
        # worksheet.write(index, 0, tracks[index][0])
        # set row height for the title
        worksheet.set_row(index, height=20)
        # write the title row
        worksheet.write(label_row, col_start + 0, tracks[index][0], label_format)
        worksheet.write(label_row, col_start + 1, tracks[index][1], title_format)
        worksheet.write(label_row, col_start + 2, "", title_right_format)
        # set row height for artist
        worksheet.set_row(index + 1, height=17)
        # write the artist row
        worksheet.write(label_row + 1, col_start + 0, "", artist_format)
        worksheet.write(
            label_row + 1, col_start + 1, tracks[index + 1][0], artist_format
        )
        worksheet.write(label_row + 1, col_start + 2, "", artist_right_format)

workbook.close()

print("Succesfully made label spreadsheet")

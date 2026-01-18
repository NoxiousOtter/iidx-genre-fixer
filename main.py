import sys
import taglib
import json
import glob

def find_match(db: dict, title: str, artist: str):
    lower_title = title.lower()
    lower_artist = artist.lower()

    for song in db:
        lower_db_title = song["title"].lower()
        lower_db_artist = song["artist"].lower()
        lower_db_ascii_title = song["title_ascii"].lower()

        # if lower_db_artist != lower_artist:
        #     continue

        if lower_db_title == lower_title:
            return song
        if lower_db_ascii_title == lower_title:
            return song

        # if " (" in lower_title:
        #     index = lower_title.find(" (")
        #     space_remove = lower_title[:index] + lower_title[index + 1:]
        #     if lower_db_title == space_remove:
        #         return song
        #     if lower_db_ascii_title == space_remove:
        #         return song
        #
        #     everything_remove = lower_title[:index]
        #     if lower_db_title == everything_remove:
        #         return song
        #     if lower_db_ascii_title == everything_remove:
        #         return song
        #
        # if "(" in lower_title:
        #     index = lower_title.find("(")
        #     everything_remove = lower_title[:index]
        #     if lower_db_title == everything_remove:
        #         return song
        #     if lower_db_ascii_title == everything_remove:
        #         return song

    raise FileNotFoundError

def main():
    if len(sys.argv) != 3:
        print("please supply input folder and db json")
        return

    input_folder = sys.argv[1]
    db_json = sys.argv[2]

    with open(db_json, "r") as file:
        db = json.load(file)

    flacs = glob.glob(f"{input_folder}/**/*.flac", recursive=True)

    not_found = []
    found = []
    mismatch_artist = []

    for flac in flacs:
        with taglib.File(flac) as song:
            try:
                found_match = find_match(db, song.tags["TITLE"][0], song.tags["ARTIST"][0])
                found.append(flac)

                if found_match["artist"] != song.tags["ARTIST"][0]:
                    mismatch_artist.append(f"{song.tags["ARTIST"][0]} => {found_match["artist"]}")
            except FileNotFoundError:
                not_found.append(f"{song.tags["ARTIST"][0]} - {song.tags["TITLE"][0]}")

    # print(f"found {len(found)}")
    # print(f"not found {len(not_found)}")
    #
    for a in sorted(mismatch_artist):
        print(a)


if __name__ == "__main__":
    main()

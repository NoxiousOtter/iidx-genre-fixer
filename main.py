import sys
import taglib
import json
import glob

def update_tags(taglib_file, song_db):
    taglib_file.tags["GENRE"] = song_db["genre"]
    taglib_file.tags["ARTIST"] = song_db["artist"]
    taglib_file.save()

def remove_suffixes(title: str, suffixes: list[str]):
    fixed_string = title

    for suffix in suffixes:
        if suffix in fixed_string:
            index = fixed_string.find(suffix)
            fixed_string = fixed_string[:index]
            fixed_string = fixed_string.strip()

    return fixed_string

def find_match(db: dict, title: str):
    lower_title = title.lower()

    matches = 0
    matched = None

    for song in db:
        lower_db_title = song["title"].lower()
        lower_db_ascii_title = song["title_ascii"].lower()

        if lower_db_title == lower_title:
            matches += 1
            matched = song
            continue

        if lower_db_ascii_title == lower_title:
            matches += 1
            matched = song
            continue

        if " (" in lower_title:
            index = lower_title.find(" (")
            space_remove = lower_title[:index] + lower_title[index + 1:]
            if lower_db_title == space_remove or lower_db_ascii_title == space_remove:
                matches += 1
                matched = song
                continue

        removed_suffixes = remove_suffixes(lower_title, ["-original", "- original", "(original", "-extend", "- extend", "(extend"])
        if lower_db_title == removed_suffixes or lower_db_ascii_title == removed_suffixes:
            matches += 1
            matched = song
            continue

    if matches > 1:
        # Multiple songs with the same title, we cannot automatically apply the correction
        matched = None

    return matched

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

    found_count = 0

    print("Processing...")

    print("FOUND MATCHES")

    for flac in flacs:
        with taglib.File(flac) as song:

            found_match = find_match(db, song.tags["TITLE"][0])

            if found_match:
                old_title = song.tags["TITLE"][0]
                old_artist = song.tags["ARTIST"][0]

                if "GENRE" in song.tags:
                    old_genre = song.tags["GENRE"][0]
                else:
                    old_genre = "No Genre"

                update_tags(song, found_match)

                print(f"{old_title} - {old_artist} => {found_match["artist"]}, {old_genre} => {found_match["genre"]}")
                found_count += 1
            else:
                not_found.append(flac)

    print()
    print("NEEDS MANUAL INTERVENTION")
    for file in not_found:
        print(file)

    print()
    print("COMPLETE")
    print(f"Updated: {found_count}, Unchanged: {len(not_found)}")


if __name__ == "__main__":
    main()

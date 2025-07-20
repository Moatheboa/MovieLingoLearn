subtitles = []

# opens in read-mode. No need to close() when using with:
with open("subtitles.srt", "r", encoding="utf-8") as file:
    lines_list = file.read().split("\n\n")  # Separates content at empty line, each block becomming an element in the list.

    for block in lines_list:
        parts = block.strip().split("\n") # removes \n in start and end, then separates content at line break.
        # In case the file is broken somewhere, for example missing text, so that the block doesnt have +3 indexes, we will get indexoutofbounds.
        # How ever, if we do following if-solution we need to make sure we also skip the corresponding part in the other subtitles-file.
        if (len(parts) >= 3):  # Skips parts with less than 3 indexes to avoid error when calling index 2
            text_part = parts[2:]  # Skips the first two lines and takes the rest
            text = " ".join(text_part).strip()  # For now, I joined if there are two lines.

            subtitles.append(text)

for line in subtitles:
    print(line)

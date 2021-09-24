import subprocess
import os
from pathlib import Path
import shutil
from jsonargparse import ArgumentParser, ActionConfigFile
from src.txt_to_html import tsv2html
from src.download_models import download_models
from src.utils import create_folder



def combine_books(src_file_path, tgt_file_path, name, src_lan, tgt_lan, title, author, data_folder="books", 
        chapter_regex=r"NO REGEX GIVEN", size=14, stylesheet="",
        overlaps=10, align_size=10, search_buffer=10, ebook_format="epub", keep_temp_files=False, underneath=True, russian_stresses=True):

    if src_lan == "rus" and russian_stresses:
        from src.russian_stresses import add_russian_stresses
    
    # print parameters
    for key, value in locals().items():
        print(f"{key}:\t{value}") 
    print("\n---------------\n")

    # create all folder and file names
    working_folder = f"{data_folder}/{name}"
    create_folder(working_folder)

    # copy the stylesheet into the working folder
    if stylesheet:
        stylesheet_name = Path(stylesheet).name
        shutil.copyfile(stylesheet, f'{working_folder}/{stylesheet_name}')
        stylesheet=stylesheet_name

    src_overlap = f"{working_folder}/{name}_overlaps.{src_lan}"
    tgt_overlap = f"{working_folder}/{name}_overlaps.{tgt_lan}"

    src_emb = src_overlap+".emb"
    tgt_emb = tgt_overlap+".emb"

    align_file = f"{working_folder}/{name}.aligns"

    aligned_sents = f"{working_folder}/{name}.txt"
    html_file = f"{working_folder}/{name}.html"
    ebook_file = f"{working_folder}/{name}.{ebook_format}"

    # create all commands to run vecalign and laser
    commands = [
        # cmd_overlap_src
        ["python", "./vecalign/overlap.py",
         "-i", src_file_path,  "-o", src_overlap, "-n", str(overlaps)],
        # cmd_overlap_tgt
        ["python", "./vecalign/overlap.py",
         "-i", tgt_file_path,  "-o", tgt_overlap, "-n", str(overlaps)],

        # cmd_emb_src
        ["./laser/tasks/embed/embed.sh",
         src_overlap, src_lan, src_emb],
        # cmd_emb_tgt
        ["./laser/tasks/embed/embed.sh",
         tgt_overlap, tgt_lan, tgt_emb]]

    cmd_align = ["python", "./vecalign/vecalign.py", "-v", "--alignment_max_size", str(align_size), "--search_buffer_size", str(search_buffer),
                 "--src", src_file_path, "--tgt", tgt_file_path, "--src_embed", src_overlap, src_emb,
                 "--tgt_embed", tgt_overlap, tgt_emb]

    my_env = os.environ.copy()
    my_env["LASER"] = "./laser"

    # download laser models if missing
    download_models()

    # run commands to create sentence overlaps with vecalign/overlap.py and get embeddings for them from LASER laser/tasks/embed/embed.sh
    for command in commands:
        print(" ".join(command), "\n")
        subprocess.check_call(command, env=my_env)

    # run the vecalign.py to get alignment file
    print(" ".join(cmd_align), "\n")
    subprocess.check_call(cmd_align, stdout=open(align_file, 'w'), env=my_env)

    # add russian stresses
    if src_lan == "ru":
        src_file_path = add_russian_stresses(src_file_path, new_path=f"{working_folder}/{name}_st_em_a.ru")

    # use the resulting alignment file to create aligned sentence document
    out_str = ""
    with open(src_file_path, 'r') as src_text, open(tgt_file_path, 'r') as tgt_text, open(align_file, 'r') as align, open(aligned_sents, 'w') as outfile:
        for line in align:
            for i, txt_file in enumerate([src_text, tgt_text]):
                out_str += " ".join([txt_file.readline().strip().replace("\t", "")
                                     for _ in eval(line.split(":")[i])])
                out_str += "\t" if i % 2 == 0 else "\n"
        out_str = out_str.strip()
        outfile.write(out_str)
    open(html_file, "w").write(
        tsv2html(out_str, stylesheet, chapter_regex=chapter_regex, size=int(size)))

    # convert HTML to ebook using Calibre
    cmd_ebook = ["ebook-convert", html_file, ebook_file,
                 "--authors", author, "--title", title, "--flow-size", "10000000"]
    if underneath:
        print("DO UNDERNEATH - ADD LINEARIZE TABLES")
        print(type(underneath), underneath)
        cmd_ebook.append("--linearize-tables")
    print(" ".join(cmd_ebook), "\n")    
    subprocess.check_call(cmd_ebook, env=my_env)

    # delete temporary files
    if not keep_temp_files:
        files = [src_overlap, tgt_overlap, src_emb, tgt_emb, align_file, aligned_sents, html_file]
        if stylesheet:
            files.append(f'{working_folder}/{stylesheet_name}')
        for file in files:
            os.remove(file)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-c', '--conf-file', action=ActionConfigFile,
               help='Config file')
    parser.add_argument('-s', '--src_file_path', required=True, help='Book in source language')
    parser.add_argument('-t', '--tgt_file_path', required=True, help='Book in target language')
    parser.add_argument('-n', '--name', required=True, help='Short name for folder/files')
    parser.add_argument('-d', '--data_folder', required=False, help='Folder for input and output', default="books")
    parser.add_argument('-i', '--src_lan', required=True, help='Source language')
    parser.add_argument('-o', '--tgt_lan', required=True, help='Target language')
    parser.add_argument('-b', '--title', required=True, help='Book title')
    parser.add_argument('-a', '--author', required=True, help='Book author')
    parser.add_argument('-r', '--chapter_regex', required=True, help='Regex to detect a new chapter')
    parser.add_argument('-z', '--size', required=False, help='Font size', default=14)
    parser.add_argument('-y', '--stylesheet', required=False, help='Path to stylesheet', default="")
    parser.add_argument('-v', '--overlaps', required=False, help='Overlaps setting in vecalign', default=10)
    parser.add_argument('-l', '--align_size', required=False, help='Align setting in Laser', default=10)
    parser.add_argument('-e', '--search_buffer', required=False, help='Search buffer setting in Laser', default=10)
    parser.add_argument('-f', '--ebook_format', required=False, help='File format of the output ebook', default="epub")
    parser.add_argument('-x', '--keep_temp_files', required=False, help='Whether to keep the temporary files afterwards', type=bool, default=False)
    parser.add_argument('-u', '--underneath', required=False, help='Translations appear underneath instead of side by side', type=bool, default=True)
    parser.add_argument('-w', '--russian_stresses', required=False, help='Add stresses to Russian text if it is source (requires udar)', type=bool, default=True)

    options = parser.parse_args()

    combine_books(src_file_path=options.src_file_path, tgt_file_path=options.tgt_file_path, name=options.name, src_lan=options.src_lan,
        tgt_lan=options.tgt_lan, title=options.title, author=options.author, data_folder=options.data_folder, chapter_regex=options.chapter_regex,
        size=options.size, stylesheet=options.stylesheet, overlaps=options.overlaps, align_size=options.align_size, search_buffer=options.search_buffer,
        ebook_format=options.ebook_format, keep_temp_files=options.keep_temp_files, underneath=options.underneath, russian_stresses=options.russian_stresses)

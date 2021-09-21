from re import search
import subprocess
import os
from pathlib import Path
import configargparse
from txt_to_html import hun2html
from download_models import download_models


def create_folder(folder):
    path = Path(folder)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Folder is already there - {folder}")
    else:
        print(f"Folder was created at {folder}")


def add_russian_stresses(src_file_path, working_folder, name, src_lan):
    import udar
    from tqdm import tqdm

    out_str = ""
    in_str = open(src_file_path, "r").read()
    for line in tqdm(in_str.split("\n")):
        line = udar.Document(line).stressed()
        line = line.replace(" ,", ",").replace("« ", "«").replace(
            " »", "»").replace("< ", "<").replace(" >", ">").replace(
            "( ", "(").replace(" )", ")")
        out_str += f"{line}\n"

    src_file_path = f"{working_folder}/{name}_st_em_a.{src_lan}"
    open(src_file_path, "w").write(out_str)

    return src_file_path



def combine_books(src_file_path, tgt_file_path, name, src_lan, tgt_lan, title, author, data_folder="books", chapter_regex=r"NO REGEX GIVEN", size=14, stylesheet="lrstyle.css",
         overlaps=10, align_size=10, search_buffer=10, ebook_format="epub", keep_temp_files=False):

    # create all folder and file names
    working_folder = f"{data_folder}/{name}"
    create_folder(working_folder)

    src_overlap = f"{working_folder}/{name}_overlaps.{src_lan}"
    tgt_overlap = f"{working_folder}/{name}_overlaps.{tgt_lan}"

    src_emb = src_overlap+".emb"
    tgt_emb = tgt_overlap+".emb"

    align_file = f"{working_folder}/{name}.aligns"

    aligned_sents = f"{working_folder}/{name}.txt"
    html_file = f"{working_folder}/{name}.html"
    ebook_file = f"{working_folder}/{name}.{ebook_format}"

    #
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
        src_file_path = add_russian_stresses(src_file_path, working_folder, name, src_lan)

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
        hun2html(out_str, stylesheet, chapter_regex=chapter_regex))

    # convert HTML to ebook using Calibre
    cmd_ebook = ["ebook-convert", html_file, ebook_file,
                 "--linearize-tables", "--authors", author, "--title", title]
    subprocess.check_call(cmd_ebook, env=my_env)

    # delete temporary files
    if not keep_temp_files:
        for file in [src_overlap, tgt_overlap, src_emb, tgt_emb, align_file, aligned_sents, html_file]:
            os.remove(file)


if __name__ == '__main__':

    parser = configargparse.ArgParser()
    parser.add('-c', '--conf-file', is_config_file=True,
               help='Config file')
    parser.add('-s', '--src_file_path', required=True, help='Book in source language')
    parser.add('-t', '--tgt_file_path', required=True, help='Book in target language')
    parser.add('-n', '--name', required=True, help='Short name for folder/files')
    parser.add('-d', '--data_folder', required=False, help='Folder for input and output', default="books")
    parser.add('-i', '--src_lan', required=True, help='Source language')
    parser.add('-o', '--tgt_lan', required=True, help='Target language')
    parser.add('-b', '--title', required=True, help='Book title')
    parser.add('-a', '--author', required=True, help='Book author')
    parser.add('-r', '--chapter_regex', required=True, help='Regex to detect a new chapter')
    parser.add('-z', '--size', required=False, help='Font size', default=14)
    parser.add('-y', '--stylesheet', required=False, help='Book author', default="lrstyle.css")
    parser.add('-v', '--overlaps', required=False, help='Overlaps setting in vecalign', default=10)
    parser.add('-l', '--align_size', required=False, help='Align setting in Laser', default=10)
    parser.add('-e', '--search_buffer', required=False, help='Search buffer setting in Laser', default=10)
    parser.add('-f', '--ebook_format', required=False, help='File format of the output ebook', default="epub")
    parser.add('-x', '--keep_temp_files', required=False, help='Whether to keep the temporary files afterwards', default=False)

    options = parser.parse_args()

    print("----------")
    print(parser.format_values())

    combine_books(src_file_path=options.src_file_path, tgt_file_path=options.tgt_file_path, name=options.name, src_lan=options.src_lan,
        tgt_lan=options.tgt_lan, title=options.title, author=options.author, data_folder=options.data_folder, chapter_regex=options.chapter_regex,
        size=options.size, stylesheet=options.stylesheet, overlaps=options.overlaps, align_size=options.align_size, search_buffer=options.search_buffer,
        ebook_format=options.ebook_format, keep_temp_files=options.keep_temp_files)

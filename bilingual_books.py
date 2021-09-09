import subprocess
import os
from pathlib import Path
from txt_to_html import hun2html


def create_folder(data_folder, name):
    working_folder = Path(data_folder).absolute() / name

    # create folder where all the files are located
    path = Path(working_folder)
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print(f"Folder is already there - {working_folder}")
    else:
        print(f"Folder was created at {working_folder}")

    return working_folder


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



def main(src_file_path, tgt_file_path, data_folder, name, src_lan, tgt_lan, title, author, chapter_regex=r"NO REGEX GIVEN", size=14, stylesheet=None,
         overlaps="10", align_size="10", search_buffer="10", ebook_format="mobi"):

    # create all folder and file names
    working_folder = create_folder(data_folder, name)
    stylesheet = f"{Path().absolute()}/lrstyle.css" if not stylesheet else stylesheet

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
         "-i", src_file_path,  "-o", src_overlap, "-n", overlaps],
        # cmd_overlap_tgt
        ["python", "./vecalign/overlap.py",
         "-i", tgt_file_path,  "-o", tgt_overlap, "-n", overlaps],

        # cmd_emb_src
        ["./laser/tasks/embed/embed.sh",
         src_overlap, src_lan, src_emb],
        # cmd_emb_tgt
        ["./laser/tasks/embed/embed.sh",
         tgt_overlap, tgt_lan, tgt_emb]]

    cmd_align = ["python", "./vecalign/vecalign.py", "-v", "--alignment_max_size", align_size, "--search_buffer_size", search_buffer,
                 "--src", src_file_path, "--tgt", tgt_file_path, "--src_embed", src_overlap, src_emb,
                 "--tgt_embed", tgt_overlap, tgt_emb]

    my_env = os.environ.copy()
    my_env["LASER"] = "./laser"

    # run commands to create sentence overlaps with vecalign/overlap.py and get embeddings for them from LASER laser/tasks/embed/embed.sh
    for command in commands:
        print(" ".join(command), "\n")
        subprocess.check_call(command, env=my_env)

    # run the vecalign.py to get alignment file
    print(" ".join(cmd_align), "\n")
    subprocess.check_call(cmd_align, stdout=open(align_file, 'w'), env=my_env)

    # add russian stresses
    if src_lan == "ru":
        add_russian_stresses(src_file_path, working_folder, name, src_lan)

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

    # convert HTML to ebook
    cmd_ebook = ["ebook-convert", html_file, ebook_file,
                 "--linearize-tables", "--authors", author, "--title", title]
    subprocess.check_call(cmd_ebook, env=my_env)


if __name__ == '__main__':
    name = 'hp7'

    book_titles = {
        'hp1': ('Гарри Поттер и Философский Камень', "Book 1 - The Philosopher's Stone"),
        'hp2': ('Гарри Поттер и Тайная Комната', 'Book 2 - The Chamber of Secrets'),
        'hp3': ('Гарри Поттер и Узник Азкабана', 'Book 3 - The Prisoner of Azkaban'),
        'hp4': ('Гарри Поттер и Кубок Огня', 'Book 4 - The Goblet of Fire'),
        'hp5': ('Гарри Поттер и Орден Феникса', 'Book 5 - The Order of the Phoenix'),
        'hp6': ('Гарри Поттер и Принц-Полукровка', 'Book 6 - The Half Blood Prince'),
        'hp7': ('Гарри Поттер и Дары Смерти', 'Book 7 - The Deathly Hallows')
    }
    title, _ = book_titles[name]
    params = dict(src_file_path=f"./data/books/{name}/{name}_st.ru",
                  tgt_file_path=f"./data/books/{name}/{name}_st.en",
                  data_folder="data/books", name=name, src_lan="ru", tgt_lan="en",
                  title=title, author="J. K. Rowling",
                  chapter_regex=r"Глав.*\d\.", size=14, stylesheet=None,
                  ebook_format="epub")
    print(params)
    main(**params)

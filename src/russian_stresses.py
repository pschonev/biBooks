import argparse
try:
    import udar
    from tqdm import tqdm
except ImportError as e:
    raise ImportError("To add Russian stresses, install udar using \"pip install udar\"") from e


def add_russian_stresses(src_file_path, new_path):
    out_str = ""
    in_str = open(src_file_path, "r").read()
    for line in tqdm(in_str.split("\n")):
        line = udar.Document(line).stressed()
        line = line.replace(" ,", ",").replace("« ", "«").replace(
            " »", "»").replace("< ", "<").replace(" >", ">").replace(
            "( ", "(").replace(" )", ")")
        out_str += f"{line}\n"

    src_file_path = new_path
    open(src_file_path, "w").write(out_str)

    return src_file_path
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="Text file as input")
    parser.add_argument("target_file", help="New output location")
    args = parser.parse_args()

    add_russian_stresses(args.source_file, args.target_file)

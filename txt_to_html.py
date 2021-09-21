import regex as re
from pathlib import Path


def html_header(stylesheet=""):
    meta = '<meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\">'
    style = f'<link rel="stylesheet" href={stylesheet} type="text/css">'
    return f'<html><head>{meta}\n{style}\n</head><body>'


def html_footer():
    return "</body></html>"


def paragraph_header(chapter_title, size):
    chapter_expanded = chapter_title.split("\t")
    th = '<th class="lr2th"></th>'
    return f"""
            <h1 class=chapter>{chapter_expanded[0]}</h1>\n<hr class="lrhr">\n<table class="lrtext">{th}{th}\n
            <tr><td></td>\n
            <td><i><span style="color:gray; font-size: {0.0625*size}em;">{chapter_expanded[1]}</span></i></td></tr>\n
            """


def paragraph_footer():
    return "</table>"


def split_tsvline(hunline, index):
    expanded = hunline.split("\t")
    if len(expanded) != 3 and len(expanded) != 2:
        raise ValueError(
            f"Unexpected line format\n {index}\t{hunline} - {len(expanded)} columns found")
    return expanded


def tsv2html_line(line, size, index):
    expanded = split_tsvline(line, index)
    lrclass = "lraltline" if index % 2 else ""
    # now, is it a content line or just a matching blank?
    # content:
    if expanded[0].strip() or expanded[1].strip():
        htmlized_line = f"""
            <tr class={lrclass}><td>{expanded[0]}</td>\n
            <td><i><span style="color:gray; font-size: {0.0625*size}em;">{expanded[1]}</span></i></td></tr>\n
            """
    else:  # blank line -- this codepath can't be hit if called via tsv2html_bar
        htmlized_line = ""
    #print >> sys.stderr, index, htmlized_line
    return htmlized_line


def tsv2html_bar(paragraph, size, chapter_regex):
    if not paragraph.strip():
        return ''
    lines = paragraph.strip('\n').split('\n')
    par_text = []
    for index, line in enumerate(lines):
        if index == 0:
            par_text.append(paragraph_header(line, size))
        elif re.search(chapter_regex, line) and index > 0:
            par_text.append(paragraph_footer())
            par_text.append(paragraph_header(line, size))
        else:
            par_text.append(tsv2html_line(line, size, index))
    par_text.append(paragraph_footer())
    return ''.join(par_text)


def tsv2html(contents, stylesheet, size=14, chapter_regex=r"NO REGEX GIVEN"):
    text = [html_header(stylesheet)]
    text.append(tsv2html_bar(contents, size, chapter_regex))
    text.append(html_footer())
    return '\n'.join(text)


if __name__ == '__main__':
    import sys
    if not sys.argv[1:]:
        print(f"Use: {sys.argv[0]} infile outfile")
        sys.exit(1)
    contents = open(sys.argv[1], "r").read()
    out_str = tsv2html(contents=contents, stylesheet="")
    open(sys.argv[2], "w").write(out_str)

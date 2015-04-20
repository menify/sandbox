import os
import re
import sys
import fnmatch


# ==============================================================================


def to_sequence(value, _seq_types=(str, bytes, bytearray)):

    if not isinstance(value, _seq_types):
        try:
            iter(value)
            return value
        except TypeError:
            pass

        if value is None:
            return tuple()

    return value,

# ==============================================================================


def _null_match(name):
    return False

# ==============================================================================


def _masks_to_match(masks):
    if not masks:
        return _null_match

    if isinstance(masks, str):
        masks = masks.split('|')

    re_list = []
    for mask in to_sequence(masks):
        re_list.append(
            "(%s)" % fnmatch.translate(os.path.normcase(mask).strip()))

    re_str = '|'.join(re_list)

    return re.compile(re_str).match

# ==============================================================================


def find_files(paths=".",
               mask=("*", ),
               exclude_mask=tuple(),
               exclude_subdir_mask=('__*', '.*')):

    found_files = []

    match_mask = _masks_to_match(mask)
    match_exclude_mask = _masks_to_match(exclude_mask)
    match_exclude_subdir_mask = _masks_to_match(exclude_subdir_mask)

    for path in to_sequence(paths):
        for root, folders, files in os.walk(os.path.abspath(path)):
            for file_name in files:
                file_name_nocase = os.path.normcase(file_name)
                if (not match_exclude_mask(file_name_nocase)) and \
                   match_mask(file_name_nocase):

                    found_files.append(os.path.join(root, file_name))

            folders[:] = (folder for folder in folders
                          if not match_exclude_subdir_mask(folder))

    found_files.sort()
    return found_files

# ==============================================================================


def _replace_handler(match,
                     _camel_re=re.compile(r'([A-Z])', re.MULTILINE)):

    name = match.group(1)
    if name.find('assert') != -1:
        return name

    return _camel_re.sub(r'_\1', name).lower()

# ==============================================================================


def convert_file(file_path,
                 _camel_re=re.compile(r'([^a-zA-Z0-9]+[a-z]+[A-Za-z]+)',
                                      re.MULTILINE)):

    with open(file_path, "r+") as f:
        content = f.read()
        content = _camel_re.sub(_replace_handler, content)
        f.seek(0)
        f.write(content)


# ==============================================================================

def convert_files(paths):

    files = find_files(paths, "*.py", "_*")

    for file_path in files:
        convert_file(file_path)


# ==============================================================================

if __name__ == '__main__':
    convert_files(sys.argv[1:])

# -*- coding: utf-8 -*-

import sys
import os
from collections import defaultdict
import errno
import filecmp

min_size = 300 * 1024  # 300KB
look_in_paths = []
same_dir = False
files_map = {}
dups = []
no_dups = []


verbose_flag = False

def vprint(s: str):
    if verbose_flag:
        print(s)

def size_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'Ti']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, '', suffix)


inner_dups_file = open("inner_dups_file.txt", "w")


class find_dup:
    def __init__(self):
        pass


class FileData:
    def __init__(self, entry: os.DirEntry):
        self.path = entry.path
        self.name = entry.name
        self.size = entry.stat(follow_symlinks=False).st_size


class Folder:
    def __init__(self, path, scan_type, min_size=0):
        if not os.path.isdir(path):
            raise NotADirectoryError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        self.path = path
        self.scan_type = scan_type
        self.map = defaultdict(list)
        self.min_size = min_size
        vprint("collecting for %s" % self.path)
        self._fill_map(path)
        vprint("collected %d keys" % len(self.map))

    def _fill_map(self, cur_path):
        for entry in os.scandir(cur_path):
            try:
                if entry.is_dir(follow_symlinks=False):
                    self._fill_map(entry.path)
                else:
                    # counter += 1
                    # if not counter % 100:
                    #     print('.', end="")
                    self._add_file_to_map(entry)
            except PermissionError:
                pass

    def _add_file_to_map(self, entry: os.DirEntry):
        if entry.stat(follow_symlinks=False).st_size < self.min_size:
            return
        new_key = self._make_key_from_entry(entry)
        self.map[new_key].append(self._make_value_from_entry(entry))

    def _make_key_from_entry(self, entry: os.DirEntry):
        if True:
            new_key = "{}".format(entry.stat(follow_symlinks=False).st_size)
        else:
            new_key = "{}_{}".format(entry.stat(follow_symlinks=False).st_size, entry.name)
        return new_key

    def _make_value_from_entry(self, entry: os.DirEntry):
        return entry

    def print_dups(self):
        for key, ent_list in sorted(self.map.items(), key=lambda kv: int(kv[0]), reverse=True):
            bucket = self.combine_results(ent_list)
            size = ent_list[0].stat(follow_symlinks=False).st_size
            for b in bucket:
                if len (b) > 1:  # If only 1 item, we didnt find a duplicate
                    ent_str = ";".join(["%s" % ent.path for ent in b])
                    print('%s: %s' % (size_fmt(size), ent_str))

    def combine_results(self, ent_list):
        bucket = [[ent_list[0]]]
        for ent in ent_list[1:]:
            for num, b in enumerate(bucket):
                #TODO: add shallow by user flag, and maybe other types of combining similar
                if filecmp.cmp(b[0], ent, shallow=False):
                    bucket[num].append(ent)
                else:
                    bucket.append([ent])
        return bucket


def main():
    global verbose_flag
    verbose_flag = True
    f = Folder('d:/Jenny LG G4/Jenny LG G4/', 'type', 100)
    print(
        "\n*******************************************************************\nDuplicated files:\n*******************************************************************")
    f.print_dups()
    print("DONE!")


if __name__ == "__main__":
    main()

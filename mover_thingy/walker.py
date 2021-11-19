# -*- coding: utf-8 -*-
"""
All the real work takes place in this module.
"""

import logging
import multiprocessing as mp
import os
import shutil
import traceback
from datetime import datetime

from PIL import Image

_current_proc = mp.current_process()
_log_filename = datetime.now().strftime("%Y-%m-%d.%H%M%S")
if _current_proc:
    _log_filename = "%s-%s" % (_log_filename, _current_proc.pid)
_log_filename = "%s.log" % _log_filename
logger = logging.getLogger(__name__)
logging.basicConfig(filename=_log_filename, level=logging.INFO)


class DirectoryWalker(object):

    def __init__(self, source_dir, dest_dir, dimensions, exclude_exts=None):
        self._source_dir = source_dir
        self._dest_dir = dest_dir
        try:
            try:
                width, height = map(int, dimensions.lower().split("x"))
            except AttributeError:
                width, height = map(int, dimensions)
        except Exception as ex:
            raise ValueError("Expected dimensions to be an iterable of 2 "
                             "integers or a string of the "
                             "format 'WIDTHxHEIGHT'") from ex
        self._width = width
        self._height = height
        if not exclude_exts:
            exclude_exts = []
        try:
            exclude_exts = exclude_exts.lower()  # is this a string?
            exclude_exts = exclude_exts.split(",")  # then convert it into a list
        except AttributeError:
            # is it iterable?
            try:
                exclude_exts = [e.lower() for e in exclude_exts]
            except TypeError:
                raise ValueError("extensions was expected to be a string or "
                                 "list of strings") from TypeError

        self._exclude_exts = exclude_exts

    def go(self):
        with mp.Pool() as pool:
            it = pool.imap_unordered(self._copy_file, self._walk_paths(), 20)
            for i in it:
                print(i)
            pool.close()
            pool.join()
        logger.info("========== All done! ==========")

    def _filter_extension(self, filename):
        """
        True if this filename should be allowed. False if the extension for
        this filename is in the exclusion list.

        :param filename: a filename to check the extension of
        :type filename: str
        :return: True if the extension is NOT in the exclude_exts list
        :rtype: bool
        """
        if not self._exclude_exts:
            return True  # we're accepting everything

        filename_lower = filename.lower()

        for ext in self._exclude_exts:
            if filename_lower.endswith(ext):
                logger.info("Skipping %s because it matched "
                            "extensions", filename)
                return False

        return True

    def _copy_file(self, filepath):
        try:
            return copy_file(filepath, self._source_dir, self._dest_dir,
                             self._width, self._height)
        except Exception as ex:
            stack_trace = traceback.format_exc()
            logger.error(stack_trace)
            return stack_trace

    def _walk_paths(self):
        for folder, subfolders, filenames in os.walk(self._source_dir):
            for filename in filenames:
                if not self._filter_extension(filename):
                    continue
                yield os.path.join(folder, filename)


def get_dimensions(filepath):
    image = Image.open(filepath)
    """:type: PIL.ImageFile.ImageFile"""
    try:
        width, height = image.size
        return width, height
    finally:
        image.close()


def copy_file(filepath, source_dir, dest_dir, min_width, min_height):
    width, height = get_dimensions(filepath)
    if width < min_width and height < min_height:
        # image is too small
        return "%s was too small" % filepath

    relative_path = filepath[len(source_dir) + 1:]
    dest_filepath = os.path.join(dest_dir, relative_path)
    dirname = os.path.dirname(dest_filepath)
    os.makedirs(dirname, exist_ok=True)
    shutil.copy2(filepath, dest_filepath, follow_symlinks=False)

    return "%s |...copied to...| %s" % (filepath, dest_filepath)

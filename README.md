# Image Mover Thingy

## A one-off image COPIER based on dimensions and extensions

Despite the name, this COPIES things, it doesn't move them.

### Usage

Copy files from `source_dir` to `dest_dir` recursively, preserving the tree
structure from the source.

Images that are **less than** 2048 pixels wide **or less than** 1024 pixels tall
will be skipped. Images that have a width **greater than or equal** to 2048 
**and** a height **greater than or equal to** 1024 will be copied. Any files 
that end in `.webp`, `.dwg`, or `.html` _will be excluded_.

```sh
move_things.py source_dir dest_dir 2048x1024 .webp,.dwg,.html
```

### Why?

Because I needed to run a Photoshop batch but it kept failing on `.webp` files
and also the watermark wasn't worth it on any images smaller than 2048x2048. So
I made this to filter out a big directory of images and subfolders to a new
less-big directory of images and subfolders sans the ones I didn't care about.

### Implementation Notes

* Uses [`shutil.copy2()`][shutilcopy] to do the actual copying. It says it
  doesn't preserve all metadata, but it seemed to get it all to me. The
  modification time was preserved at least so that's something.
* Uses [`multiprocessing.Pool`][pool] to speed things up and creates one log
  file for the master process plus each child process. The number of processes
  is equal to the number of CPU cores you have. The **log files are created in
  whatever your current directory is** so hopefully it's writeable.

[pool]: <https://docs.python.org/library/multiprocessing.html#multiprocessing.pool.Pool>

[shutilcopy]: <https://docs.python.org/library/shutil.html>

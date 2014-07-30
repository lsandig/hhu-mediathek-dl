hhu-mediathek-dl
================

About
-----

This program allows you to download or stream lecture videos from
[http://mediathek.hhu.de](http://mediathek.hhu.de) of Heinrich-Heine
Universität Düsseldorf.

This is useful if you

- want to watch it later without internet connection
- are on a system with no *adobe flash player* available

Dependencies
------------

1. python >= 3.0
2. mplayer (optional, for streaming)

Usage
-----

To **download** a lecture video (let's say [this
one](http://mediathek.hhu.de/watch/c19993bc-8a64-4ba9-bdce-96a84b0ba4cc))
in medium quality and mp4 format:

    $ ./hhu-mediathek-dl -d -q medium -f mp4 http://mediathek.hhu.de/watch/c19993bc-8a64-4ba9-bdce-96a84b0ba4cc

Note that if no output filename is supplied, the program will try to
make an educated guess to use a sensible one.

To **stream** the same video directly, run

    $ ./hhu-mediathek-dl -s -q medium -f mp4 http://mediathek.hhu.de/watch/c19993bc-8a64-4ba9-bdce-96a84b0ba4cc

Note that the options **-d** and **-s** are mutually exclusive right now.

For more options run:

    $ ./hhu-mediathek-dl --help

License
-------

GNU GPL v3, see LICENSE in the same directory as this README

Homepage
--------

[GitHub](https://github.com/lsandig/hhu-mediathek-dl)

Author
------

Copyright (c) 2014 Ludger Sandig

[Blog](http://lsandig.org/blog)

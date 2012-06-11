[bookmaker][]
=============

A simple script to monitor and auto-convert eBooks.



INSTALL
-------

The `ebook-convert` utility (provided by [calibre][]) must be available in the
`$PATH` of the user, or specified with the relevant option at runtime.

This program is meant to run continuously, which is probably best accomplished
by way of [supervisord][].



REQUIREMENTS
------------

* Python 2.7
* [calibre][]
* packages from `requirements.txt`, to be installed via [pip][]



AUTHORS
-------

Originally coded by [alexandru totolici][] and hosted on [github][bookmaker].



COPYING
-------

Please refer to the include `LICENSE` file for information on what you can do
with this code.

(c) alexandru totolici



[bookmaker]: https://github.com/xorbyte/bookmaker/
[calibre]: http://calibre-ebook.com/
[pip]: http://pypi.python.org/pypi/pip
[supervisord]: http://supervisord.org/
[alexandru totolici]: http://alexandrutotolici.com

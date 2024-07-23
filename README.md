# objdictgen
objdictgen from https://github.com/ljessendk/CanFestival, it have to use python2 to start the UI. So I try to adapt it to use Python3, still on going, so don't use it currently.


Main python file is objdictedit.py

My setting is:
- Python: 3.11.9
- WxPython: 4.2.1

Adaption work:
1. Syntax modification, py2->py3, like print, try..except, etc..
3. lib gnosis, need replacement, this is used to serialize/de-serialize, big work..
4. WxPython, old->new, some api has changed / missing, need modification


Update:
Now load/save works, build dic to .c/h files have some problem, still need debugging.

Old code use gnosis to load/dump, now replace with pickle, but not compatible with old style generated file.


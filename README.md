# objdictgen
objdictgen from https://github.com/ljessendk/CanFestival, old code have to use python2 to start the UI, so I try to adapt it to use Python3, now it finally works, you can try it :)


Main python file is objdictedit.py, must know that this project is only objdictgen, have not test with CANFestival.

My setting is:
- Python: 3.11.9
- WxPython: 4.2.1

Note: For domain type var, default buffer size is 128 bytes, at GetValidTypeInfos() in gen_cfile.py


Adaption work:
1. Syntax modification, py2->py3, like print, try..except, etc..
3. lib gnosis, use pickle to replace, this is used to serialize/de-serialize, big work..
4. WxPython, old->new, some api has changed / missing, need modification


Note: Old code use gnosis to load/dump, now replace with pickle, but not compatible with old style generated file.


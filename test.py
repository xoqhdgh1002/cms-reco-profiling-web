#!/usr/bin/python3
import sys

import codecs

sys.stdout=codecs.getwriter("utf-8")(sys.stdout.detach())

print("content-type: text/html; charset=utf-8\n")
print("Hello World!")

import artist
import random

symbols = r" .:,-/()%#@{}[]$€!?_;\|'*+^~=&<>"
letters = r" qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM"
numbers = r" 1234567890"
# basic = [(r, g, b) for r in (0, 255) for g in (0, 255) for b in (0, 255)]
black = [(0, 0, 0)]

artist.generate_ascii("ascii-art-starting.jpg", symbols+letters+numbers,
                      color_pool=black, out_file="ascii-art-example.jpg")


import re

regex = r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|.*\.astromeric\.pages\.dev|astromeric\.pages\.dev)(:\d+)?"
origin = "https://8554ee90.astromeric.pages.dev"

if re.fullmatch(regex, origin):
    print("Match!")
else:
    print("No match")

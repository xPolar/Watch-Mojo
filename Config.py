# IMPORTANT
# Whenever you edit the Config file you must do a full restart of the bot (This also applies if you edit the main file)
# IMPORTANT

# Imports
import pymongo

# Discord Bot
# Bot's token (DON'T SHARE WITH ANYONE ELSE!) (To find your token go to https://discordapp.com/developers/appli~cations/ > Your Bot's Application > Bot (Turn the application into a bot if you haven't already) > Token)
TOKEN = "NzM5Mzg2MzgwMzgzNDIwNDQ3.XyZtOg.xkZXTEyxwoJOdSOvwEGfp_F4LQU"
# Bot's prefix
PREFIX = "?"
# Owner IDS (People who have access to restart the bot)
OWNER_IDS = [619284841187246090]
# Main Color (Replace the part after 0x with a hex code)
MAINCOLOR = 0x009ACA
# Error Color (Replace the part after the 0x with a hex code)
ERRORCOLOR = 0xFF2B2B

# MongoDB
# Cluster (Replace the <password> of your uri part with your password and remove the "<>")
CLUSTER = pymongo.MongoClient("mongodb+srv://watchmojo:WmpbTab4M6k3fPQM@watch-mojo.cppbg.mongodb.net/<dbname>?retryWrites=true&w=majority")

# YouTUbe
API_KEY = "AIzaSyBHcfTRcjmGpDUjDghrGV8f4nE6xd8ieuQ"
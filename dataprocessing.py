'''
Data processing on serverside
'''

def postprocess(jsondata):
    if "light_collected" in jsondata.keys():
        if jsondata["light_collected"]:
            jsondata["raw_light"] = jsondata["light"]
            if jsondata["source"] == "wood_panda":
                jsondata["light"] = 1.0-jsondata["light"]

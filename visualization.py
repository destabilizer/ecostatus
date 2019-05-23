from yattag import Doc

def generate_page(datatypes, lastdata, devices):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            doc.asis('<link rel="stylesheet" type="text/css" href="static/style.css">')
            #doc.asis('<script src="static/jquery.js"></script>')
            #doc.asis('<script src="static/smoothie.js"></script>')
            doc.asis('<script src="static/visualization.js"></script>')
            with tag('title'):
                text("EcoStatus visualization")
        with tag('body'):
            with tag('div', id='body'):
                with tag('div', id='devices_block'):
                    for d in devices:
                        with tag('h4', id='device_name_'+d):
                            text(d)
                for dt in datatypes:
                    with tag('p'):
                        with tag('h2'):
                            text(dt)
                        with tag('canvas', id=dt, width="720", height="150"):
                            pass
                with tag('p'):
                    with tag('h2'): text("Current")
                    for d in devices:
                        with tag('h4'): text(d)
                        with tag('b'): text(str(lastdata["current"][d]))
                        with tag('br'): pass
                    with tag('h2'): text("Database")
                    for d in devices:
                        with tag('h4'): text(d)
                        with tag('b'): text(str(lastdata["db"][d]))
                        with tag('br'): pass
    return doc.getvalue()

from yattag import Doc

def generate_page(datatypes, lastdata, devices):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text("EcoStatus visualization")
        with tag('body'):
            doc.asis('<script src="static/smoothie.js"></script>')
            doc.asis('<script src="static/visualization.js"></script>')
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
            for dt in datatypes:
                with tag('p'):
                    with tag('h2'):
                        text(dt)
                    with tag('canvas', id=dt, width="600", height="150"):
                        pass
    return doc.getvalue()

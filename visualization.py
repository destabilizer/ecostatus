from yattag import Doc

def generate_page(datatypes):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text("EcoStatus visualization")
        with tag('body'):
            doc.asis('<script src="bundle.js"></script>')
            for dt in datatypes:
                with tag('p'):
                    with tag('h2'):
                        text(dt)
                    with tag('canvas', id=dt, width="600", height="150"):
                        pass
    return doc.getvalue()

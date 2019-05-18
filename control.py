from yattag import Doc

def generate_page(control_status):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text('EcoStatus Control')
        with tag('body'):
            doc.asis('<script src="static/control.js"></script>')
            with tag('p'):
                with tag('h2'):
                    text("Registered devices")
                for d in control_status["registered_devices"]:
                    vis_status = "(visible)" if d in control_status["visible_devices"] else "(invisible)"
                    text(d + " " + vis_status)
                    with tag('br'): pass
                with tag('form', action="/api/control", method="post"):
                    #with tag('input', name="action", value="register_device"): pass
                    with tag('input', type="text", name="source"): pass
                    with tag('input', type="checkbox", checked="visible"): pass
                    with tag('button', type="submit"): text("Register")
            with tag('p'):
                with tag('h2'):
                    text('Database')
                db_status = control_status["is_db_writing_enabled"]
                db_text = "DB is writing" if db_status  else "DB is NOT writing"
                db_button = "Disable DB" if db_status else "Enable DB"
                with tag('h4'): text(db_text)
                with tag('button'): text(db_button)
                with tag('h4'):
                    text('Current database: ')
                    text(control_status["current_database"])
                with tag('form', action="/api/control", method="post"):
                    with tag('input', type="text", name="database_name"): pass
                    with tag('button', type="submit"): text("Create database")
                with tag('form', action="/api/control", method="post"):
                    with tag('button', type="submit"): text("Create database with timestamp")
    return doc.getvalue()

from yattag import Doc

def generate_page(control_status):
    doc, tag, text = Doc().tagtext()
    with tag('html'):
        with tag('head'):
            #doc.asis('<script src="static/control.js"></script>')
            doc.asis('<link rel="stylesheet" type="text/css" href="static/style.css">')
            with tag('title'):
                text('EcoStatus Control')
        with tag('body'):
            with tag('div', id='body'):
                with tag('p'):
                    with tag('h2'):
                        text("Registered devices")
                    for d in control_status["registered_devices"]:
                        vis_status = "(visible)" if d in control_status["visible_devices"] else "(invisible)"
                        text(d + " " + vis_status)
                        with tag('br'): pass
                    with tag('form', action="/api/control/register_device", method="post"):
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
                    with tag('form', method="get",
                             action="/api/control/" + ("disable" if db_status else "enable") + "_db_writing"):
                        with tag('button', type="submit"): text(db_button)
                    with tag('h4'):
                        text('Current database: ')
                        text(control_status["current_database"])
                    with tag('form', action="/api/control/new_database", method="post"):
                        with tag('input', type="text", name="database_name"): pass
                        with tag('button', type="submit"): text("Create database")
                    with tag('form', action="/api/control/new_database_with_timestamp", method="get"):
                        with tag('button', type="submit"): text("Create database with timestamp")
    return doc.getvalue()

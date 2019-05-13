from server import initserver

def main():
    serv = initserver()
    serv.initDataStack()
    serv.datastack().newSource("lattepanda1")
    serv.datastack().newSource("testclient")
    serv.database().create_with_timestamp()
    serv.serve_forever()



if __name__ == "__main__":
    main()

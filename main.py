from server import initserver

def main():
    serv = initserver()
    serv.initDataStack()
    serv.createDB()
    serv.datastack().newSource("test")
    serv.serve_forever()



if __name__ == "__main__":
    main()

from server import initserver

def main():
    serv = initserver()
    serv.enable_db_writing()
    serv.run()

if __name__ == "__main__":
    main()


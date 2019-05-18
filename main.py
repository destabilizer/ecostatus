from server import initserver

def main():
    serv = initserver()
    serv.enable_db_writing()
    serv.register_device({"source":"wood_panda", "visible": True})
    serv.register_device({"source":"iron_panda", "visible": True})
    serv.run()

if __name__ == "__main__":
    main()


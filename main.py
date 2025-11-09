import handler as h
import file
saved_data = []
class Main:
    def __init__(self):
        ##здесь будет главный модуль
        print("startmodule status: ok")
        #f.File.save_data(self, h.handler()) ##определение позиции машин
        #print(data)

        saved_data = file.read_data()
        data = h.handler()
        print("saved_data: " + str(saved_data))
        print("data: " + str(data))
        h.comparison(saved_data,data)
        print()
        print("фывфы")
if __name__ == "__main__":
    Main()


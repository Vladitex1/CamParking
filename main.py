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
        print(saved_data)
        print(data)
        #h.comparison(saved_data,data)
        #print()
#[уй
if __name__ == "__main__":
    Main()


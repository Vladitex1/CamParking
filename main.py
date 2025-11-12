import handler as h
import file
saved_data = []
class Main:
    def __init__(self):
        ##здесь будет главный модуль
        #print("startmodule status: ok")
        #file.save_data(self, h.handler()) ##определение позиции машин
        #print("123123фывыввввв",file.read_data())
        #data = file.read_data()
        saved_data,path = file.read_data("saves/test.mask")
        #print("хуй")
        detected_car_data = h.handler("test6.jpg")
        #print("app_saved_data: " + str(saved_data))
        #print("detected_car_data: " + str(detected_car_data))
        h.comparison(saved_data,detected_car_data)

if __name__ == "__main__":
    Main()


import ast
pos = []
text_data = []
real_data = []

def save_data(data,filename = "saves/saved_data.txt"):
    open(filename, 'w').close()
    with open(filename, "a") as file:
        #for car in data:
            #temp_data = car['position']
            #text_data.append(temp_data)
            #print(temp_data)
        file.write(str(data))

# чтение файла файл
def read_data(filename = "saves/saved_data.txt"):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        result = ast.literal_eval(content)
    return result


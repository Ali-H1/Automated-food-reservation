from apiCall import call_food
from parseFoodData import xmlToJson

def get_foods():
    response = (call_food("a"))
    print(response)
    json1 = xmlToJson(response)
    f = open('data.json', 'w', encoding='utf-8')
    f.write((json1))
    f.close()


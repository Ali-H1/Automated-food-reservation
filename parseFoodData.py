import xmltodict
import json


def parse_data(data):
    f = open('parsed_data.txt', 'w', encoding='utf-8')
    data = json.loads(data)
    # data = data["ArrayOfDietMenu"]["DietMenu"]
    dayId={'شنبه':2,'یکشنبه':5,'دوشنبه':8,'سه شنبه':11,'چهارشنبه':14}
    parsed_list = []
    for day in data:
        food = dict()
        food["Date"] = day["Meals"] [1][ "Date"]
        food["MealId"] = 2
        if len(day["Meals"] [1] ["FoodMenu"])==2:
            food["FoodName"] = day["Meals"] [1] ["FoodMenu"][0][ "FoodName"] if day["Meals"] [1] ["FoodMenu"][0]["SelfMenu"][0][ "Price"] > day["Meals"] [1] ["FoodMenu"][1]["SelfMenu"][0][ "Price"] else day["Meals"] [1] ["FoodMenu"][1][ "FoodName"]
            food["FoodId"] = day["Meals"] [1] ["FoodMenu"][0][ "FoodId"] if day["Meals"] [1] ["FoodMenu"][0]["SelfMenu"][0][ "Price"] > day["Meals"] [1] ["FoodMenu"][1]["SelfMenu"][0][ "Price"] else day["Meals"] [1] ["FoodMenu"][1][ "FoodId"]
        else:
            food["FoodName"] = day["Meals"] [1] ["FoodMenu"][0][ "FoodName"]
            food["FoodId"] = day["Meals"] [1] ["FoodMenu"][0][ "FoodId"]
        food["SelfId"] = 1
        food["LastCounts"] = 0
        food["Counts"] = 1
        if len(day["Meals"] [1] ["FoodMenu"])==2:
            food["Price"] = day["Meals"] [1] ["FoodMenu"][0]["SelfMenu"][0][ "Price"] if day["Meals"] [1] ["FoodMenu"][0]["SelfMenu"][0][ "Price"] > day["Meals"] [1] ["FoodMenu"][1]["SelfMenu"][0][ "Price"] else day["Meals"] [1] ["FoodMenu"][1]["SelfMenu"][0][ "Price"]
        else:
            food["Price"] = day["Meals"] [1] ["FoodMenu"][0]["SelfMenu"][0][ "Price"]
        food["SobsidPrice"] = 0
        food["PriceType"] = 2
        food["State"] = 0
        food["Type"] = 1
        food["OP"] = 1
        food["OpCategory"] = 1
        food["Provider"] = 1
        food["Saved"] = 0
        food["MealName"] = "ناهار"
        food["DayName"] = day["DayTitle"]
        food["SelfName"] = "مرکزی"
        food["DayIndex"] = day["DayId"]
        food["MealIndex"] = 1
        food['Id'] = dayId[food["DayName"]]
        if len(day["Meals"] [1] ["FoodMenu"])==2:
            food["Row"] = 3 if day["Meals"] [1] ["FoodMenu"][0][ "FoodName"] == food['FoodName'] else 2
        else:
            food["Row"] = 2
        parsed_list.append(food)
        json_data = json.dumps([food], ensure_ascii=False)
        f.write((json_data))
        f.write(",\n")

        if food["DayName"]=="چهارشنبه":
            break

    f.close()
    return parsed_list

def xmlToJson(xml):
    data_dict = xmltodict.parse(xml)
    print(data_dict)
    json_data = json.dumps(data_dict, ensure_ascii=False)
    parse_data(data_dict)
    return json_data


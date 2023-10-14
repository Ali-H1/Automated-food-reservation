import xmltodict
import json


def parse_data(data):
    f = open('parsed_data.txt', 'w', encoding='utf-8')
    data = data["ArrayOfDietMenu"]["DietMenu"]
    dayId = {'شنبه': 2, 'یکشنبه': 5, 'دوشنبه': 8,
             'سه شنبه': 11, 'چهارشنبه': 14}
    parsed_list = []
    for day in data:
        food = dict()
        food["Date"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:Date"]
        food["MealId"] = 2
        if len(day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]) == 2:
            food["FoodName"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:FoodName"] if day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:SelfMenu"]["d3p1:SelfMenu"][
                "d3p1:Price"] > day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"] else day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:FoodName"]
            food["FoodId"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:FoodId"] if day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:SelfMenu"]["d3p1:SelfMenu"][
                "d3p1:Price"] > day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"] else day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:FoodId"]
        else:
            food["FoodName"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]["d3p1:FoodName"]
            food["FoodId"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]["d3p1:FoodId"]
        food["SelfId"] = 1
        food["LastCounts"] = 0
        food["Counts"] = 1
        if len(day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]) == 2:
            food["Price"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"] if day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:SelfMenu"]["d3p1:SelfMenu"][
                "d3p1:Price"] > day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"] else day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][1]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"]
        else:
            food["Price"] = day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]["d3p1:SelfMenu"]["d3p1:SelfMenu"]["d3p1:Price"]
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
        if len(day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"]) == 2:
            food["Row"] = 3 if day["Meals"]["d3p1:MealMenu"][1]["d3p1:FoodMenu"]["d3p1:FoodMenu"][0]["d3p1:FoodName"] == food['FoodName'] else 2
        else:
            food["Row"] = 2
        parsed_list.append(food)
        json_data = json.dumps([food], ensure_ascii=False)
        f.write((json_data))
        f.write(",\n")

        if food["DayName"] == "چهارشنبه":
            break

    f.close()


def xmlToJson(xml):
    data_dict = xmltodict.parse(xml)
    print(data_dict)
    json_data = json.dumps(data_dict, ensure_ascii=False)
    parse_data(data_dict)
    return json_data

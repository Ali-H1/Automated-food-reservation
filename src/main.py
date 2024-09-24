from api import ShahedFoodApi, parse_reservation, to_json
from json import dumps, loads
from utils import write_file, write_file_bin


if __name__ == "__main__":
    """
    usage 
    """
    sfa = ShahedFoodApi()

    (login_data, capcha_binary) = sfa.login_before_captcha()

    sfa.login_after_captcha(
        login_data,
        "992164012", "@123456789",
        0)

    # print(sfa.credit())
    # # print(sfa.available_banks(), "banks")
    # # print(sfa.personal_info(), "personal")
    # print(sfa.financial_info(2), "finacial")
    weekProgram = sfa.getFood(1)
#     "Date": "1403/07/04",
#     "MealId": 2,
#     "FoodName": "چلو کباب کوبیده گوشت",
#     "FoodId": 45,
#     "SelfId": 1,
#     "LastCounts": 0,
#     "Counts": 1,
#     "Price": 150000,
#     "SobsidPrice": 0,
#     "PriceType": 2,
#     "State": 0,
#     "Type": 1,
#     "OP": 1,
#     "OpCategory": 1,
#     "Provider": 1,
#     "Saved": 0,
#     "MealName": "ناهار",
#     "DayName": "چهارشنبه",
#     "SelfName": "مرکزی",
#     "DayIndex": 4,
#     "MealIndex": 1,
#     "Id": 14,
#     "Row": 2
#   })
    write_file_bin("./temp/data1.json", dumps(weekProgram, ensure_ascii=False).encode("utf-8"))
    # write_file_bin("./temp/data2.json",
    #            dumps((weekProgram), ensure_ascii=False).encode("utf-8").replace('"',""))
    # print(loads(weekProgram)[0]["StateCode"])
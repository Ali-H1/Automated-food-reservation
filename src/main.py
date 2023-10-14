from api import ShahedFoodApi
from utils import write_file_bin
from parseFoodData import xmlToJson


def get_foods():
    response = (call_food("a"))
    print(response)
    json1 = xmlToJson(response)
    f = open('data.json', 'w', encoding='utf-8')
    f.write((json1))
    f.close()


if __name__ == "__main__":
    """
    usage 
    """
    sfa = ShahedFoodApi()

    (login_data, capcha_binary) = sfa.loginBeforeCaptcha()
    write_file_bin("../temp/capcha.png", capcha_binary)

    sfa.loginAfterCaptcha(
        login_data,
        "992164012", "@123456789",
        input("read capcha: "))

    print(sfa.credit())

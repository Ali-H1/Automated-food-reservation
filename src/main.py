from api import ShahedFoodApi, parse_reservation
from json import dumps
from utils import write_file, write_file_bin


if __name__ == "__main__":
    """
    usage 
    """
    sfa = ShahedFoodApi()

    (login_data, capcha_binary) = sfa.login_before_captcha()
    write_file_bin("./temp/capcha.png", capcha_binary)

    sfa.login_after_captcha(
        login_data,
        "992164012", "@123456789",
        input("read capcha: "))

    print(sfa.credit())
    weekProgram = sfa.reservation()
    write_file("./temp/data1.json", dumps(weekProgram, ensure_ascii=False))
    write_file("./temp/data2.json",
               dumps(parse_reservation(weekProgram), ensure_ascii=False))

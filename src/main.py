from api import ShahedFoodApi
from json import dumps
from utils import write_file, write_file_bin


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
    weekProgram = sfa.reservation()
    write_file("../temp/data1.json", dumps(weekProgram, ensure_ascii=False))

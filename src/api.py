from requests import Session as HttpSession
from random import randint
import json
from bs4 import BeautifulSoup
from parseFoodData import parse_data

baseUrl = "https://food.shahed.ac.ir"
apiv0 = baseUrl + "/api/v0"

foods = {
    "ماکارونی": "🍝",  # Spaghetti
    "مرغ": "🍗",            # Chicken
    "کره": "🧈",            # Butter
    "ماهی": "🐟",          # Fish
    "برنج": "🍚",          # Rice
    "پلو": "🍚",            # Rice
    "میگو": "🦐",          # Shrimp
    "خورشت": "🍛",        # Stew
    "کوکو": "🧆",          # koo koooooo
    "کتلت": "🥮",          # cutlet
    "زیره": "🍘",          # Caraway
    "رشته": "🍜",          # str
    "کباب": "🥓",          # Kebab
    "ماهیچه": "🥩",      # Muscle
    "مرگ": "💀",            # Death
    "خالی": "🍽️",       # Nothing
    "گوجه": "🍅",          # Tomamto
    "سوپ": "🥣",            # Soup
    "قارچ": "🍄",          # Mushroom
    "کرفس": "🥬",          # Leafy Green
    "بادمجان": "🍆",    # Eggplant
    "هویج": "🥕",          # Carrot
    "پیاز": "🧅",          # Onion
    "سیب زمینی": "🥔",  # Potato
    "سیر": "🧄",            # Garlic
    "لیمو": "🍋",          # Lemon
    "آلو": "🫐",            # Plum
    "زیتون": "🫒",        # Olive

    "دوغ": "🥛",            # Dough
    "ماست": "⚪",           # Yogurt
    "دلستر": "🍺",        # Beer
    "سالاد": "🥗",        # Salad
    "نمک": "🧂",            # Salt
    "یخ": "🧊",              # Ice
}


# ----- working with data objects -----


def entity_to_utf8(entity: str):
    return entity.replace("&quot;", '"')


def extractLoginPageData(htmlPage: str) -> dict:
    headSig = b"{&quot;loginUrl&quot"
    tailSig = b",&quot;custom&quot;:null}"
    s = htmlPage.find(headSig)
    e = htmlPage.find(tailSig)
    content = htmlPage[s:e + len(tailSig)]
    bbbb = entity_to_utf8(str(content)[2:-1])
    return json.loads(bbbb)


def extractLoginUrl(loginPageData: dict) -> str:
    return baseUrl + loginPageData["loginUrl"]


def extractLoginXsrfToken(loginPageData: dict) -> str:
    return loginPageData["antiForgery"]["value"]


def loginForm(user, passw, captcha, token: str):
    return {
        "username": user,
        "password": passw,
        "Captcha": captcha,
        "idsrv.xsrf": token}


def cleanLoginCaptcha(binary: str) -> str:
    jpegTail = b"\xff\xd9"
    i = binary.find(jpegTail)
    return binary[0:i+2]


def genRedirectTransactionForm(data: dict):
    # Code: <StatusCode>,
    # Result: <Msg>,
    # Action: <RedirectUrl>,
    # ActionType: <HttpMethod>,
    # Tokenitems: Array[FormInput]
    # {"Name": "...", "Value": "..."}

    # buildHtml tdiv:
    #     form(
    #         id="X",
    #         action=getstr data["Action"],
    #       `method`=getstr data["ActionType"]
    #     ):
    #         for token in data["Tokenitems"]:
    #             input(
    #                 name=getstr token["Name"],
    #                 value=getstr token["Value"])

    #     script:
    #         verbatim "document.getElementById('X').submit()"

    return "<html></html>"


def freshCaptchaUrl() -> str:
    return f"{apiv0}/Captcha?id=" + str(randint(1, 10000))

def to_json(response) -> dict:
    return json.loads(response.content)

class ShahedFoodApi:
    def __init__(self) -> None:
        self.currentSession = HttpSession()
        self.signedIn = False
        
    def login_before_captcha(self):
        """
        returns tuple of [login_data: dict, captcha_binary: bstr]
        """
        resp = self.currentSession.get(baseUrl)
        assert resp.status_code in range(200, 300)

        a = extractLoginPageData(resp.content)

        r = self.currentSession.get(
            freshCaptchaUrl(),
            headers={"Referer": resp.url}
        ).content

        b = cleanLoginCaptcha(r)

        return (a, b)

    def login_after_captcha(self,
                          loginPageData: dict,
                          uname, passw, capcha: str):

        resp = self.currentSession.post(
            extractLoginUrl(loginPageData),
            data=loginForm(
                uname, passw, capcha,
                extractLoginXsrfToken(loginPageData)
            ))

        assert resp.status_code in range(200, 300)

        html = BeautifulSoup(resp.text, "html.parser")
        form = html.find("form")
        url = form["action"]
        inputs = [(el["name"], el["value"]) for el in form.find_all("input")]

        if url.startswith("{{"):
            raise "login failed"
        else:
            resp = self.currentSession.post(url, data=inputs)
            assert resp.status_code in range(200, 300)
            self.signedIn = True

    def credit(self) -> int:
        """
        returns the credit in Rials
        """
        return to_json(self.c.get(f"{apiv0}/Credit"))
    
    def getFood(self):
        api_url = f"{apiv0}/Reservation?lastdate=&navigation=0"
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        response = self.currentSession.get(api_url)
        return parse_data(response.content.decode('utf8').replace("'", '"'))
    
    def reserveFood(self,food):
        api_url = f"{apiv0}/Reservation"
        headers = {
            "Host":"food.shahed.ac.ir",
            "Accept":"application/json, text/plain, */*",
            "Accept-Language":"en-US,en;q=0.5",
            "Accept-Encoding":"gzip, deflate, br",
            "Content-Type":"application/json;charset=utf-8",
            "Origin": "https://food.shahed.ac.ir",
            "Connection":"keep-alive",
            "Referer":"https://food.shahed.ac.ir/",
            "Sec-Fetch-Dest":"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site":"same-origin"
            }
        response = self.currentSession.post(api_url,data=f"{[food]}".encode('utf-8'),headers=headers)
        return response.content


    def is_captcha_enabled(self) -> bool:
        return to_json(self.c.get(f"{apiv0}/Captcha?isactive=wehavecaptcha"))

    def personal_info(self) -> dict:
        return to_json(self.c.get(f"{apiv0}/Student"))

    def personal_notifs(self) -> dict:
        return to_json(self.c.get(
            f"{apiv0}/PersonalNotification?postname=LastNotifications"))

    def instant_sale(self) -> dict:
        return to_json(self.c.get(f"{apiv0}/InstantSale"))

    def available_banks(self) -> dict:
        return to_json(self.c.get(f"{apiv0}/Chargecard"))

    def financial_info(self, state=1) -> dict:
        """
        state:
            all = 1
            last = 2
        """
        return to_json(self.c.get(f"{apiv0}/ReservationFinancial?state={state}"))

    def reservation(self, week: int = 0) -> dict:
        return to_json(self.c.get(f"{apiv0}/Reservation?lastdate=&navigation={week*7}"))

    def register_invoice(self, bid, amount: int) -> dict:
        return to_json(self.c.get(f"{apiv0}/Chargecard?IpgBankId={bid}&amount={amount}"))

    def prepare_bank_transaction(self, invoiceId: int, amount: int) -> dict:
        return to_json(self.c.post(f"{apiv0}/Chargecard", data={
            "amount": amount,
            "Applicant": "web",
            "invoicenumber": invoiceId}))



if __name__ == "__main__":
    """
    usage 
    """
    sfa = ShahedFoodApi()
    days = [2,3]
    (login_data, capcha_binary) = sfa.loginBeforeCaptcha()
    #write_file_bin("c.png", capcha_binary)
    print(sfa.getCredit())
    foodlist  = sfa.getFood()
    for day in days:
        print(sfa.reserveFood(foodlist[day]))


def parse_reservation(week_program) -> list:
    result = []
    for day_program in week_program:
        p = {
            # "DayId": day_program["DayId"],
            # "DayName": day_program["DayName"],
            # "GDate": day_program["MiladiDayDate"],
            # "JDate": day_program["DayDate"],
            "date": day_program["DayDate"],
            "foods": [],
        }

        for meal in day_program["Meals"]:
            for food in meal["FoodMenu"]:
                p["foods"].append({
                    "id": food["FoodId"],
                    "name": food["FoodName"],
                    "state": food["FoodState"],
                    "price": food["SelfMenu"][0]["ShowPrice"],
                })

        result.append(p)
    return result


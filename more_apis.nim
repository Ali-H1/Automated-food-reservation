type
  FinancialInfoState* = enum
    fisAll = 1
    fisLast = 2

# --- json API

staticAPI isCaptchaEnabled, bool, "/Captcha?isactive=wehavecaptcha"
staticAPI personalInfo, JsonNode, "/Student"
staticAPI credit, Rial, "/Credit"
staticAPI personalNotifs, JsonNode, "/PersonalNotification?postname=LastNotifications"
staticAPI instantSale, JsonNode, "/InstantSale"
staticAPI availableBanks, JsonNode, "/Chargecard"

staticAPI financialInfo(state: FinancialInfoState), JsonNode:
  fmt"/ReservationFinancial?state={state.int}"

staticAPI reservation(week: int), JsonNode:
  fmt"/Reservation?lastdate=&navigation={week*7}"

staticAPI registerInvoice(bid: int, amount: Rial), JsonNode:
  fmt"/Chargecard?IpgBankId={bid}&amount={amount.int}"

proc prepareBankTransaction*(c: var CustomHttpClient,
    invoiceId: int,
    amount: Rial
): JsonNode =

  let data = %* {
      "amount": $amount.int,
      "Applicant": "web",
      "invoicenumber": invoiceId}

  c.request(
    apiv0 & "/Chargecard", HttpPost,
    $data,
    content = cJson,
    accept = cJson
  ).body.parseJson

# --- login API

proc loginBeforeCaptcha*(c: var CustomHttpClient
  ): tuple[loginPageData: JsonNode, captchaBinary: string] =

  let resp = c.request(baseUrl, HttpGet)
  assert resp.code.is2xx
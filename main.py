import urequests  # HTTPリクエスト
import ujson  
import network  
import utime  # 時間制御
import machine  # ハードウェア制御
import ssd1306  # OLEDディスプレイ制御
from misakifont import MisakiFont  # 美咲フォント

# 大阪の天気JSONデータのURL
url = "https://weather.tsukumijima.net/api/forecast/city/270000"

# Wi-Fiネットワークに接続するための設定
ssid = '自宅wi-fiのSSIDを入力してください'  # Wi-FiのSSID
password = 'パスワードを入力してください'  # Wi-Fiのパスワード
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wi-Fi接続のための待機処理
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    utime.sleep(1)

# Wi-Fi接続が失敗していたらエラーを投げる
if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()

# 天気情報APIへのリクエストを送信し、レスポンスを取得
response = urequests.get(url)

# レスポンスのステータスコードをチェックし、JSONデータを解析
if response.status_code == 200:
    json_data = ujson.loads(response.text)
    forecasts = json_data["forecasts"]
    today_forecast = forecasts[0]
    telop = today_forecast["telop"]
    # 最高気温
    max_temperature = today_forecast["temperature"]["max"]["celsius"]
    # 12時から18時までの降水確率
    chance_of_rain = today_forecast["chanceOfRain"]["T12_18"]
    if telop == "曇り":
        telop = "くもり"
response.close()

# 天気情報を変数に格納
today_weather = telop
max_temp = max_temperature
cor = chance_of_rain

# 美咲フォントでディスプレイに文字を表示する関数
def show_bitmap(oled, fd, x, y, color, size):
    for row in range(0, 7):
        for col in range(0, 7):
            if (0x80 >> col) & fd[row]:
                oled.fill_rect(int(x + col * size), int(y + row * size), size, size, color)
    oled.show()

# OLEDディスプレイの設定
sda = machine.Pin(0)
scl = machine.Pin(1)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
mf = MisakiFont()

# ボタン入力のチェック
btn_pin = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_DOWN)
prev_button_state = False

# ボタンが押されたときの処理
def check_button():
    global prev_button_state, today_weather, max_temp, cor
    curr_button_state = btn_pin.value()
    if curr_button_state == 1 and not prev_button_state:  
        # Chatbotに挨拶する
        prompt = "あなたは一流のスタイリストです。天気:" + today_weather + "最高気温:" + max_temp + "降水確率:" + cor + "の天気に適した、２０代男性におすすめのコーディネートを３０字以内で教えて。気温や天気は不要です。漢字を使わず、ひらがなやカタカナで答えて"
        print('User: ' + prompt)
        oled.fill(0)
        display_text = "天気: " + today_weather + "  最高気温: " + max_temp + "度  降水確率 (12時から18時): " + cor + " " 
        x = 0
        y = 0
        color = 1
        size = 1
        for char in display_text:
            font_data = mf.font(ord(char))
            show_bitmap(oled, font_data, x, y, color, size)
            x += 8 * size
            if x >= 128:
                x = 0
                y += 8 * size
            if y >= 64:
                y = 0
            utime.sleep(0.02)
        flag = True
        prev_button_state = curr_button_state

# ボタンチェックをループで実行
while True:
    check_button()
    utime.sleep(1)

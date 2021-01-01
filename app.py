from flask import Flask, request, abort, render_template, redirect
import random
import sqlite3
import datetime as dt
import secrets as se
import re
import requests
 
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, MessageTemplateAction,
    TemplateSendMessage, ConfirmTemplate, PostbackTemplateAction,
    StickerMessage, StickerSendMessage, ButtonsTemplate,
    PostbackAction, MessageAction, URIAction
)
import os
 
app = Flask(__name__)
path = "status.db"
url = "https://time-capsule-messages.herokuapp.com/data/"
 
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
 
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def index():
    return render_template("index.html")


#Webhookからのリクエストをチェックします。
@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名検証のための値を取得します。
    signature = request.headers['X-Line-Signature']
 
    # リクエストボディを取得します。
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
 
    # handle webhook body
    # 署名を検証し、問題なければhandleに定義されている関数を呼び出す。
    try:
        handler.handle(body, signature)
    # 署名検証で失敗した場合、例外を出す。
    except InvalidSignatureError:
        abort(400)
    # handleの処理を終えればOK
    return 'OK'
 
def submit_card(user_id, message, status):
    # 2.stautsが0だったら「このメッセージで登録しますか？」
    # 3.statusが1だったら「この日付で登録しますか？」
    if status is None or status == 0:
        text_c = f'「{message}」を登録しますか？'
    if status == 1:
        text_c = f'「{message}」この日にちで登録しますか？'
    line_bot_api.push_message(
        user_id,
        TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text=text_c,
                actions=[
                    MessageTemplateAction(
                        label='Yes',
                        text='> Yes'
                    ),
                    MessageTemplateAction(
                        label='No',
                        text='> No'
                    )
                ]
            )
        )
    )

def push_db(date:str, content:str, created_datetime:str, user_id:str, status:int):
    conn = sqlite3.connect(path)

    c = conn.cursor()
    # Insert a row of data
    c.execute(f"INSERT INTO stocks VALUES ('{date}','{content}', '', '{created_datetime}', '{user_id}', {status})")
 
    conn.commit()

    conn.close()

def user_status(user_id:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT status FROM stocks where user_id = "{user_id}"'):
        conn.close()
        return i[0]


def update_db(user_id:str, status:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    c.execute(f'UPDATE stocks SET {status} WHERE user_id = "{user_id}"')

    conn.commit()

    conn.close()


def delete_db(user_id:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute(f'DELETE from stocks WHERE user_id = "{user_id}"')

    conn.commit()

    conn.close()

def user_all_data(user_id:str):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    where_list = []

    for i in c.execute(f'SELECT * FROM stocks WHERE user_id = "{user_id}"'):
        where_list.append(i)

    conn.close()

    return where_list


def send_message(user_id:str, message:str):
    line_bot_api.multicast([user_id], TextSendMessage(text=message))


def pattern_math(date):
    date_type = re.compile(r"""(
        (^\d{4})        # First 4 digits number
        (\D)            # Something other than numbers
        (\d{1,2})       # 1 or 2 digits number
        (\D)            # Something other than numbers
        (\d{1,2})       # 1 or 2 digits number
        )""",re.VERBOSE)

    try:
        hit_date = date_type.search(date)
        bool_value = bool(hit_date)
        if bool_value is True:
            split = hit_date.groups()

            # Tuple unpacking
            year, month, day = int(split[1]),int(split[3]),int(split[5])

        if year>3000 or month >12 or day > 31:
            return False
        else:
            if month <= 9:
                month = '0' + str(month)
            if day <= 9:
                day = '0' + str(day)
            return [str(year), str(month), str(day)]
    except:
        return False

def now():
    return dt.datetime.now().strftime("%Y-%m-%d")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    message = event.message.text
    id = profile.user_id
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))
    # 1.ユーザのstatusを確認。
    
    status = user_status(id)

    if status is None:
        #登録
        # push_db(date:str, content:str, created_datetime:str, user_id:str, status:int)
        submit_card(id, message, status)
        push_db("", "", "", id, 0)
        
    # 2.stautsが0だったら「このメッセージで登録しますか？」Yes or No
    if status == 0:
        if message == "> Yes":
            # message, 
            update_db(id, f'message = "{message}", status = 1')
            send_message(id, "メッセージを登録しました。次に日付を設定してください")
            return
        if message == "> No":
            send_message(id, "メッセージを入力してください")
            return
        else:
            submit_card(id, message, status)
            return
    # 3.statusが1だったら「この日付で登録しますか？」
    if status == 1:
        if message == "> Yes":
            update_db(id, f'created_datetime = "{now()}"')
            q = user_all_data(id)[0]
            requests.get(url + f"?d={q[0]}&m={q[1]}&c={q[3]}&u={q[4]}")
            send_message(id, "Done. メッセージが届くのをお待ちください")
            delete_db(id)
            return
        if message == "> No":
            send_message(id, "日付を設定してください")
            return
        
        dates = pattern_math(message)

        if dates:
            update_db(id, f'date = "{dates[0]}-{dates[1]}-{dates[2]}"')
            submit_card(id, message, status)
            return
        elif not dates:
            send_message(id, "日付のフォーマットが間違っています")
            return

#     line_bot_api.reply_message(
#         event.reply_token,
#         TemplateSendMessage(
#         alt_text='Buttons template',
#         template=ButtonsTemplate(
#         thumbnail_image_url='https://example.com/image.jpg',
#         title='Menu',
#         text='Please select',
#         actions=[
#             PostbackAction(
#                 label='postback',
#                 display_text='postback text',
#                 data='action=buy&itemid=1'
#             ),
#             MessageAction(
#                 label='message',
#                 text='message text'
#             ),
#             URIAction(
#                 label='uri',
#                 uri='http://example.com/'
#             )
#         ]
#     )
# ))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    sticker_list = [
        '51626496', '51626497', '51626502', '51626504',
        '51626508', '51626511', '51626517', '51626530'
    ]

    sticker_message = StickerSendMessage(
        package_id='11538',
        sticker_id=random.choice(sticker_list)
    )

    line_bot_api.reply_message(
        event.reply_token,
        sticker_message
    )

# port
if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
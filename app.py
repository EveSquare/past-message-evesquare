from flask import Flask, request, abort, render_template, redirect
import random
 
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
 
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
 
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/triger')
def triger():
    line_bot_api.multicast(['Ud04d8ad9c4a2070d410d4b913422da5f'], TextSendMessage(text='Hello World!'))
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
 
def submit_text(user_id, message, status):
    # 2.stautsが0だったら「このメッセージで登録しますか？」
    # 3.statusが1だったら「この日付で登録しますか？」
    if status == 0:
        pass
    if status == 1:
        pass
    line_bot_api.push_message(
        user_id,
        TemplateSendMessage(
            alt_text='Confirm template',
            template=ConfirmTemplate(
                text=f'「{message}」を登録しますか？',
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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))
    # 1.ユーザのstatusを確認。

    # 2.stautsが0だったら「このメッセージで登録しますか？」
    # 3.statusが1だったら「この日付で登録しますか？」
    message = event.message.text
    if message == "> Yes":
        # message, 
        pass
    if message == "> No":
        pass
    else:
        submit_text(profile.user_id, message)
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
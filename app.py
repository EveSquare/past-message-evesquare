from flask import Flask, request, abort
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
    StickerMessage, StickerSendMessage
)
import os
 
app = Flask(__name__)
 
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
 
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
 

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
 


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # print(f'event.reply_token:{event.reply_token}')

    profile = line_bot_api.get_profile(event.source.user_id)

    line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='Are you sure?',
                    actions=[
                        PostbackTemplateAction(
                            label='Yes',
                            text='postback text',
                            data=print("hello")
                        ),
                        MessageTemplateAction(
                            label='No',
                            text='> No'
                        )
                    ]
                )
            )
        )


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
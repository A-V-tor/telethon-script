from pydantic import ValidationError
from config import DevelopmentConfig
from flask_qrcode import QRcode
import hypercorn.asyncio
from quart import (
    Quart,
    render_template,
    request,
    jsonify,
)
from telethon.sync import TelegramClient, events
from telethon.tl.types import PeerChannel
from .utils import (
    DataForMessage,
    RequestWildberriesAPI,
    open_database,
    save_to_database,
    PHONE_PATERN,
)


API_ID = DevelopmentConfig.API_ID
API_HASH = DevelopmentConfig.API_HASH

client = TelegramClient('name.session', API_ID, API_HASH)


app = Quart(__name__)
app.config.from_object(f'config.DevelopmentConfig')
qrcode = QRcode(app)


@app.before_serving
async def startup():
    await client.connect()


@app.after_serving
async def cleanup():
    await client.disconnect()


@app.route('/')
async def index():
    return await render_template('index.html')


@app.route('/login')
async def login_page():
    """Подключение устройства по qr коду."""
    # отдача данных в зависимости от того кто делает запрос
    user_agent = request.headers.get('User-Agent', False)

    qr_login = await client.qr_login()
    if not user_agent or len(user_agent) < 25:
        return {'qr_link_url': qr_login.url}, 200
    return await render_template('login.html', data_to_qr=qr_login)


@app.route('/check/login')
async def check_login():
    """Проверка авторизованного номера."""
    phone_number = request.args.get('phone', '')

    # проверить валидность номера
    if not PHONE_PATERN.match(phone_number):
        return {'valid error': 'неверный формат номера'}, 400
    try:
        me = await client.get_me()
        current_phone = me.phone
    except AttributeError:
        # если клиент не авторизован
        return {'error': 'Нет авторизованного клиента'}, 400

    if phone_number != current_phone:
        # номер не относится к текущему клиенту
        return {'status': 'waiting_qr_login'}, 208

    return {'status': 'login'}, 200


@app.route('/messages', methods=['POST'])
async def send_message():
    """Ендпоинт для отправки сообщений клиентом."""
    body = await request.get_json()
    try:
        DataForMessage(**body)
        companion = body['username']
        entity = await client.get_entity(companion)
        await client.send_message(entity, body['message_text'])
    except ValidationError as e:
        return {'validation error': str(e)}, 400
    except ValueError:
        return {'value error': f'No user has {companion} as username'}, 400

    return {'status': 'ok'}, 200


@app.route('/messages', methods=['GET'])
async def get_list_messages():
    """Ендпоинт для просмотра сообщений отправленных клиентом."""
    name = request.args.get('name', '')
    try:
        me = await client.get_me()
        phone = me.phone.strip()
    except AttributeError:
        # клиент не залогинен
        return {'error': 'need to login'}, 400
    try:
        entity = await client.get_entity(name)
    except ValueError:
        responce = {'ValueError': 'Cannot find any entity'}, 400
    else:
        database = open_database()
        user_chat = str(entity.id)
        responce = database[phone][user_chat]
    # отправить последние 50 сообщений из чата
    return jsonify(responce[::-1][:50])


async def handle_incoming_message(event):
    """Обработчик сообщений получаемых клиентом."""
    msg = 'Пожалуй я сохраню твое сообщение!Так что не шли глупости.'
    is_self = False
    sender = await event.get_sender()
    sender_username = sender.username if sender.username else ''
    message_text = event.text
    companion = event.peer_id
    me = await client.get_me()
    me_id = me.id

    # игнорировать сообщения топиков
    if isinstance(companion, PeerChannel):
        return

    companion_id = companion.user_id

    #  клиент пишет себе в избранное
    if companion_id == me_id:
        msg = 'Наверное это что-то важное, да?'
        is_self = True

    # сохранение сообщения
    data_dict = {
        'username': sender_username,
        'is_self': is_self,
        'message_text': message_text,
    }
    save_to_database(str(companion_id), me.phone, data_dict)

    # запрос к маркетплейсу
    if message_text.startswith('wild:'):
        msg = ''
        product = message_text.split('wild:')[1]
        api = RequestWildberriesAPI(product)
        try:
            list_data_products = api.make_request()
        except TimeoutError:
            await client.send_message(companion, 'Сервер не дал ответа')
            return

        for datatuple in list_data_products:
            part_msg = f'{datatuple[1]}\n{datatuple[0]}\n\n'
            msg += part_msg

    await client.send_message(companion, msg)


client.add_event_handler(handle_incoming_message, events.NewMessage)


async def main():
    await hypercorn.asyncio.serve(app, hypercorn.Config())

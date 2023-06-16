import requests
from cfg.config import TOKEN_YOOKASSA


def generate_request(amount, number_s):
    url = 'https://yoomoney.ru/api/request-payment'
    headers = {
        'Authorization': f'Bearer {TOKEN_YOOKASSA}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'pattern_id': 'p2p',
        'to': f'{number_s}',
        'amount': f'{amount}.00',
        'message': 'Вывод средств',
        'comment': 'Деньги с "Копилки"'
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        try:
            request_id = response.json()["request_id"]
            return accept_pay(request_id)
        except:
            return 'Произошла ошибка при подтверждении перевода, попробуйте снова'

    else:
        return 'Произошла ошибка при подтверждении перевода, попробуйте снова'


def accept_pay(request_id):
    url = 'https://yoomoney.ru/api/process-payment'
    headers = {
        'Authorization': f'Bearer {TOKEN_YOOKASSA}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'request_id': f'{request_id}'
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return 'Перевод успешно подтвержден'
    else:
        return 'Произошла ошибка при подтверждении перевода, попробуйте снова'

#!/usr/bin/python
# -*- coding: utf8 -*-
import serial
# import io
import struct
from struct import pack, unpack
from binascii import b2a_hex, hexlify
import inspect
from functools import partial

import settings
import logging
import time
from collections import namedtuple
from pprint import pprint as pp

# Пароль админа по умолчанию = 30, Пароль кассира по умолчанию = 1
PASSWORD = 30

ENQ = '\x05'
STX = '\x02'
ACK = '\x06'
NAK = '\x15'

ERROR_CODES = {
    0x00: "Ошибок нет",
    0x01: "Неисправен накопитель ФП 1, ФП 2 или часы",
    0x02: "Отсутствует ФП 1",
    0x03: "Отсутствует ФП 2",
    0x04: "Некорректные параметры в команде обращения к ФП",
    0x05: "Нет запрошенных данных",
    0x06: "ФП в режиме вывода данных",
    0x07: "Некорректные параметры в команде для данной реализации ФП",
    0x08: "Команда не поддерживается в данной реализации ФП",
    0x09: "Некорректная длина команды",
    0x0A: "Формат данных не BCD",
    0x0B: "Неисправна ячейка памяти ФП при записи итога",
    0x11: "Не введена лицензия",
    0x12: "Заводской номер уже введен",
    0x13: "Текущая дата меньше даты последней записи в ФП",
    0x14: "Область сменных итогов ФП переполнена",
    0x15: "Смена уже открыта",
    0x16: "Смена не открыта",
    0x17: "Номер первой смены больше номера последней смены",
    0x18: "Дата первой смены больше даты последней смены",
    0x19: "Нет данных в ФП",
    0x1A: "Область перерегистраций в ФП переполнена",
    0x1B: "Заводской номер не введен",
    0x1C: "В заданном диапазоне есть поврежденная запись",
    0x1D: "Повреждена последняя запись сменных итогов",
    0x1E: "Область перерегистраций ФП переполнена",
    0x1F: "Отсутствует память регистров",
    0x20: "Переполнение денежного регистра при добавлении",
    0x21: "Вычитаемая сумма больше содержимого денежного регистра",
    0x22: "Неверная дата",
    0x23: "Нет записи активизации",
    0x24: "Область активизаций переполнена",
    0x25: "Нет активизации с запрашиваемым номером",
    0x26: "Вносимая клиентом сумма меньше суммы чека",
    0x2B: "Невозможно отменить предыдущую команду",
    0x2C: "Обнулённая касса (повторное гашение невозможно)",
    0x2D: "Сумма чека по секции меньше суммы сторно",
    0x2E: "В ФР нет денег для выплаты",
    0x30: "ФР заблокирован, ждет ввода пароля налогового инспектора",
    0x32: "Требуется выполнение общего гашения",
    0x33: "Некорректные параметры в команде",
    0x34: "Нет данных",
    0x35: "Некорректный параметр при данных настройках",
    0x36: "Некорректные параметры в команде для данной реализации ФР",
    0x37: "Команда не поддерживается в данной реализации ФР",
    0x38: "Ошибка в ПЗУ",
    0x39: "Внутренняя ошибка ПО ФР",
    0x3A: "Переполнение накопления по надбавкам в смене",
    0x3B: "Переполнение накопления в смене",
    0x3C: "Смена открыта – операция невозможна | ЭКЛЗ: неверный регистрационный номер",
    0x3D: "Смена не открыта – операция невозможна",
    0x3E: "Переполнение накопления по секциям в смене",
    0x3F: "Переполнение накопления по скидкам в смене",
    0x40: "Переполнение диапазона скидок",
    0x41: "Переполнение диапазона оплаты наличными",
    0x42: "Переполнение диапазона оплаты типом 2",
    0x43: "Переполнение диапазона оплаты типом 3",
    0x44: "Переполнение диапазона оплаты типом 4",
    0x45: "Cумма всех типов оплаты меньше итога чека",
    0x46: "Не хватает наличности в кассе",
    0x47: "Переполнение накопления по налогам в смене",
    0x48: "Переполнение итога чека",
    0x49: "Операция невозможна в открытом чеке данного типа",
    0x4A: "Открыт чек – операция невозможна",
    0x4B: "Буфер чека переполнен",
    0x4C: "Переполнение накопления по обороту налогов в смене",
    0x4D: "Вносимая безналичной оплатой сумма больше суммы чека",
    0x4E: "Смена превысила 24 часа",
    0x4F: "Неверный пароль",
    0x50: "Идет печать предыдущей команды",
    0x51: "Переполнение накоплений наличными в смене",
    0x52: "Переполнение накоплений по типу оплаты 2 в смене",
    0x53: "Переполнение накоплений по типу оплаты 3 в смене",
    0x54: "Переполнение накоплений по типу оплаты 4 в смене",
    0x55: "Чек закрыт – операция невозможна",
    0x56: "Нет документа для повтора",
    0x57: "ЭКЛЗ: количество закрытых смен не совпадает с ФП",
    0x58: "Ожидание команды продолжения печати",
    0x59: "Документ открыт другим оператором",
    0x5A: "Скидка превышает накопления в чеке",
    0x5B: "Переполнение диапазона надбавок",
    0x5C: "Понижено напряжение 24В",
    0x5D: "Таблица не определена",
    0x5E: "Некорректная операция",
    0x5F: "Отрицательный итог чека",
    0x60: "Переполнение при умножении",
    0x61: "Переполнение диапазона цены",
    0x62: "Переполнение диапазона количества",
    0x63: "Переполнение диапазона отдела",
    0x64: "ФП отсутствует",
    0x65: "Не хватает денег в секции",
    0x66: "Переполнение денег в секции",
    0x67: "Ошибка связи с ФП",
    0x68: "Не хватает денег по обороту налогов",
    0x69: "Переполнение денег по обороту налогов",
    0x6A: "Ошибка питания в момент ответа по I2C",
    0x6B: "Нет чековой ленты",
    0x6C: "Нет контрольной ленты",
    0x6D: "Не хватает денег по налогу",
    0x6E: "Переполнение денег по налогу",
    0x6F: "Переполнение по выплате в смене",
    0x70: "Переполнение ФП",
    0x71: "Ошибка отрезчика",
    0x72: "Команда не поддерживается в данном подрежиме",
    0x73: "Команда не поддерживается в данном режиме",
    0x74: "Ошибка ОЗУ",
    0x75: "Ошибка питания",
    0x76: "Ошибка принтера: нет импульсов с тахогенератора",
    0x77: "Ошибка принтера: нет сигнала с датчиков",
    0x78: "Замена ПО",
    0x79: "Замена ФП",
    0x7A: "Поле не редактируется",
    0x7B: "Ошибка оборудования",
    0x7C: "Не совпадает дата",
    0x7D: "Неверный формат даты",
    0x7E: "Неверное значение в поле длины",
    0x7F: "Переполнение диапазона итога чека",
    0x80: "Ошибка связи с ФП",
    0x81: "Ошибка связи с ФП",
    0x82: "Ошибка связи с ФП",
    0x83: "Ошибка связи с ФП",
    0x84: "Переполнение наличности",
    0x85: "Переполнение по продажам в смене",
    0x86: "Переполнение по покупкам в смене",
    0x87: "Переполнение по возвратам продаж в смене",
    0x88: "Переполнение по возвратам покупок в смене",
    0x89: "Переполнение по внесению в смене",
    0x8A: "Переполнение по надбавкам в чеке",
    0x8B: "Переполнение по скидкам в чеке",
    0x8C: "Отрицательный итог надбавки в чеке",
    0x8D: "Отрицательный итог скидки в чеке",
    0x8E: "Нулевой итог чека",
    0x8F: "Касса не фискализирована",
    0x90: "Поле превышает размер, установленный в настройках",
    0x91: "Выход за границу поля печати при данных настройках шрифта",
    0x92: "Наложение полей",
    0x93: "Восстановление ОЗУ прошло успешно",
    0x94: "Исчерпан лимит операций в чеке",
    0xA0: "Ошибка связи с ЭКЛЗ",
    0xA1: "ЭКЛЗ отсутствует",
    0xA2: "ЭКЛЗ: Некорректный формат или параметр команды",
    0xA3: "Некорректное состояние ЭКЛЗ",
    0xA4: "Авария ЭКЛЗ",
    0xA5: "Авария КС в составе ЭКЛЗ",
    0xA6: "Исчерпан временной ресурс ЭКЛЗ",
    0xA7: "ЭКЛЗ переполнена",
    0xA8: "ЭКЛЗ: Неверные дата и время",
    0xA9: "ЭКЛЗ: Нет запрошенных данных",
    0xAA: "Переполнение ЭКЛЗ (отрицательный итог документа)",
    0xB0: "ЭКЛЗ: Переполнение в параметре количество",
    0xB1: "ЭКЛЗ: Переполнение в параметре сумма",
    0xB2: "ЭКЛЗ: Уже активизирована",
    0xC0: "Контроль даты и времени (подтвердите дату и время)",
    0xC1: "ЭКЛЗ: суточный отчёт с гашением прервать нельзя",
    0xC2: "Превышение напряжения в блоке питания",
    0xC3: "Несовпадение итогов чека и ЭКЛЗ",
    0xC4: "Несовпадение номеров смен",
    0xC5: "Буфер подкладного документа пуст",
    0xC6: "Подкладной документ отсутствует",
    0xC7: "Поле не редактируется в данном режиме",
}

FP_MODES_DESCR = {
    0: 'Принтер в рабочем режиме.',
    1: 'Выдача данных.',
    2: 'Открытая смена, 24 часа не кончились.',
    3: 'Открытая смена, 24 часа кончились.',
    4: 'Закрытая смена.',
    5: 'Блокировка по неправильному паролю налогового инспектора.',
    6: 'Ожидание подтверждения ввода даты.',
    7: 'Разрешение изменения положения десятичной точки.',
    8: 'Открытый документ:',
    9: ('Режим разрешения технологического обнуления.'
        'В этот режим ККМ переходит по включению питания'
        'если некорректна информация в энергонезависимом ОЗУ ККМ.'),
    10: 'Тестовый прогон.',
    11: 'Печать полного фис. отчета.',
    12: 'Печать отчёта ЭКЛЗ.',
    13: 'Работа с фискальным подкладным документом:',
    14: 'Печать подкладного документа.',
    15: 'Фискальный подкладной документ сформирован.'
}

FR_SUBMODES_DESCR = {
    8: {
        0: 'Продажа',
        1: 'Покупка',
        2: 'Возврат продажи',
        3: 'Возврат покупки'
    },
    13: {
        0: 'Продажа (открыт)',
        1: 'Покупка (открыт)',
        2: 'Возврат продажи (открыт)',
        3: 'Возврат покупки (открыт)'
    },
    14: {
        0: 'Ожидание загрузки.',
        1: 'Загрузка и позиционирование.',
        2: 'Позиционирование.',
        3: 'Печать.',
        4: 'Печать закончена.',
        5: 'Выброс документа.',
        6: 'Ожидание извлечения.'},
}


class Error(Exception):
    def __str__(self):
        return "%s %s" % (self.args)
    pass


def LRC(data, lenData=None):
    """Подсчет CRC"""
    result = 0
    if lenData is None:
        lenData = len(data)
    result = result ^ lenData
    for c in data:
        result = result ^ ord(c)
    return chr(result)


def float2100int(f, digits=2):
    mask = "%." + str(digits) + 'f'
    s = mask % f
    return int(s.replace('.', ''))


class Driver(object):
    """docstring for Driver"""
    def __init__(self, port, baudrate):
        super(Driver, self).__init__()
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=2)
        self.ser.flushOutput()
        self.ser.flushInput()

    def _read(self, l):
        data = ''
        for i in range(3):
            r = self.ser.read(l)
            data += r

            l -= len(r)
            if l == 0:
                break
            logging.debug('read %d bytes data = [%s]', l, hexlify(data))

        if l != 0:
            raise Error('Read Timeout', -1)

        return data

    def _write(self, data):
        self.ser.write(data)

    def _wait_for(self, match, how_long=100):
        r = self._read(1)
        for i in range(how_long):
            r += self._read(1)
            r = r[-len(match):]
            if match == r:
                return True

            if NAK == r[-1]:
                logging.debug('<< NAK[%s]', hexlify(r[-1]))
            else:
                logging.warning('<< bullshit[%s]', hexlify(r[-1]))

        return False

    def read_answer(self):
        logging.debug('read_answer')
        data = None  # нет связи

        for i in range(100):
            self._write(ENQ)

            if not self._wait_for(ACK + STX, how_long=150):
                logging.debug('try again')
                continue
            logging.debug('<< ACK STX')

            len_cmd = self._read(1)
            logging.debug('<< len[%s]', hexlify(len_cmd))

            data = self._read(ord(len_cmd))
            if not data:
                logging.debug('>> NAK[%s]', hexlify(NAK))
                self._write(NAK)
                continue
            logging.debug('<< data[%s]', hexlify(data))

            crc = self._read(1)

            logging.debug('<< LRC[%s]', hexlify(crc))
            if crc == LRC(data):
                logging.debug('>> ACK[%s]', hexlify(ACK))
                self._write(ACK)
                break
            else:
                logging.debug('>> NAK[%s]', hexlify(NAK))
                self._write(NAK)
                continue

        return data

    def raw(self, cmd):
        len_cmd = len(cmd)
        crc = LRC(cmd, len_cmd)
        self._write(STX)
        self._write(chr(len_cmd))
        self._write(cmd)
        self._write(crc)
        logging.debug('>> STX[%s]:len[%s]:data[%s]:LRC[%s]',
                      hexlify(STX), hexlify(chr(len_cmd)),
                      hexlify(cmd), hexlify(crc))
        self.ser.flush()

    def send_cmd(self, cmd):
        res = ()

        self.raw(cmd)
        while True:
            data = self.read_answer()
            if not data:
                continue

            cmd_answer = data[0]
            if cmd_answer != cmd[0]:
                # Не разобрался пока с магией внизу но походу
                # это должно решить вопросх
                logging.warning(
                    'Получил ответ от другой команды =\ %s != %s попробую еще раз',
                    hexlify(cmd_answer), hexlify(cmd[0])
                )
                continue

            error_code = data[1]
            error_code_str = ERROR_CODES.get(
                ord(error_code),
                'Неизвестная ошибка %s' % error_code
            )
            logging.debug('>> result %s %s',
                          hexlify(error_code),
                          error_code_str)

            if 0x00 == ord(error_code):
                res = (True, 'Ok', 0, data[2:])
                break

            # TODO разобраться потом что это за магия
            # Идет печать предыдущей команды
            elif 0x50 == ord(error_code):
                time.sleep(0.25)
                continue
            # Ожидание команды продолжения печати
            elif 0x58 == ord(error_code):
                time.sleep(0.25)

                self.raw(pack('<Bi', 0xB0, PASSWORD))
                # закоментирую это по идее просто получу ответ
                # от этой команды
                # и буду ждать ответ от своей
                # data = self.read_answer()
                continue
            else:
                res = (False,
                       '0x%s %s' % (hexlify(error_code), error_code_str),
                       '0x%s' % hexlify(error_code),
                       data[2:])
                break
        return res

    def std_cmd(self, num,
                request_frm='', req_params=(),
                responce_frm='', res_params="",):

        self.ser.flushOutput()
        self.ser.flushInput()

        caller_name = inspect.currentframe().f_back.f_code.co_name
        if hasattr(self, caller_name):
            logging.debug(getattr(self, caller_name).__doc__)

        logging.info('Cmd_0x%x%s' % (num, req_params))

        try:
            cmd = pack('<B', num) + pack(request_frm, *req_params)
            is_ok, error_str, error_code, data = self.send_cmd(cmd)
        except struct.error as e:
            logging.error(
                'Неверный формат для упаковки аргументов "%s" "%s" ',
                request_frm, req_params
            )
            logging.error(e)
            raise

        res = None
        logging.debug('data_len = %d' % len(data))

        answer_len = struct.calcsize(responce_frm)
        try:
            if res_params:
                res = namedtuple('cmd_%x' % num, res_params)
                res = res._make(unpack(responce_frm, data[:answer_len]))
                res = dict(res._asdict())
                res['_tail'] = data[answer_len:]
            else:
                res = list(unpack(responce_frm, data[:answer_len]))
                res.append(data[answer_len:])
        except struct.error as e:
            logging.error(
                'Неверный формат для распаковки ответа "%s" "%s" ',
                responce_frm, hexlify(data)
            )
            logging.error(e)

        logging.info('Cmd_0x%x%s -> %s',
                     num, req_params,
                     (is_ok, error_str, res))

        if is_ok:
            return res
        else:
            raise Error(error_str, error_code)
        # return is_ok, error_str, res

    def beep(self):
        """
        Команда: Гудок
            13H. Длина сообщения: 5 байт.
            • Пароль оператора (4 байта)
            Ответ:
            13H. Длина сообщения: 3 байта.
            • Код ошибки (1 байт)
            • Порядковый номер оператора (1 байт) 1...30
        """
        return self.std_cmd(
            0x13,
            '<i', (PASSWORD,),
            '<B', 'byte',
        )

    def cash_income(self, summ):
        """
            Команда: Внесение
            50H. Длина сообщения: 10 байт.
            Пароль оператора (4 байта)
            Сумма (5 байт)
            Ответ:
            50H. Длина сообщения: 5 байт.
            Код ошибки (1 байт)
            Порядковый номер оператора (1 байт) 1...30
            Сквозной номер документа (2 байта)
        """
        return self.std_cmd(
            0x50,
            '<ilb', (PASSWORD, float2100int(summ), 0),
            '<BH', '',
        )
        # cmd = pack('<BilB', 0x50, PASSWORD, float2100int(summ), 0)
        # is_ok, error_str, data = self.send_cmd(cmd)
        # return is_ok, error_str, unpack('<BH', data)

    def cash_outcome(self, summ):
        """
            Команда: Выплата
        """
        return self.std_cmd(
            0x51,
            '<ilb', (PASSWORD, float2100int(summ), 0),
            '<BH', '',
        )

    def cancel_check(self):
        """Команда: Аннулирование чека
        88H. Длина сообщения: 5 байт.
        Пароль оператора (4 байта)
        Ответ:
        88H. Длина сообщения: 3 байта.
        Код ошибки (1 байт)
        Порядковый номер оператора (1 байт) 1...30
        """
        return self.std_cmd(
            0x88,
            '<i', (PASSWORD, ),
            '<B', 'operator',
        )

    def open_drawer(self):
        """ Команда: Открыть денежный ящик
        28H. Длина сообщения: 6 байт.
        Пароль оператора (4 байта)
        Номер денежного ящика (1 байт) 0, 1
        Ответ:
        28H. Длина сообщения: 3 байта.
        Код ошибки (1 байт)
        Порядковый номер оператора (1 байт) 1...30
        """
        return self.std_cmd(
            0x28,
            '<iB', (PASSWORD, 0),
            '<B', 'operator',
        )

    def report_z(self):
        """Команда: Суточный отчет с гашением
        41H. Длина сообщения: 5 байт.
        Пароль администратора или системного администратора (4 байта)
        Ответ:
        41H. Длина сообщения: 3 байта.
        Код ошибки (1 байт)
        Порядковый номер оператора (1 байт) 29, 30
        """
        return self.std_cmd(
            0x41,
            '<i', (PASSWORD, ),
            '<B', 'operator',
        )

    def report_x(self):
        """Команда: Суточный отчет без гашения
        40H. Длина сообщения: 5 байт.
        Пароль администратора или системного администратора (4 байта)
        Ответ:
        40H. Длина сообщения: 3 байта.
        Код ошибки (1 байт)
        Порядковый номер оператора (1 байт) 29, 30
        """
        return self.std_cmd(
            0x40,
            '<i', (PASSWORD, ),
            '<B', 'operator',
        )

    def _dont_care_get_type(self):
        """Команда: Суточный отчет без гашения
        Получить тип устройства
        Команда:
            FCH. Длина сообщения: 1 байт.
        Ответ:
            FCH. Длина сообщения: (8+X) байт.
            • Код ошибки (1 байт)
            • Тип устройства (1 байт) 0...255
            • Подтип устройства (1 байт) 0...255
            • Версия протокола для данного устройства (1 байт) 0...255
            • Подверсия протокола для данного устройства (1 байт) 0...255
            • Модель устройства (1 байт) 0...255
            • Язык устройства (1 байт) 0...255 русский – 0; английский – 1;
            • Название устройства – строка символов в кодировке WIN1251. Количество
            байт, отводимое под название устройства, определяется в каждом конкретном
            случае самостоятельно разработчиками устройства (X байт)
        """
        return self.std_cmd(
            0xfc,
            '<i', (PASSWORD, ),
            '<B', 'type subtype protocolv subprotocolv model lang',
        )

    def print_report(self, close=None):
        if close:
            kkm.report_z()
        else:
            kkm.report_x()

    def open_check(self, ctype=0, is_refund=None):
        """
        Команда:
            8DH. Длина сообщения: 6 байт.
            • Пароль оператора (4 байта)
            • Тип документа (1 байт): 0 – продажа;
            1 – покупка;
            2 – возврат продажи;
            3 – возврат покупки
            Ответ:       8DH. Длина сообщения: 3 байта.
            • Код ошибки (1 байт)
            • Порядковый номер оператора (1 байт) 1...30
        """
        if is_refund is True:
            ctype = 2
        else:
            ctype = 0
        return self.std_cmd(
            0x8d,
            '<iB', (PASSWORD, ctype),
            '<B', 'operator',
        )

    def sale(self, amount, price, text=u"",
             taxes=None, department=0, is_refund=False):
        """Команда:     8DH. Длина сообщения: 6 байт.
        • Пароль оператора (4 байта)
        • Тип документа (1 байт): 0 – продажа;
        1 – покупка;
        2 – возврат продажи;
        3 – возврат покупки
        Ответ:       8DH. Длина сообщения: 3 байта.
        • Код ошибки (1 байт)
        • Порядковый номер оператора (1 байт) 1...30
        """
        if taxes is None:
            taxes = [0, 0, 0, 0]

        if is_refund:
            cmd_num = 0x82  # Возврат продажи
        else:
            cmd_num = 0x80  # Продажа

        return self.std_cmd(
            cmd_num,
            '<ilclcBBBBB40s', (PASSWORD,
                               float2100int(amount) * 10,
                               '\x00',
                               float2100int(price),
                               '\x00',
                               department,
                               taxes[0], taxes[1], taxes[2], taxes[3],
                               text[:40].encode('cp1251').ljust(40, '\x00')
                               ),
            '<B', 'operator',
        )

    def close_check(self, summa, discount=0, text=u"",
                    summa2=0, summa3=0, summa4=0,
                    taxes=[0, 0, 0, 0][:]):

        """
            Команда:     85H. Длина сообщения: 71 байт.
                 • Пароль оператора (4 байта)
                 • Сумма наличных (5 байт) 0000000000...9999999999
                 • Сумма типа оплаты 2 (5 байт) 0000000000...9999999999
                 • Сумма типа оплаты 3 (5 байт) 0000000000...9999999999
                 • Сумма типа оплаты 4 (5 байт) 0000000000...9999999999
                 • Скидка/Надбавка(в случае отрицательного значения) в % на чек от 0 до 99,99
                   % (2 байта со знаком) -9999...9999
                 • Налог 1 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                 • Налог 2 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                 • Налог 3 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                 • Налог 4 (1 байт) «0» – нет, «1»...«4» – налоговая группа
                 • Текст (40 байт)
            Ответ:       85H. Длина сообщения: 8 байт.
                 • Код ошибки (1 байт)
                 • Порядковый номер оператора (1 байт) 1...30
                 • Сдача (5 байт) 0000000000...9999999999
        """
        data = self.std_cmd(
            0x85,
            '<ilclclclchBBBB40s', (PASSWORD,
                                   float2100int(summa), '\x00',
                                   float2100int(summa2), '\x00',
                                   float2100int(summa3), '\x00',
                                   float2100int(summa4), '\x00',
                                   float2100int(discount),
                                   taxes[0], taxes[1], taxes[2], taxes[3],
                                   text[:40].encode('cp1251').ljust(40, '\x00')
                                   ),
            '<Blx', 'operator renting',
        )
        if data and 'renting' in data:
            data['renting'] = data['renting'] / 100.0
        return data

    def set_taxes(self, taxes=None):
        if taxes is None:
            logging.warning('set_taxes taxes list is empty')
            return False
        for i, (k, v) in enumerate(taxes):
            self.set_table_value(6, i + 1,
                                 2, k.encode('cp1251'))
            self.set_table_value(6, i + 1,
                                 1, pack('H', int(v) * 100))
        return True

    def set_header(self, text_list=None):
        if text_list is None:
            logging.warning('set_header header list is empty')
            return

        for i, t in zip(range(11, 15), text_list):
            self.set_table_value(4, i, 1, t.encode('cp1251'))

    def print_check(self, cash, items=None, mode='',
                    is_refund=False, taxes=None,
                    extra_text=None):
        # TODO не понятно что за taxes которые закрывают чек
        # так что просто поставлю по умолчанию те что были у типов
        # ну и можно руками ввести
        if mode == 'plastic':
            if taxes is None:
                taxes = [0, 2, 0, 0]

            self._check(cash, items,
                        open_check=partial(self.open_check,
                                           is_refund=is_refund),
                        sale=partial(self.sale, is_refund=is_refund),
                        close_check=partial(self.close_check,
                                            summa=0,
                                            summa2=cash,
                                            taxes=taxes,
                                            ),
                        on_error=self.cancel_check,
                        extra_text=extra_text,
                        )
        elif mode == 'cash':
            if taxes is None:
                taxes = [2, 0, 0, 0]
            self._check(cash, items,
                        open_check=partial(self.open_check, is_refund=is_refund),
                        sale=partial(self.sale, is_refund=is_refund),
                        close_check=partial(self.close_check,
                                            summa=cash,
                                            taxes=taxes,
                                            ),
                        on_error=self.cancel_check,
                        extra_text=extra_text,
                        )
            self.open_drawer()
        else:
            raise Error('Неизветный mode = %s Варианты: (plastic, cash)' % mode,
                        str(mode))

    def _check(self, cash, items=None, taxes=None,
               open_check=lambda: 0,
               sale=lambda: 0,
               close_check=lambda: 0,
               on_error=lambda: 0,
               mode='',
               extra_text=None):
        if not items:
            items = []
        if not taxes:
            taxes = [0, 0, 0, 0]

        try:
            logging.info("Включаем печать налоговыx ставок и суммы налога")
            self.set_table_value(1, 1, 19, chr(0x02))
        except Error as e:
            logging.error(str(e))

        logging.debug((
            cash,
            [tuple(map(i.get, ['text', 'qty', 'price', 'taxes'])) for i in items]
        ))

        try:
            open_check()
            for item in items:
                sale(
                    item['qty'],
                    item['price'],
                    item['text'],
                    item['taxes'],
                )

            if extra_text:
                self.writeln(extra_text)

            close_check(
                # text="------------------------------",
            )
        except Error:
            on_error()
            raise


    def get_state(self,):
        """
            Команда:
            11H. Длина сообщения: 5 байт.
            • Пароль оператора (4 байта)
            Ответ:
            11H. Длина сообщения: 48 байт.
            • Код ошибки (1 байт)
            • Порядковый номер оператора (1 байт) 1...30
            • Версия ПО ФР (2 байта)
            • Сборка ПО ФР (2 байта)
            • Дата ПО ФР (3 байта) ДД-ММ-ГГ
            • Номер в зале (1 байт)
            • Сквозной номер текущего документа (2 байта)
            • Флаги ФР (2 байта)
            • Режим ФР (1 байт)
            • Подрежим ФР (1 байт)
            • Порт ФР (1 байт)
            • Версия ПО ФП (2 байта)
            • Сборка ПО ФП (2 байта)
            • Дата ПО ФП (3 байта) ДД-ММ-ГГ
            • Дата (3 байта) ДД-ММ-ГГ
            • Время (3 байта) ЧЧ-ММ-СС
            • Флаги ФП (1 байт)
            • Заводской номер (4 байта)
            • Номер последней закрытой смены (2 байта)
            • Количество свободных записей в ФП (2 байта)
            • Количество перерегистраций (фискализаций) (1 байт)
            • Количество оставшихся перерегистраций (фискализаций) (1 байт)
            • ИНН (6 байт)
        """
        r = [
            ('B', 'operator'),     # "Порядковый номер оператора (1 байт) 1...30",
            ('H', 'fr_ver'),     # "Версия ПО ФР (2 байта)",
            ('H', 'fr_build'),     # "Сборка ПО ФР (2 байта)",
            ('3s', 'fr_date'),     # "Дата ПО ФР (3 байта) ДД-ММ-ГГ",
            ('B', 'room_num'),     # "Номер в зале (1 байт)",
            ('H', 'doc_num'),     # "Сквозной номер текущего документа (2 байта)",
            ('2s', 'fr_flags'),     # "Флаги ФР (2 байта)",
            ('B', 'mode'),     # "Режим ФР (1 байт)",
            ('B', 'submode'),     # "Подрежим ФР (1 байт)",
            ('B', 'fr_port'),     # "Порт ФР (1 байт)",
            ('H', 'fp_ver'),     # "Версия ПО ФП (2 байта)",
            ('H', 'fp_build'),     # "Сборка ПО ФП (2 байта)",
            ('3s', 'fp_date'),     # "Дата ПО ФП (3 байта) ДД-ММ-ГГ",
            ('3s', 'date'),     # "Дата (3 байта) ДД-ММ-ГГ",
            ('3s', 'time'),     # "Время (3 байта) ЧЧ-ММ-СС",
            ('B', 'flags_fp'),     # "Флаги ФП (1 байт)",
            ('L', 'factory_number'),     # "Заводской номер (4 байта)",
            ('H', 'last_closed_tour'),     # "Номер последней закрытой смены (2 байта)",
            ('H', 'free_fp_records'),     # "Количество свободных записей в ФП (2 байта)",
            ('B', 'register_count'),     # "Количество перерегистраций (фискализаций) (1 байт)",
            ('B', 'register_count_left'),     # "Количество оставшихся перерегистраций (фискализаций) (1 байт)"
            ('6s', 'inn'),     # "ИНН (6 байт)",
        ]
        res = self.std_cmd(
            0x11,
            '<i', (PASSWORD, ),
            '<' + ''.join([i[0] for i in r]),
            '' + ' '.join([i[1] for i in r]),
        )
        # res['fp_date'] = '%02i.%02i.20%02i' % tuple(bytearray(res['fp_date']))
        # res['fr_date'] = '%02i.%02i.20%02i' % tuple(bytearray(res['fr_date']))
        # res['date'] = '%02i.%02i.20%02i' % tuple(bytearray(res['date']))
        # res['time'] = '%02i.%02i.%02i' % tuple(bytearray(res['time']))
        res['fp_date'] = tuple(bytearray(res['fp_date']))
        res['fr_date'] = tuple(bytearray(res['fr_date']))
        res['date'] = tuple(bytearray(res['date']))
        res['time'] = tuple(bytearray(res['time']))

        res['mode_str'] = ' Режим: %s' % FP_MODES_DESCR.get(res['mode'], 'Режим неизвестен')
        res['submode_str'] = ' Подрежим: %s' % FR_SUBMODES_DESCR.get(res['mode'], {}).get(res['submode'], 'Подрежим не предусмотрен')

        if 0:
            print bin(res['fr_flags'])
            bits = bin(res['fr_flags']).lstrip('0b').rjust(16, '0')
            flags = [b == '1' for b in bits]

        print bin(ord(res['fr_flags'][0])).lstrip('0b').rjust(8, '0')
        print bin(ord(res['fr_flags'][1])).lstrip('0b').rjust(8, '0')

        res['fr_flags_raw'] = [
            bin(ord(res['fr_flags'][i])).lstrip('0b').rjust(8, '0') for i in [0, 1]
        ]
        if 0:
            res['fr_flags'] = dict(zip(
                [
                    'roll_oper_log',  # 0 – Рулон операционного журнала (0 – нет, 1 – есть)
                    'roll_check_tape',  # 1 – Рулон чековой ленты (0 – нет, 1 – есть)
                    'top_sensor_doc',  # 2 – Верхний датчик подкладного документа (0 – нет, 1 – да)
                    'lower_sensor_doc',  # 3 – Нижний датчик подкладного документа (0 – нет, 1 – да)
                    'deciminal_point,  '# 4 – Положение десятичной точки (0 – 0 знаков, 1 – 2 знака)
                    'ELKZ',   # 5 – ЭКЛЗ (0 – нет, 1 – есть)
                    'optical_sensor_oper_log',   # 6 – Оптический датчик операционного журнала (0 – бумаги нет, 1 – бумага есть)
                    'optical_sensor_check_tape', # 7 – Оптический датчик чековой ленты (0 – бумаги нет, 1 – бумага есть)
                    'thermal_track_control_tape', # 8 – Рычаг термоголовки контрольной ленты (0 – поднят, 1 – опущен)
                    'thermal_track_control_tape', # 9 – Рычаг термоголовки чековой ленты (0 – поднят, 1 – опущен)
                    'is_up', # 10 – Крышка корпуса ФР (0 – опущена, 1 – поднята)
                    'dawler', # 11 – Денежный ящик (0 – закрыт, 1 – окрыт)
                    'right_sensor_failure', # 12 – Отказ правого датчика принтера (0 – нет, 1 – да)
                    'left_sensor_failure', # 13 – Отказ левого датчика принтера (0 – нет, 1 – да)
                    'EKLZ_almost_full', # 14 – ЭКЛЗ почти заполнена (0 – нет, 1 – да)
                    'accurancy', # 15а – Увеличенная точность количества (0 – нормальная точность, 1 – увеличенная
                                 # точность) [для ККМ без ЭКЛЗ]
                                 # 15б – Буфер принтера непуст (0 – пуст, 1 – непуст)
                ],
                flags
            ))

        # print res

        return res

    def get_type_of_device(self):
        """
        """
        return self.std_cmd(
            0xfc,
            '<', (),
            '<B', 'reg_number',
        )

    def set_table_value(self, table, row, field, value, value_format=None):
        """
        Записать значение в таблицу, ряд, поле
        поля бывают бинарные и строковые, поэтому value
        делаем в исходном виде
        Команда:
            1EH. Длина сообщения: (9+X) байт.
            • Пароль системного администратора (4 байта)
            • Таблица (1 байт)
            • Ряд (2 байта)
            • Поле (1 байт)
            • Значение (X байт) до 40 байт
            Ответ:
            1EH. Длина сообщения: 2 байта.
            • Код ошибки (1 байт)
        """
        # drow = pack('l', row).ljust(2, chr(0x0))[:2]
        # assert drow == pack('<H', row)
        fmt = '<iBHB'
        if value_format:
            value_format = value_format.encode('utf-8')
            fmt += value_format
        else:
            # value = value.encode('cp1251')
            fmt += '%ds' % len(value)

        logging.info('set_table_value')
        logging.info((table, row, field, value, value_format))

        return self.std_cmd(
            0x1e,
            fmt, (PASSWORD,
                  table,
                  row,  # drow
                  field,
                  value),
            '<', '',
        )

    def get_table_value(self, table, row, field):
        """
            Чтение таблицы
            Команда:
            1FH. Длина сообщения: 9 байт.
                • Пароль системного администратора (4 байта)
                • Таблица (1 байт)
                • Ряд (2 байта)
                • Поле (1 байт)
            Ответ:
                1FH. Длина сообщения: (2+X) байт.
                • Код ошибки (1 байт)
                • Значение (X байт) до 40 байт
        """
        drow = pack('l', row).ljust(2, chr(0x0))[:2]
        assert drow == pack('<H', row)
        return self.std_cmd(
            0x1f,
            '<iBHB', (PASSWORD,
                      table,
                      row,
                      field),
            '<', '',
        )

    def repeat_check(self):
        """Команда:    8CH. Длина сообщения: 5 байт.
             • Пароль оператора (4 байта)
        Ответ:      8CH. Длина сообщения: 3 байта.
             • Код ошибки (1 байт)
             • Порядковый номер оператора (1 байт) 1...30
             Команда выводит на печать копию последнего закрытого документа
                 продажи, покупки, возврата продажи и возврата покупки.
        """
        return self.std_cmd(
            0x8c,
            '<i', (PASSWORD, ),
            '<B', 'operator',
        )

    def get_datetime(self):
        res = self.get_state()
        logging.debug('DATE: %02i.%02i.20%02i', *(res['date']))
        logging.debug('TIME: %02i:%02i:%02i', *(res['time']))
        return (res['date'], res['time'])

    def set_time(self, time=(19, 55, 0)):
        """
            Программирование времени
            Команда:
            21H. Длина сообщения: 8 байт.
            • Пароль системного администратора (4 байта)
            • Время (3 байта) ЧЧ-ММ-СС
            Ответ:
            21H. Длина сообщения: 2 байта.
            • Код ошибки (1 байт)
        """
        return self.std_cmd(
            0x21,
            '<iBBB', (PASSWORD, time[0], time[1], time[2]),
            '', '',
        )

    def set_date(self, date=(20, 3, 3)):
        self.set_date_1st(date)
        # TODO: вылетает с внутренней ошибкой выяснить
        # это дело в нефискальном режиме или ещё в чём
        self.set_date_confirm(date)

    def set_date_1st(self, date=(20, 3, 3)):
        """
            Программирование даты
            Команда:
            22H. Длина сообщения: 8 байт.
            • Пароль системного администратора (4 байта)
            • Дата (3 байта) ДД-ММ-ГГ
            Ответ:
            22H. Длина сообщения: 2 байта.
            • Код ошибки (1 байт)
        """
        return self.std_cmd(
            0x22,
            '<iBBB', (PASSWORD, date[0], date[1], date[2]),
            '', '',
        )

    def set_date_confirm(self, date=(20, 3, 3)):
        """
            Подтверждение программирования даты
            Команда:
            23H. Длина сообщения: 8 байт.
            • Пароль системного администратора (4 байта)
            • Дата (3 байта) ДД-ММ-ГГ
            Ответ:
            23H. Длина сообщения: 2 байта.
            • Код ошибки (1 байт)
        """
        return self.std_cmd(
            0x23,
            '<iBBB', (PASSWORD, date[0], date[1], date[2]),
            '', '',
        )

    def set_datetime(self, date, time):
        self.set_time(time)
        self.set_date(date)
        # TODO: вылетает с внутренней ошибкой выяснить
        # это дело в нефискальном режиме или ещё в чём
        self.set_date_confirm(date)

    def writeln(self, text):
        """
            печать строки
        """
        res = None
        if isinstance(text, list):
            for t in text:
                flag = 0x00 | 2
                res = self.std_cmd(
                    0x17,
                    '<iB%ds' % len(t), (PASSWORD, flag,
                                        t.decode('utf-8').encode('cp1251')),
                    '<B', 'operator',
                )
        else:
            flag = 0x00 | 2
            res = self.std_cmd(
                0x17,
                '<iB%ds' % len(text), (PASSWORD, flag,
                                       text.decode('utf-8').encode('cp1251')),
                '<B', 'operator',
            )
        return res

    def cut(self):
        """
            Отрезка чека
            Команда:
            25H. Длина сообщения: 6 байт.
            • Пароль оператора (4 байта)
            • Тип отрезки (1 байт) «0» – полная, «1» – неполная
            Ответ:
            25H. Длина сообщения: 3 байта.
            • Код ошибки (1 байт)
            • Порядковый номер оператора (1 байт) 1...30
        """
        return self.std_cmd(
            0x25,
            '<iB', (PASSWORD, 1),
            '<B', 'operator',
        )

    def ping(self):
        """
            Использую как Ping Запрос регистрационного номера ЭКЛЗ
        """
        return self.std_cmd(
            0xab,
            '<i', (PASSWORD,),
            '<5s', 'reg_number',
        )

    def close_port(self):
        self.ser.close()

    def is_open_port(self):
        self.ser.isOpen()


if __name__ == '__main__':
    print 'hahaha'
    logging.debug('common')
    kkm = Driver(settings.KKM['PORT'],
                 settings.KKM['BAUDRATE'])
    # print kkm.ping()
    # exit()

    kkm.set_header(text_list = [u' блин запорол хедер        ',
                                u'надеюсь это не критичная инфа       ',
                                u'надеюсь это не критичная инфа       ',
                                u'надеюсь это не критичная инфа  была     ',])
    # exit()
    if 0:
        taxes = [
            # ('НДС', 10),
            ('PDF', 15),
            ('RTFM', 50),
            ('KMFDM', 10),
            # ('Ебать колотить', 0),
        ]
        kkm.set_taxes(taxes)

    # kkm.repeat_check()
    # exit()

    # kkm.repeat_check()
    # kkm.set_time(time=(0, 0, 0))
    items = [
        # dict(qty=2, price=30, text=u'пакет травы'),
        # dict(qty=75, price=70, text=u'таблеток мескалина'),
        # dict(qty=5, price=70, text=u'кислота'),
        # dict(qty=1, price=70, text=u'пол солонки кокаина'),
        # dict(qty=1, price=70, text=u'танквилизаторы всех сортов и расцветок'),
        dict(qty=1, price=70, text=u'текила, ром, ящик пива,'),
        dict(qty=1, price=70, text=u'пинта чистого эфира и амилнитрит'),
        dict(qty=1, price=100, text=u'текила, ром, ящик пива,'),
        # dict(qty=1, price=30, text=u'пинта чистого эфира и амилнитрит'),
    ]

    # items = [ dict(qty=20, price=100, text=u'текила, ром, ящик пива,'), ]
    items = [
        dict(qty=2, price=100, text=u'ABCDE', taxes=[1, 0, 0, 0]),
        dict(qty=2, price=100, text=u'ABCDE', taxes=[2, 0, 0, 0]),
        dict(qty=2, price=100, text=u'ABCDE', taxes=[3, 0, 0, 0]),
        dict(qty=2, price=100, text=u'ABCDE', taxes=[4, 0, 0, 0]),
    ]
    kkm.print_check(800, items, mode='plastic')

    exit()



    # kkm.set_date()
    # kkm.set_datetime(date=(20, 3, 5), time=(19, 55, 0))
    # kkm.repeat_check()

    # kkm.report_z()
    # kkm.cancel_check()

    # pp(kkm.get_state())

    # kkm.std_cmd(
    #     0xfc,
    #     '<', (),
    #     '<BBBBBBBB', '',
    # )
    # exit()
    # nds = 4
    # # Включаем начисление налогов на ВСЮ операцию чека
    # kkm.open_check()
    # kkm.set_table_value(1, 1, 17, chr(0x1))
    # # Включаем печатать налоговые ставки и сумму налога
    # kkm.set_table_value(1, 1, 19, chr(0x2))
    # kkm.set_table_value(6, 2, 1, pack('l', nds * 100)[:2])
    # kkm.close_check()

    # for i in range(2):
    #     for i in range(2):
    #         print kkm.beep()
    #     # kkm.cash_income(10.0)
    #     print kkm.cancel_check()
    #     print kkm.beep()
    #     # kkm.cash_outcome(20.0)
    #     time.sleep(0.1)
    #     kkm.open_drawer()

    # kkm.print_report(close=True)

    # kkm.close_check(232, discount=2)
    # print kkm.get_table_value(6, 1, 1)
    # kkm.set_table_value(6, 1, 1, pack('l', nds * 100)[:2])
    # print kkm.get_table_value(6, 1, 1)

    # kkm.set_table_value(1, 1, 17, chr(0x1))
    # Включаем печатать налоговые ставки и сумму налога
    # kkm.set_table_value(1, 1, 19, chr(0x2))

    # kkm.get_table_value(1, 1, 19)
    # kkm.get_table_value(1, 1, 19)
    # kkm.get_table_value(6, 2, 1)
    # kkm.get_table_value(6, 2, 2)

    # kkm.set_table_value(6, 1, 1, pack('>H', 500))
    # kkm.get_table_value(6, 1, 1)

    # for item in items:
    #     kkm.sale(
    #         item['qty'],
    #         item['price'],
    #         item['text'][:40],
    #         taxes=[2, 0, 0, 0]
    #     )

#!/usr/bin/python
# -*- coding: utf8 -*-
import serial
# import io
import struct
from struct import pack, unpack
from binascii import b2a_hex, hexlify

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

class KKMError(Exception):
    pass

class Driver(object):
    """docstring for Driver"""
    def __init__(self, port, baudrate):
        super(Driver, self).__init__()
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=1)
        # self.ser_io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
        #                                newline='\r',
        #                                line_buffering=True)
        self.ser.flushOutput()
        self.ser.flushInput()

    def _read(self, l):
        data = ''
        for i in range(200):
            r = self.ser.read(l)
            data += r

            l -= len(r)
            if l == 0:
                break
            logging.debug('read %d bytes data = [%s]', l, hexlify(data))

        if l != 0:
            raise None

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
            if data:
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
                    res = (True, 'Ok', data[2:])
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
                           '%s %s' % (hexlify(error_code),
                                      error_code_str),
                           data[2:])
                    break
        return res

    def standart_command(self,
                         num,
                         req_frm='', req_params=(),
                         res_frm='', res_params="",
                         desc=""):

        self.ser.flushOutput()
        self.ser.flushInput()

        if desc:
            logging.info(desc)
        logging.info('Cmd_0x%x%s' % (num, req_params))

        try:
            cmd = pack('<B', num) + pack(req_frm, *req_params)
            is_ok, error_str, data = self.send_cmd(cmd)
        except struct.error as e:
            logging.error(
                'Неверный формат для упаковки аргументов "%s" "%s" ',
                req_frm, req_params
            )
            logging.error(e)

        res = None
        try:
            if res_params:
                res = namedtuple('cmd_%x' % num, res_params)
                res = res._make(unpack(res_frm, data))
                res = dict(res._asdict())
            else:
                res = list(unpack(res_frm, data))

        except struct.error as e:
            logging.error(
                'Неверный формат для распаковки ответа "%s" "%s" ',
                res_frm, hexlify(data)
            )
            logging.error(e)

        logging.info('Cmd_0x%x%s -> %s',
                     num, req_params,
                     (is_ok, error_str, res))

        if is_ok:
            return res
        else:
            raise KKMError(error_str)
        # return is_ok, error_str, res

    def beep(self):
        return self.standart_command(
            0x13,
            '<i', (PASSWORD,),
            '<B', 'byte',
            """
            Команда: Гудок
                13H. Длина сообщения: 5 байт.
                • Пароль оператора (4 байта)
                Ответ:
                13H. Длина сообщения: 3 байта.
                • Код ошибки (1 байт)
                • Порядковый номер оператора (1 байт) 1...30
            """
        )

    def cash_income(self, summ):
        return self.standart_command(
            0x50,
            '<ilb', (PASSWORD, float2100int(summ), 0),
            '<BH', '',
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
        )
        # cmd = pack('<BilB', 0x50, PASSWORD, float2100int(summ), 0)
        # is_ok, error_str, data = self.send_cmd(cmd)
        # return is_ok, error_str, unpack('<BH', data)

    def cash_outcome(self, summ):
        return self.standart_command(
            0x51,
            '<ilb', (PASSWORD, float2100int(summ), 0),
            '<BH', '',
            """
                Команда: Выплата
            """
        )

    def cancel_check(self):
        return self.standart_command(
            0x88,
            '<i', (PASSWORD, ),
            '<', '',
            """Команда: Аннулирование чека
            88H. Длина сообщения: 5 байт.
            Пароль оператора (4 байта)
            Ответ:
            88H. Длина сообщения: 3 байта.
            Код ошибки (1 байт)
            Порядковый номер оператора (1 байт) 1...30
            """
        )

    def open_drawer(self):
        return self.standart_command(
            0x28,
            '<iB', (PASSWORD, 0),
            '<B', 'operator',
            """ Команда: Открыть денежный ящик
            28H. Длина сообщения: 6 байт.
            Пароль оператора (4 байта)
            Номер денежного ящика (1 байт) 0, 1
            Ответ:
            28H. Длина сообщения: 3 байта.
            Код ошибки (1 байт)
            Порядковый номер оператора (1 байт) 1...30
            """
        )

    def report_z(self):
        return self.standart_command(
            0x41,
            '<i', (PASSWORD, ),
            '<B', 'operator',
            """Команда: Суточный отчет с гашением
            41H. Длина сообщения: 5 байт.
            Пароль администратора или системного администратора (4 байта)
            Ответ:
            41H. Длина сообщения: 3 байта.
            Код ошибки (1 байт)
            Порядковый номер оператора (1 байт) 29, 30
            """
        )

    def report_x(self):
        return self.standart_command(
            0x40,
            '<i', (PASSWORD, ),
            '<B', 'operator',
            """Команда: Суточный отчет без гашения
            40H. Длина сообщения: 5 байт.
            Пароль администратора или системного администратора (4 байта)
            Ответ:
            40H. Длина сообщения: 3 байта.
            Код ошибки (1 байт)
            Порядковый номер оператора (1 байт) 29, 30
            """
        )

    def print_report(self, close=None):
        if close:
            kkm.report_z()
        else:
            kkm.report_x()

    def open_check(self, ctype=0, fg_return=None, passwd=PASSWORD):
        if fg_return is True:
            ctype = 2
        elif fg_return is False:
            ctype = 0
        return self.standart_command(
            0x8d,
            '<iB', (PASSWORD, ctype),
            '<B', 'operator',
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
        )

    def sale(self, amount, price, text=u"", department=0,
             taxes=None, fg_return=False, passwd=PASSWORD):
        if taxes is None:
            taxes = [0, 0, 0, 0]

        if fg_return:
            cmd_num = 0x82  # Возврат продажи
        else:
            cmd_num = 0x80  # Продажа

        return self.standart_command(
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
        )

    def close_check(self, summa, discount=0, text=u"",
                    summa2=0, summa3=0, summa4=0,
                    taxes=[0, 0, 0, 0][:], passwd=PASSWORD):

        data = self.standart_command(
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
        )
        if data and 'renting' in data:
            data['renting'] = data['renting'] / 100.0
        return data

    def print_check(self, cash, items=None, mode=''):
        if not items:
            items = []

        logging.debug((
            cash,
            [tuple(map(i.get, ['text', 'qty', 'price'])) for i in items]
        ))

        try:
            self.open_check(ctype=0)
            for item in items:
                self.sale(
                    item['qty'],
                    item['price'],
                    item['text'][:40],
                    taxes=[2, 0, 0, 0]
                )
            if mode == 'plastic':
                self.close_check(
                    summa=0,
                    summa2=cash,
                    text="------------------------------",
                    taxes=[0, 2, 0, 0]
                )
            else:
                self.close_check(
                    summa=cash,
                    text="------------------------------",
                    taxes=[2, 0, 0, 0]
                )
                self.open_drawer()
        except KKMError:
            self.cancel_check()
            raise

    def close(self):
        self.ser.close()


if __name__ == '__main__':
    print 'hahaha'
    logging.debug('common')
    kkm = Driver(settings.KKM['PORT'],
                 settings.KKM['BAUDRATE'])
    time.sleep(1)

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
    items = [
        dict(qty=2, price=3, text='alal'),
        dict(qty=2, price=3, text='afff')
    ]

    kkm.open_check()
    kkm.print_check(2000, items)
    # for item in items:
    #     kkm.sale(
    #         item['qty'],
    #         item['price'],
    #         item['text'][:40],
    #         taxes=[2, 0, 0, 0]
    #     )

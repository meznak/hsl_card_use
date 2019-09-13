#!/bin/env python3
import argparse
import csv
from time import strptime
import string


def main(cardholder_file: string, door_log_file: string):
    (cardholders, door_logs) = read_files(cardholder_file, door_log_file)
    door_log = calculate_card_numbers(door_logs)
    cardholders, door_log = associate_names(cardholders, door_log)
    cardholders = calculate_stats(cardholders, door_log)
    write_files(cardholders, door_log, cardholder_file, door_log_file)


def calculate_stats(cardholders: list, door_log: list):
    card_events = [door_log[i][1] for i in range(len(door_log))]

    for i in range(len(cardholders)):
        cardholders[i].append(card_events.count(cardholders[i][1].lower()))

    for i in range(len(cardholders)):
        for j in range(len(door_log)):
            if door_log[j][1] == cardholders[i][1].lower():
                cardholders[i].append(door_log[j][0])
                break
        if len(cardholders[i]) < 4:
            cardholders[i].append('')

    return cardholders


def calculate_card_numbers(door_logs: list):
    log = []
    for index in range(len(door_logs) - 1):
        cur_row = door_logs[index]
        next_row = door_logs[index + 1]
        if cur_row[1] == 'G':
            remainder = cur_row[2]
            if next_row[1] == 'g':
                quotient = next_row[2]

                card_number = hex(int(quotient) * 32767 + int(remainder))
                log.append([next_row[3], card_number[2:]])
            else:
                pass
    return log


def associate_names(cardholders: list, door_logs: list):
    cards = {}
    door_log = []
    for log in door_logs:
        for card in cardholders:
            if card[1].lower() == log[1]:
                log.append(card[6])
                door_log.append(log)

                if strptime(log[0][:19], "%Y-%m-%d %H:%M:%S") > \
                        strptime(card[7][:19], "%Y-%m-%d %H:%M:%S"):
                    card[7] = log[0]
                    cards[card[1].lower()] = card

                break

    return [v for v in cards.values()], door_log


def read_files(cardholder_file: string, door_log_file: string):
    cardholders = []
    # name	card_number	exit_reason
    with open(cardholder_file) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            row.append('1970-01-01 00:00:00.000000')  # last seen
            cardholders.append(row)

    door_logs = []
    # id	key	data	created_at	updated_at	card_number
    with open(door_log_file) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
            door_logs.append(row)

    return cardholders[1:], door_logs[1:]


def write_files(cardholders: list, door_log: list, cardholder_file: string, door_log_file: string):
    with open(cardholder_file[:-4] + '-out.csv', 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['name', 'card_number', 'open_count', 'last_open_utc'])
        for row in cardholders:
            out_row = [row[6], row[1], row[5], row[7]]
            csv_writer.writerow(out_row)

    with open(door_log_file[:-4] + '-out.csv', 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['time_utc', 'card_number', 'name'])
        for row in door_log:
            csv_writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='cardholder_file', help="CSV including name, card_number")
    parser.add_argument(dest='door_log_file', help="CSV including key, data (g,G), created_at")
    args = parser.parse_args()
    print(args)
    main(args.cardholder_file, args.door_log_file)

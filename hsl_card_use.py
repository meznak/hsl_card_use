#!/bin/env python3
import argparse
import csv
import string


def main(cardholder_file: string, door_log_file: string):
    (cardholders, door_logs) = read_files(cardholder_file, door_log_file)
    door_log = calculate_card_numbers(door_logs)
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
        if cur_row[1] == 'g':
            quotient = cur_row[2]
            if next_row[1] == 'G':
                remainder = next_row[2]

                card_number = hex(int(quotient) * 32767 + int(remainder))
                log.append([next_row[3], card_number[2:]])
            else:
                raise ValueError
    return log


def read_files(cardholder_file: string, door_log_file: string):
    cardholders = []
    # name	card_number	exit_reason
    with open(cardholder_file) as f:
        csv_reader = csv.reader(f, delimiter=',')
        for row in csv_reader:
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
        csv_writer.writerow(['name', 'card_number', 'exit_reason', 'open_count', 'last_open_utc'])
        for row in cardholders:
            csv_writer.writerow(row)

    with open(door_log_file[:-4] + '-out.csv', 'w') as f:
        csv_writer = csv.writer(f, delimiter=',')
        csv_writer.writerow(['time', 'card_number'])
        for row in door_log:
            csv_writer.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='cardholder_file', help="CSV including name, card_number")
    parser.add_argument(dest='door_log_file', help="CSV including key, data (g,G), created_at")
    args = parser.parse_args()
    print(args)
    main(args.cardholder_file, args.door_log_file)

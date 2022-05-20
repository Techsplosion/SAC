cards = [('0', 0), ('1', 0), ('2', 0), ('3', 0), ('4', 0), ('5', 0), ('6', 0), ('7', 0), ('8', 0), ('9', 0), ('+2', 0), ('reverse', 0), ('block', 0),
         ('0', 1), ('1', 1), ('2', 1), ('3', 1), ('4', 1), ('5', 1), ('6', 1), ('7', 1), ('8', 1), ('9', 1), ('+2', 1), ('reverse', 1), ('block', 1),
         ('0', 2), ('1', 2), ('2', 2), ('3', 2), ('4', 2), ('5', 2), ('6', 2), ('7', 2), ('8', 2), ('9', 2), ('+2', 2), ('reverse', 2), ('block', 2),
         ('0', 3), ('1', 3), ('2', 3), ('3', 3), ('4', 3), ('5', 3), ('6', 3), ('7', 3), ('8', 3), ('9', 3), ('+2', 3), ('reverse', 3), ('block', 3),
         ('switch cards', 4), ('+4', 4), ('change color', 4)]

special = ['+2', '+4', 'reverse', 'block', 'switch cards']

def uno_decode(card):
    if card[1] == 0:
        return f'red {card[0]}'

    elif card[1] == 1:
        return f'blue {card[0]}'

    elif card[1] == 2:
        return f'green {card[0]}'

    elif card[1] == 3:
        return f'yellow {card[0]}'

    elif card[1] == 4:
        return card[0]

def uno_encode(decoded_card):
    decoded_card = decoded_card.lower()
    decoded_card = decoded_card.split()
    if isinstance(decoded_card, str):
        decoded_card = [decoded_card]

    match decoded_card:
        case ['red', card_name]:
            return (card_name, 0)

        case ['blue', card_name]:
            return (card_name, 1)

        case ['green', card_name]:
            return (card_name, 2)

        case ['yellow', card_name]:
            return (card_name, 3)

        case [*wild_card_name]:
            final_card_name = ''
            for i, v in enumerate(wild_card_name):
                if i == len(wild_card_name) - 1:
                    final_card_name += v

                else:
                    final_card_name += v + ' '
            return (final_card_name, 4)


def win(player_cards):
    for i in player_cards:
        if player_cards[i] == []:
            return True
    return False

def determine_winner(player_cards):
    for i in player_cards:
        if player_cards[i] == []:
            return i

def can_play(card_to_throw, card_to_compare):
    if card_to_compare[0] == '+2' or card_to_compare[0] == '+4':
        if card_to_throw[0] == card_to_compare[0]:
            return True
    if card_to_throw[0] == card_to_compare[0] or card_to_throw[1] == card_to_compare[1] or card_to_throw[1] == 4:
        return True
    return False


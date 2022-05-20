# 0 = red 1 = blue 2 = green 3 = yellow
import random
from uno_structures import *
from misc import *
players = 4

player_cards = {}

forwards = True

desk_cards = []
start_card = random.choice(cards)
while start_card[0] in special:
    start_card = random.choice(cards)
desk_cards.append(start_card)


for i in range(players):
    player_cards[f'p{i + 1}'] = random.choices(cards, k=7)


uno_players = [i for i in range(players) if len(player_cards[f'p{i + 1}']) == 1]

turn = 0
to_take = 0
while not win(player_cards):
    top_card = desk_cards[-1]
    throwable_cards = filter_list(lambda x: can_play(x, top_card), player_cards[f'p{turn % 4 + 1}'])
    print(f'Turn {turn + 1}')
    print(f'UNO Players:')
    for i, v in enumerate(uno_players):
        print(f'{i + 1}. Player {v}')
    print(f'Top card: {uno_decode(top_card)}')
    print(f'Player {(turn % 4) + 1}')
    print(f'Your cards:')
    for i, v in enumerate(player_cards[f'p{(turn % 4) + 1}']):
        print(f'\t{i + 1}. {uno_decode(v)}')
    print('Throwable cards:')
    for i, v in enumerate(player_cards[f'p{(turn % 4) + 1}']):
        if can_play(v, top_card):
            print(f'\t{uno_decode(v)}')
    print('\n')
    chosen_card = uno_encode(input('Choose card: '))
    while chosen_card not in throwable_cards:
        chosen_card = uno_encode(input('Sorry, you can\'t throw that card. Choose another card: '))

    if not throwable_cards and not not player_cards[f'p{(turn % 4) + 1}']:
        print('You can\'t throw any card. You have to draw a card.')
        player_cards[f'p{(turn % 4) + 1}'].append(random.choice(cards))
        print(f'You drew {uno_decode(player_cards[f"p{(turn % 4) + 1}"][-1])}')
        desk_cards.append(player_cards[f'p{(turn % 4) + 1}'][-1])
        player_cards[f'p{(turn % 4) + 1}'].remove(player_cards[f'p{(turn % 4) + 1}'][-1])
        print(f'You have played drawn card {uno_decode(top_card)}')
        print('\n')
        continue

    player_cards[f'p{(turn % 4) + 1}'].remove(chosen_card)

    turn += 1

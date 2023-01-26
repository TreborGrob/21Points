import random


def display_point(nick, current, score, robot):
    if not robot:
        return f'{nick} попалась карта {current}, у вас {score} очков.'
    else:
        return f'Дилеру попалась карта {current}, у дилера {score} очков.'


def card_random() -> str:
    # масти
    suits = "❤♦♣♠"
    # ранги
    ranks = ('6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
    # генерируем колоду
    all_cards = [r + s for r in ranks for s in suits]
    random.shuffle(all_cards)
    card = all_cards.pop()
    return card


def issuance_of_card(score: int, card: str) -> int:
    if card.startswith('6'):
        score += 6
    elif card.startswith('7'):
        score += 7
    elif card.startswith('8'):
        score += 8
    elif card.startswith('9'):
        score += 9
    elif card.startswith('10'):
        score += 10
    elif card.startswith('J'):
        score += 2
    elif card.startswith('Q'):
        score += 3
    elif card.startswith('K'):
        score += 4
    elif card.startswith('A'):
        if score <= 10:
            score += 11
        else:
            score += 1
    else:
        score += 10
    return score


def evaluate_points(score_bot: int, score_player: int, stats: bool):
    if score_bot == score_player == 21:
        return 'Ничья!\n'
    elif score_bot > 21 and score_player > 21:
        return 'Lose'
    elif score_bot > 21 > score_player:
        return 'Win'
    elif score_bot < 21 < score_player:
        return 'Lose'
    elif score_bot < 21 > score_player:
        return 'Game'
    elif score_bot == score_player:
        if stats:
            pass
        else:
            return 'Ничья!\n'


def text_points(dealer: int, player: int) -> str:
    pass


if __name__ == "__main__":
    print(card_random())

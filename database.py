import logging
from sqlalchemy import create_engine, MetaData, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from models import Games, Rating, Players

logger = logging.getLogger(__name__)
Base = declarative_base()
engine = create_engine("sqlite:///points.db")
meta = MetaData()
session = Session(bind=engine)


def add_in_game(tg_id_one: int, tg_id_two: int, status: bool, result: str, score_one: int, score_two: int):
    session.add(Games(id_tg_player_one=tg_id_one,
                      id_tg_player_two=tg_id_two,
                      status=status, result=result,
                      score_one=score_one,
                      score_two=score_two))
    session.commit()


def delete_in_game(tg_id_one: int, tg_id_two: int):
    session.delete(session.query(Games).filter(and_(Games.id_tg_player_one == tg_id_one,
                                                    Games.id_tg_player_two == tg_id_two)))
    session.commit()


def select_rating(tg_id: int):
    return session.query(Rating.games_rating, Rating.wins_rating, Rating.loses_rating, Rating.draws_rating,
                         Rating.rate).filter(Rating.id_telegram == tg_id).all()


def update_score_rating(tg_id: int, flag='win'):
    data = select_rating(tg_id)
    games = int(data[0][0]) + 1
    wins = int(data[0][1]) + 1
    loses = int(data[0][2]) + 1
    draws = int(data[0][3]) + 1
    if flag == 'draw':
        session.query(Rating).filter(Rating.id_telegram == tg_id).update({"games_rating": games,
                                                                          "draws_rating": draws},
                                                                         synchronize_session='fetch')
    elif flag == 'lose':
        session.query(Rating).filter(Rating.id_telegram == tg_id).update({"games_rating": games,
                                                                          "loses_rating": loses},
                                                                         synchronize_session='fetch')
    else:
        session.query(Rating).filter(Rating.id_telegram == tg_id).update({"games_rating": games,
                                                                          "wins_rating": wins},
                                                                         synchronize_session='fetch')
    session.commit()


def wait_gamers():
    return session.query(Rating.id_telegram).filter(Rating.desire == 1).all()


def select_player(tg_id: int) -> tuple | None:
    try:
        data = session.query(Players.games, Players.wins, Players.loses, Players.draws) \
            .filter(Players.id_telegram == tg_id).all()[0]
        games = data[0]
        wins = data[1]
        loses = data[2]
        draws = data[3]
        return games, wins, loses, draws
    except Exception as e:
        print(e)
        return None


def insert_to_db(id_tg: int, nickname: str, games=0, wins=0, loses=0, draws=0):
    session.add(Players(id_telegram=id_tg,
                        nickname=nickname,
                        games=games,
                        wins=wins,
                        loses=loses,
                        draws=draws))
    session.commit()


def update_score(tg_id: int, games: int, wins: int, loses: int, draws: int, flag='win'):
    if flag == 'draw':
        session.query(Players).filter(Players.id_telegram == tg_id).update({"games": games,
                                                                            "draws": draws},
                                                                           synchronize_session='fetch')
    elif flag == 'lose':
        session.query(Players).filter(Players.id_telegram == tg_id).update({"games": games,
                                                                            "loses": loses},
                                                                           synchronize_session='fetch')
    else:
        session.query(Players).filter(Players.id_telegram == tg_id).update({"games": games,
                                                                            "wins": wins}, synchronize_session='fetch')
    session.commit()


def insert_to_rating(id_tg: int, nickname: str, games=0, wins=0, loses=0, draws=0):
    session.add(Rating(id_telegram=id_tg,
                       nickname=nickname,
                       games=games,
                       wins=wins,
                       loses=loses,
                       draws=draws))
    session.commit()


def update_desire(tg_id: int, flag: bool):
    session.query(Rating).filter(Rating.id_telegram == tg_id).update({"desire": flag}, synchronize_session='fetch')
    session.commit()


def update_games_1plr(score: int, flag: bool, id_game: int):
    session.query(Games).filter(Games.id_game == id_game).update({"score_one": score,
                                                                  "move_one": flag}, synchronize_session='fetch')
    session.commit()


def update_games_2plr(score: int, flag: bool, id_game: int):
    session.query(Games).filter(Games.id_game == id_game).update({"score_two": score,
                                                                  "move_two": flag}, synchronize_session='fetch')
    session.commit()


def slct_game(tg_id: int):
    import sqlite3
    con = sqlite3.connect("points.db")
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM games WHERE id_tg_player_one = {tg_id} OR id_tg_player_two = {tg_id}")
    result = cursor.fetchall()
    return result


def del_game(id_game: int):
    i = session.query(Games).filter(Games.id_game == id_game).one()
    session.delete(i)
    session.commit()


if __name__ == '__main__':
    pass

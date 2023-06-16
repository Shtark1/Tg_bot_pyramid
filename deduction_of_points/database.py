import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def update_user_balances(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM users")
            rows = self.cursor.fetchall()

            for row in rows:
                id_c, user_id, username, referer_id, ban, balance, day_reg, what_day = row
                if what_day == 365:
                    self.cursor.execute("UPDATE users SET what_day = ? WHERE user_id = ?", (1, user_id))
                else:
                    if balance is None or balance <= 0:
                        print("Отрицательный баланс")
                        continue

                    new_balance = balance - (what_day * 100)
                    new_what_day = what_day + 1

                    self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                    if referer_id is not None:
                        self.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (referer_id,))
                        referer_balance = self.cursor.fetchone()[0]
                        referer_balance += what_day * 90
                        self.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (referer_balance, referer_id))

                    self.cursor.execute("UPDATE users SET what_day = ? WHERE user_id = ?", (new_what_day, user_id))

            self.connection.commit()
            print("Обновление балансов завершено")

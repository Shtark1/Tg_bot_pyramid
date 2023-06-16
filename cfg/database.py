import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, username, referer_id=None, ban="False", balance=0):
        with self.connection:
            if referer_id is not None:
                return self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `referer_id`, `ban`, `balance`) VALUES (?, ?, ?, ?, ?)", (user_id, username, referer_id, ban, balance,))
            else:
                return self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `ban`, `balance`) VALUES (?, ?, ?, ?)", (user_id, username, ban, balance,))

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def count_referer(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT COUNT(`id`) as count FROM `users` WHERE `referer_id` = ?", (user_id,)).fetchone()[0]

    def add_balance(self, user_id, up):
        with self.connection:
            al = self.cursor.execute("SELECT `balance` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
            a = up + al

            self.cursor.execute("UPDATE `users` SET `balance` = ? WHERE `user_id` = ?", (a, user_id,))
            self.connection.commit()

    def get_balance(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT `balance`, `what_day`, `day_reg` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()

    def register_day(self, user_id, day_reg, what_day):
        with self.connection:
            self.cursor.execute("UPDATE `users` SET `day_reg` = ?, `what_day` = ? WHERE `user_id` = ?", (day_reg, what_day, user_id,))
            self.connection.commit()

    def out_money(self, user_id, money):
        with self.connection:
            al = self.cursor.execute("SELECT `balance` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
            a = int(al) - int(money)

            self.cursor.execute("UPDATE `users` SET `balance` = ? WHERE `user_id` = ?", (a, user_id,))
            self.connection.commit()

    def get_all_data(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users`").fetchall()

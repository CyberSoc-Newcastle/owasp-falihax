on line 441, change:

credit_score = int(
        cursor.execute("select credit_score from users where username = \"" + username + "\"").fetchone()[0])
        

to


score = cursor.execute("select credit_score from users where username = \"" + username + "\"").fetchone()[0]
credit_score = int(score if score else 0)

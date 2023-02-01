from extensions import db, app

class MovieStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    movieId = db.Column(db.String)
    rating = db.Column(db.Integer)
    minutesWatched = db.Column(db.Integer)
    def __init__(self, userId, movieId, rating, minutesWatched):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.minutesWatched = minutesWatched
    def __repr__(self):
        return '<User %r>' % str(self.id) + " " + str(self.userId) + " " + str(self.movieId)

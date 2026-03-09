from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    User model - stores player profile and gamification stats.
    TODO: Add OAuth integration (Google/GitHub) for easier sign-up.
    TODO: Add avatar/profile picture support.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # TODO: Hash with bcrypt in production
    xp = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=100)  # Starting coins for new users
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship('Progress', backref='user', lazy=True, uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'xp': self.xp,
            'coins': self.coins,
            'level': self.level,
            'streak_days': self.streak_days
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Progress(db.Model):
    """
    Progress model - tracks user learning journey and financial health score.
    TODO: Add per-topic completion tracking.
    TODO: Add timestamps for each scenario completion for analytics.
    """
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scenarios_completed = db.Column(db.Integer, default=0)
    financial_score = db.Column(db.Float, default=50.0)  # Scale 0-100
    budgeting_level = db.Column(db.Integer, default=0)    # 0=locked, 1=unlocked, 2=complete
    saving_level = db.Column(db.Integer, default=0)
    debt_level = db.Column(db.Integer, default=0)
    investing_level = db.Column(db.Integer, default=0)
    independence_level = db.Column(db.Integer, default=0)
    badges_earned = db.Column(db.String(500), default='')  # Comma-separated badge IDs
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'scenarios_completed': self.scenarios_completed,
            'financial_score': self.financial_score,
            'budgeting_level': self.budgeting_level,
            'saving_level': self.saving_level,
            'debt_level': self.debt_level,
            'investing_level': self.investing_level,
            'independence_level': self.independence_level,
            'badges_earned': self.badges_earned.split(',') if self.badges_earned else []
        }

    def __repr__(self):
        return f'<Progress user_id={self.user_id} score={self.financial_score}>'

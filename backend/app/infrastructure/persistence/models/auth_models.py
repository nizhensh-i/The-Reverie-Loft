from ....infrastructure.database.sqlalchemy import db
from ....utils.time_util import DateUtils


class ThirdPartyAccount(db.Model):
    __tablename__ = "third_party_accounts"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(32), nullable=False)
    uuid = db.Column(db.String(128), nullable=False)

    username = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(128))
    mobile = db.Column(db.String(32))
    gender = db.Column(db.SmallInteger, nullable=True)
    location = db.Column(db.String(64))
    company = db.Column(db.String(128))
    blog = db.Column(db.String(255))
    remark = db.Column(db.String(255))

    raw_user_info = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=DateUtils.now_time)
    updated_at = db.Column(
        db.DateTime,
        default=DateUtils.now_time,
        onupdate=DateUtils.now_time,
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("provider", "uuid", name="uq_provider_uuid"),
        db.Index("idx_provider_uuid", "provider", "uuid"),
    )

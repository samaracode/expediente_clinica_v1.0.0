import sqlalchemy as sa
from app.db.base_class import Base


class File(Base):
    __tablename__ = "files"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    s3_key = sa.Column(sa.String, nullable=False)
    s3_bucket = sa.Column(sa.String, nullable=False)
    file_name = sa.Column(sa.String, nullable=False)
    mime_type = sa.Column(sa.String, nullable=True)
    entity_type = sa.Column(sa.String, nullable=True)
    entity_id = sa.Column(sa.Integer, nullable=True)
    uploaded_by_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), nullable=True)
    uploaded_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())


def get_user(db, model, user):
    return db.session.query(model).filter(model.id == user)

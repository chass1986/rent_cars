from rent_cars import app, db


if __name__ == '__main__':
    db.create_all()  # create sql tables
    app.run(debug=True, host='0.0.0.0')

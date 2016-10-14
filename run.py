from blog import app
from blog.models.entry import Entry

def main():
    app.database.create_tables([Entry], safe=True)
    app.app.run(debug=True)

if __name__ == '__main__':
    main()
from blog import app
from blog.views import views

from blog.models.entry import Entry

def main():
    app.database.create_all()
    app.app.run(debug=True)

if __name__ == '__main__':
    main()
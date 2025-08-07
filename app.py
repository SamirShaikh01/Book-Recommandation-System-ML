from flask import Flask, render_template, request
import pickle
import numpy as np
from rapidfuzz import process

# Loading models
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
pt.index = pt.index.str.lower()  # ✅ normalize index

books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))


app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           ratings=list(popular_df['avg_ratings'].values),
                           )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/Docs')
def about():
    return render_template('docs.html')


@app.route('/all_books')
def all_books():
    page = int(request.args.get('page', 1))  # default page = 1
    books_per_page = 24

    all_books_data = books[['Book-Title', 'Book-Author', 'Image-URL-M']].drop_duplicates('Book-Title')
    total_books = len(all_books_data)
    total_pages = (total_books + books_per_page - 1) // books_per_page

    start = (page - 1) * books_per_page
    end = start + books_per_page
    page_books = all_books_data.iloc[start:end]

    return render_template('all_books.html',
                           titles=list(page_books['Book-Title'].values),
                           authors=list(page_books['Book-Author'].values),
                           images=list(page_books['Image-URL-M'].values),
                           current_page=page,
                           total_pages=total_pages)




@app.route('/recommend_books', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        user_input = request.form.get('user_input').lower()  # ✅ normalize input

         # Check if user_input is in the model
        if user_input not in pt.index:
            return render_template('recommend.html', data=None, error="Sorry, the book was not found. Please try another title.")

        try:
            index = np.where(pt.index == user_input)[0][0]
            distances = similarity_scores[index]
            similar_items = sorted(
                list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:7]

            data = []
            for i in similar_items:
                item = []
                book_title = pt.index[i[0]]  # lowercase
                temp_df = books[books['Book-Title'].str.lower() == book_title]

                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
                data.append(item)


            return render_template('recommend.html', data=data)

        except Exception as e:
            print(f"Error: {e}")
            return render_template('recommend.html', data=None, error="An error occurred. Please try again.")

    # For GET request (initial page load or refresh), no error or data
    return render_template('recommend.html')

if __name__ == '__main__':
    app.run(debug=True)

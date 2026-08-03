from models.book import Book

def test_book_borrow():

    book = Book(
        1001,
        "三体",
        ["刘慈欣"],
        "科幻"
    )

    assert book.borrow() is False

    assert book.available == 0 and book.total == 0

    book.add_quantity(1)

    assert book.borrow() is True

    assert book.available == 0

    assert book.borrow() is False

    assert book.available == 0 and book.total == 1


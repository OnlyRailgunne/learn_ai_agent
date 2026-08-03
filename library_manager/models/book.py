# book.py
class Book:

    def __init__(self, book_id, name, authors, category):

        self.book_id = book_id

        self.name = name

        self.authors = authors

        self.category = category

        self.total = 0

        self.available = 0

    def print_info(self):

        print(f"ID: {self.book_id}")

        print(f"Name: {self.name}")

        print(f"Authors: {', '.join(self.authors)}")

        print(f"Category: {self.category}")

        print(f"Total Copies: {self.total}")

        print(f"Available Copies: {self.available}")

    def add_quantity(self, quantity):
        if quantity < 0:
            return False
        self.total += quantity

        self.available += quantity
        return True

    def borrow(self):
        if self.available > 0:
            self.available -= 1
            return True
        return False

    def return_book(self):
        if self.available < self.total:
            self.available += 1
            return True
        return False

    def can_remove(self):
        return self.available == self.total

    def can_borrow(self):
        return self.available > 0

    def get_info(self):
        return{
            "book_id": self.book_id,
            "name": self.name,
            "authors": self.authors,
            "category": self.category,
            "total": self.total,
            "available": self.available
        }

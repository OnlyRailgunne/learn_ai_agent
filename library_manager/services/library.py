# library.py 
class Library: 
    def __init__(self): 
        self.books = {} 
        self.users = {} 
        self.borrow_records = [] 

    def add_book(self, book, quantity):
         if book.book_id in self.books: 
            self.books[book.book_id].add_quantity(quantity)
            return True 
         else: 
            self.books[book.book_id] = book
            book.add_quantity(quantity) 
            return True 

    def show_books(self): 
        for book in self.books.values(): 
            book.print_info() 
        return True  

    def find_book(self, book_id):
        return self.books.get(book_id)

    def remove_book(self,book_id):
        if book_id in self.books: 
            if self.books[book_id].can_remove():
                del self.books[book_id] 
                return True 
            return False 
        return False 
    
    def borrow(self, user_id, book_id): 
        if book_id not in self.books: 
            return False 
        book = self.books[book_id] 
        if not book.can_borrow(): 
            return False 
        if user_id not in self.users: 
            return False 
        user = self.users[user_id] 
        if not user.can_borrow(): 
            return False 
        book.borrow()
        # TODO
        # 以后改成数据库自增ID
        record = BorrowRecord(len(self.borrow_records) + 1, user_id, book_id, None, get_time(), get_due_date(), None)
        user.borrow(record)
        self.borrow_records.append(record) 
        
        return True

    def return_book(self, user_id, book_id):
        user = self.users.get(user_id)
        book = self.books.get(book_id) 
        if user is None:
            return False
        if book is None:
            return False
        if not user.return_book(book_id):
            return False
        book.return_book()
        return True
# borrow_record.py 
class BorrowRecord:

    def __init__(
        self,
        record_id,
        user_id,
        book_id,
        book_copy_id,
        borrow_date,
        due_date,
        return_date
    ):

        self.record_id = record_id

        self.user_id = user_id

        self.book_id = book_id

        self.book_copy_id = book_copy_id

        self.borrow_date = borrow_date

        self.due_date = due_date

        self.return_date = return_date

    def update_return_date(self):
        self.return_date = datetime.now()
        return self.return_date
    
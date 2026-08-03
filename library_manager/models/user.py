# user.py
ROLE_COMMON = "common_user"
ROLE_ADMIN = "admin"
ROLE_VIP = "vip_user"
ROLE_VALUE = {
    "admin": 99999,
    "common_user": 5,
    "vip_user": 20
}
class User:
    def __init__(self):
        self.user_id =  None
        self.password = ""
        self.name = ""
        self.borrow_records = []
        self.role = ROLE_COMMON
        self.role_value = ROLE_VALUE

    def get_using_records(self):
        using_records = []
        for record in self.borrow_records:
            if record.return_date is None:
                using_records.append(record)
        return using_records

    def can_borrow(self):
        return len(self.get_using_records()) < ROLE_VALUE[self.role]

    def can_return(self, book_id):
        for record in self.borrow_records:
            if record.book_id == book_id and record.return_date is None:
                return True
        return False


    def update_borrow_record(self, book_id):
        for record in self.borrow_records:
            if record.book_id == book_id and record.return_date is None:
                record.update_return_date()
                return True
        return False
        
    def borrow(self, record):
        self.borrow_records.append(record)
        return True

    def return_book(self, book_id):
        if not self.can_return(book_id):
            return False
        if not self.update_borrow_record(book_id):
            return False
        return True
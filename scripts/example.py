class example(NebriOS):
    listens_to = ['example']

    def check(self):
        return self.example == True

    def action(self):
        self.example = "Ran"
        send_email ("koryd@bixly.com","""
            My email message...
            """)

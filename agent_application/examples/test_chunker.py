from chunker import Chunker


text = """
Remote Work Policy

Employees can work remotely up to three days per week.

Remote work must be requested in advance through the company system.

Employees are responsible for maintaining a stable internet connection when working remotely.

Employees should be available during normal working hours from 9:00 to 18:00.
"""


chunker = Chunker()

chunks = chunker.chunk(text)


print("=== Chunks ===")

for index, chunk in enumerate(chunks):

    print()
    print(f"Chunk {index}:")
    print(chunk)
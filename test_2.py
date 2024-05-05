import pickle  # Example using JSON for serialization (consider pickle for more complex objects)
from multiprocessing import shared_memory
import os
# TODO, Today:
#  highlight trigger for when sensor is active

class SharedData:
    def __init__(self, name, size):
        self.mem = shared_memory.SharedMemory(name, create=True, size=size)
        self.mem_size = size  # Store size for data validation

    def store_data(self, data):
        # Serialize data to JSON bytes
        serialized_data = pickle.dumps(data)

        # Validate data size to prevent buffer overflow
        if len(serialized_data) > self.mem_size:
            raise ValueError("Data exceeds shared memory size")

        # Copy serialized data to shared memory buffer
        memoryview(self.mem.buf)[:len(serialized_data)] = memoryview(serialized_data)

    def retrieve_data(self):
        # Read data from shared memory buffer
        serialized_data = self.mem.buf

        # Deserialize data from JSON (replace with appropriate deserialization based on your data)
        return pickle.loads(serialized_data)

_importing_file = None
def set_importing_file(file_name):
    global _importing_file
    print('here')
    _importing_file = os.path.basename(file_name)


'''# Example usage
shared_data = SharedData("my_shared_data", 1024)  # Adjust size based on your data

data_to_store = {"key1": [[1, None, 3], [4, 5, 6]], "key2": [1, 2, 3]}
shared_data.store_data(data_to_store)

retrieved_data = shared_data.retrieve_data()
print(retrieved_data)
'''
print(f'importing: {_importing_file}')
if not _importing_file:
    print(f'name: {__name__}')
    print(f'File: {__file__}')
    print(F"Importing: {_importing_file}")

from multiprocessing import shared_memory, Semaphore
import pickle, os

# TODO: Fix array allocation size

sem = Semaphore()


# creating two dicts:
#   - vector_field: a 2D array with each element being [x, y]
#   - sensor_field: a 2d array with each element being either true or false


def SemaphoreWrapper(func):
    global sem

    def wrapper(*args, **kwargs):
        sem.acquire()
        print("Gained access")
        res = func(*args, **kwargs)
        sem.release()
        print("relinquished access")
        return res

    return wrapper


class SharedData:
    row: int = 5
    col: int = 5
    mem_size: int = 1024 * 1024

    #   dict names
    vector_field = 'vector_field'
    sensor_field = 'sensor_field'
    simulation_information = 'simulation_information'
    shrm_name = 'shared_cell_data'

    def __init__(self, name, val=None, create=False, mem_offset=0):
        if create:
            self.mem = shared_memory.SharedMemory(name, create=True, size=self.mem_size)
        else:
            self.mem = shared_memory.SharedMemory(name, create=False, size=self.mem_size)
        self.mem_offset = mem_offset

    def getIndex(self, x, y, row=None, col=None):
        if row is None:
            row = self.row
            col = self.col
        if 0 <= x < col and 0 <= y < row:
            i = y * col + x
            return i
        else:
            return None

    def getRowCol(self, i, row=None, col=None):
        if row is None:
            row = self.row
            col = self.col
        if 0 <= i < row * col:
            y = i // col
            x = i % col
            return x, y
        else:
            return None, None

    @SemaphoreWrapper
    def store_data(self, data):
        # Serialize data to JSON bytes
        serialized_data = pickle.dumps(data)

        # Validate data size to prevent buffer overflow
        if len(serialized_data) > self.mem_size:
            raise ValueError("Data exceeds shared memory size")

        # Copy serialized data to shared memory buffer
        memoryview(self.mem.buf)[:len(serialized_data)] = memoryview(serialized_data)

    @SemaphoreWrapper
    def retrieve_data(self):
        # Read data from shared memory buffer
        serialized_data = self.mem.buf

        # Deserialize data from JSON (replace with appropriate deserialization based on your data)
        try:
            t = pickle.loads(serialized_data)
        except:
            t = None
        return t

    def unlink(self):
        self.mem.unlink()


def create_shared_data():
    print(f"Creating shared data named: {SharedData.shrm_name}")
    # t = SharedData(SharedData.shrm_name, None, create=True)
    # t.unlink()

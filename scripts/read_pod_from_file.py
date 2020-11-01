import pickle


def read_pod_from_file(filename: str):
    """
    从文件中反序列化pods
    如果在不同的主机上使用该函数，应当保证kubernetes库的版本接近，否则会报错
    """
    with open(filename, 'rb') as f:
        return pickle.load(f)

# coding=utf-8
import threading
class Singleton(object):
    _instance_lock = threading.Lock()
    def __init__(self):
        pass
    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = object.__new__(cls)
        return Singleton._instance
    def gets(self):
        return ":"



if __name__ == '__main__':
    obj1 = Singleton()
    obj2 = Singleton()
    print(obj1, obj2)
    print obj1.gets()
# def task(arg):
#     obj = Singleton.instance()
#     print(obj)
# for i in range(10):
#     t = threading.Thread(target=task,args=[i,])
#     t.start()
# time.sleep(20)
# obj = Singleton.instance()
# print(obj)

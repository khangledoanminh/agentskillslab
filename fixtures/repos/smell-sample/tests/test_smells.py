from src.god import GodClass
from src.longf import long_func
from src.dup_a import duplicated
def test_god(): assert GodClass().method_0() == 0
def test_long(): assert long_func(5) is not None
def test_dup(): assert duplicated() == 1/3

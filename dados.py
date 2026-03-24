import pathlib

from rdata import Rdata

fpath = pathlib.Path().resolve()._str

data_name = rf"{fpath}\data\L1FO5_gwo_10_40_1_res7.json"

dataset = Rdata()

key = "fo3"
dataset.analise(data_name, key=key)
dataset.show(data_name, order=key)
# dataset.evolution(data_name,30,key=key)
# dataset.convergence(data_name,30,key=key)

import pathlib

from rdata import Rdata

fpath = pathlib.Path().resolve()._str
dataset = Rdata()


data_name = rf"{fpath}\data\L1FO6_gwo_3_60_1_res3.json"
key = "fo6"


dataset.analise(data_name, key=key)

dataset.show(data_name, order=key)
# dataset.evolution(data_name, 40, key=key)
# dataset.convergence(data_name, 40, key=key)

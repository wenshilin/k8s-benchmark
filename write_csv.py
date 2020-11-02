from benchmark.jct_tables import *


base_dir = 'results/jobs/'
dirs = [os.path.join(base_dir, d) for d in [
    '2020-11-02 13-10-47-云到边-ep',
    '2020-11-02 12-55-51-云到边-bra',
    '2020-11-02 12-41-07-云到边-aladdin',
    '2020-11-02 12-26-54-云到边-mrp',
    '2020-11-02 12-12-25-云到边-lrp',
    '2020-11-02 11-41-03-云到边-lrp'
]]

data = read_data_from_directories(dirs)
save_csv(data)

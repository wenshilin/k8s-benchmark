import json

filename = "E:\\2K20\\k8s-benchmark\\templates\\alibaba-trace-jobs.json"
with open(filename, "r") as fp:
    data = json.load(fp)
    print(len(data))
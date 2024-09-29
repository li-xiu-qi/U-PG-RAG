import magic

res = magic.from_file("nepu.md", mime=True)
print(res)

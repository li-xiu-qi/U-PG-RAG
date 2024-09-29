from diskcache import Cache

if __name__ == "__main__":
    cache = Cache("./cache")
    cache.set("key", "value")
    print(cache.get("key"))

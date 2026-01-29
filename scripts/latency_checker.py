import time
import requests
import threading

URL_1 = "https://api.genesysmap.com/api/v1/live-traffic/india-part1of3?api_key=970c4ce718df4501bf329058c6a78ead"
URL_2 = "http://localhost:8000/traffic/india/part1"


def check_latency(url, results, key):
    start = time.perf_counter()
    response = requests.get(url)
    end = time.perf_counter()

    results[key] = {
        "status_code": response.status_code,
        "latency_ms": (end - start) * 1000
    }


if __name__ == "__main__":
    results = {}

    t1 = threading.Thread(target=check_latency, args=(URL_1, results, "url1"))
    t2 = threading.Thread(target=check_latency, args=(URL_2, results, "url2"))

    start_all = time.perf_counter()

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    end_all = time.perf_counter()

    print(f"\nURL 1 : {URL_1}")
    print(f"Status: {results['url1']['status_code']}")
    print(f"Latency: {results['url1']['latency_ms']:.2f} ms")

    print(f"\nURL 2 : {URL_2}")
    print(f"Status: {results['url2']['status_code']}")
    print(f"Latency: {results['url2']['latency_ms']:.2f} ms")

    print(f"\nTotal wall time: {(end_all - start_all) * 1000:.2f} ms")

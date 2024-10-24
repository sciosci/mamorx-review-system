from ratelimit import limits, sleep_and_retry

# @sleep_and_retry
@limits(calls=40, period=1)
def fn(n):
    print(f"Ok-{n}")

def main():
    for i in range(120):
        fn(i)

if __name__ == "__main__":
    main()
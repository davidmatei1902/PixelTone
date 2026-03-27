import sys

def main():
    print("Hello World!")
    x = []
    n = 50  
    for i in range(n + 1):
        if i % 2 == 0:
            x.append(i)
    
    print(x)
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication Stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Exception catched: {e}")
        sys.exit(1)